from bs4 import BeautifulSoup
import requests
import datetime


# This file contains all functions that fetch the data from the STW Aachen website
# and converts data such as dates and canteen names between their "raw" and "formatted" formats


RAW_TO_FORMATTED_MENSA = {
    "academica":        "Academica",
    "ahornstrasse":     "Ahornstraße",
    "templergraben":    "Bistro Templergraben",
    "bayernallee":      "Bayernallee",
    "kmac":             "KMAC",
    "eupenerstrasse":   "Eupener Straße",
    "suedpark":         "Südpark",
    "vita":             "Vita",
    "juelich":          "Jülich"
}

FORMATTED_TO_RAW_MENSA = {
    "Academica":            "academica",
    "Ahornstraße":          "ahornstrasse",
    "Bistro Templergraben": "templergraben",
    "Bayernallee":          "bayernallee",
    "KMAC":                 "kmac",
    "Eupener Straße":       "eupenerstrasse",
    "Südpark":              "suedpark",
    "Vita":                 "vita",
    "Jülich":               "juelich"
}


# See above
def formatted_mensa(raw_name: str) -> str:
    return RAW_TO_FORMATTED_MENSA[raw_name]


# See above
def raw_mensa(formatted_name: str) -> str:
    return FORMATTED_TO_RAW_MENSA[formatted_name]


# Output format: "DD.MM.YYYY"
def formatted_date(day: int, month: int, year: int) -> str:
    day_string = ('0' if day < 10 else '') + str(day)
    month_string = ('0' if month < 10 else '') + str(month)
    year_string = str(year)

    return '.'.join([day_string, month_string, year_string])


# Output format: (day, month, year)
def raw_date(s: str) -> (int, int, int):
    try:
        return tuple(int(i) for i in s.split('.'))
    except ValueError:
        today = datetime.date.today()
        return today.day, today.month, today.year


# Output format: [(day, month, year)]
def get_available_days(mensa="academica") -> list[tuple[int, int, int]]:
    request = requests.get(f"https://www.studierendenwerk-aachen.de/speiseplaene/{mensa}-w.html")
    request.encoding = "utf-8"
    request = request.text
    soup = BeautifulSoup(request, 'html.parser')
    soup = soup.body.find(class_="accordion")
    return [raw_date(elem.h3.a.text.split(', ')[1]) for elem in soup.contents]


# Returns the menu for the given canteen and date
# in the format [(dish category, dish name, price in cents]
def get_menu(mensa="academica", day=0, month=0, year=0) -> list[str, str, int]:
    if day == 0 or month == 0 or year == 0:
        today = datetime.date.today()
        day = today.day
        month = today.month
        year = today.year

    request = requests.get(f"https://www.studierendenwerk-aachen.de/speiseplaene/{mensa}-w.html")
    request.encoding = "utf-8"
    request = request.text
    soup = BeautifulSoup(request, 'html.parser')
    soup = soup.body.find(class_="accordion")
    dayMenu = [elem for elem
               in soup.contents
               if elem.h3.a.text.split(', ')[1] == formatted_date(day, month, year)]

    if len(dayMenu) == 0:
        return []

    dayMenu = dayMenu[0].div
    side_dishes = [i for i in
                   dayMenu.find(class_="extras").find(string="Hauptbeilagen").parent.parent.contents[1].contents
                   if i.name is None]
    side_dishes += [i for i in
                    dayMenu.find(class_="extras").find(string="Nebenbeilage").parent.parent.contents[1].contents
                    if i.name is None]

    dayMenu = dayMenu.find(class_="menues").tbody.contents

    dishes = []
    for item in dayMenu:
        category = item.find(class_="menue-item menue-category").text

        dish = ' '.join([i.text.strip() for i
                         in item.find(class_="menue-item menue-desc").span.contents
                         if i.name is None])

        try:
            price = item.find(class_="menue-item menue-price large-price").text
            price = int(''.join([char for char in price if char.isnumeric()]))
        except AttributeError:
            price = 0

        dishes.append([category, dish, price])

    for side_dish in side_dishes: dishes.append(['Beilage', side_dish, 0])
    return dishes


# Used for testing, is run only when run as a standalone file
if __name__ == "__main__":
    print(get_menu("academica", 9, 12, 2024))
    print(get_available_days())
