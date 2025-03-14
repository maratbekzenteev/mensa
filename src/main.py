import sys

from blessed import Terminal
from widget import Widget
from grid import Grid
from menuGrid import MenuGrid
from verticalTabs import VerticalTabs
from horizontalTabs import HorizontalTabs
from textLine import TextLine
from header import Header
from enums import Unit, Event
from stw_parser import (get_menu, formatted_date, raw_date,
                        get_available_days, raw_mensa, FORMATTED_TO_RAW_MENSA)

ARROW_KEYS = {"KEY_LEFT", "KEY_RIGHT", "KEY_UP", "KEY_DOWN"}

# Conventions used:
# - snake_case for variables, functions and methods
# - CamelCase for class names
# - camelCase for file names
# - no more than one class in one file

# Project structure:
# - src - source code of the program
# - scripts - scripts for cmd and Powershell used to quickly launch the program

# UI structure:
# - main_grid - Grid object containing the header, the footer and the body grid
# - - body_grid - Grid Object with the menu grid and tabs for selecting the day and the canteen
# - - - menu_grid - MenuGrid object displaying the dishes served in a given canteen on a given day
# - - - day_tabs - VerticalTabs object for selecting the day for which the menu is shown
# - - - mensa_tabs - HorizontalTabs for selecting the canteen for which the menu is shown


# The main function
# Contains the initialisation of the TUI and the event loop
# with things like keyboard and internal event handling and screen update
def main(term: Terminal) -> int:
    # Sets the terminal mode before initialisation
    with (term.cbreak(), term.hidden_cursor(), term.fullscreen()):
        # Initialises main_grid, fills the cells with needed widgets
        # The header and the footer are initialised in-place
        main_grid = Grid(term.width, term.height)
        main_grid.set_grid([(1, Unit.CELLS), (100, Unit.PERCENTS), (1, Unit.CELLS)],
                           [(100, Unit.PERCENTS)])
        main_grid.set_active(True)
        main_grid.set_cell(0, 0, Header(0, 0, "Speisepläne - STW Aachen"))
        main_grid.set_cell(0, 1, Grid(0, 0))
        main_grid.set_cell(0, 2, Header(0, 0, "Press Q to quit"))

        # Initialises body_grid
        body_grid = main_grid.get_cell(0, 1)
        body_grid.set_grid([(2, Unit.CELLS), (100, Unit.PERCENTS)],
                           [(11, Unit.CELLS), (100, Unit.PERCENTS)])
        body_grid.set_cell(0, 1, VerticalTabs(0, 0))
        body_grid.set_cell(1, 0, HorizontalTabs(0, 0))
        body_grid.set_cell(1, 1, MenuGrid(0, 0))

        if len(get_available_days()) == 0:
            print(term.red + term.on_black + "ERROR: No available days")
            print(term.white + term.on_black + "Press any key to quit")
            key = term.inkey()
            return

        # Fills day_tabs with days for which the menus can be fetched from the STW website
        day_tabs = body_grid.get_cell(0, 1)
        day_tabs.set_tabs([formatted_date(*date) for date in get_available_days()])

        # Fills mensa_tabs with a fixed set of canteens for which the menus can be fetched
        mensa_tabs = body_grid.get_cell(1, 0)
        mensa_tabs.set_tabs(list(FORMATTED_TO_RAW_MENSA))

        # Sets the appearance for body_grid and its child widgets
        body_grid.set_parameters({
            "active_background": (0, 0, 255),
            "inactive_background": (96, 96, 96),
            "opened_background": (255, 255, 255),
            "active_text": (255, 255, 255),
            "inactive_text": (255, 255, 255),
            "opened_text": (0, 0, 0)
        })
        day_tabs.set_parameter("active_background", (96, 96, 96), propagate=False)
        mensa_tabs.set_parameter("active_background", (96, 96, 96), propagate=False)

        # Setting different background colors for odd and even rows makes them more legible
        for row in range(len(day_tabs.rows)):
            day_tabs.get_cell(0, row).set_parameter(
                "inactive_background", (128, 128, 128) if row % 2 == 0 else (96, 96, 96)
            )

        menu_grid = body_grid.get_cell(1, 1)

        # Fetches the menu before the event loop
        menu = get_menu(
            raw_mensa(
                mensa_tabs.get_cell(*mensa_tabs.get_opened_cell()).get_text(),
            ),
            *raw_date(
                day_tabs.get_cell(*day_tabs.get_opened_cell()).get_text()
            )
        )

        if len(menu) == 0:
            print(term.red + term.on_black + "ERROR: Empty menu")
            print(term.white + term.on_black + "Press any key to quit")
            key = term.inkey()
            return

        # Redraws menu_grid with the new data
        init_menu_grid(menu_grid, menu)

        # The main loop
        while True:
            # Handles the keyboard presses
            key = term.inkey(timeout=0.05)
            if key == 'q':
                break
            elif key.name in ARROW_KEYS:
                main_grid.move_cursor(key.name)

            # Updates body_grid (needed for scrolling the menu text, menu_grid and the tabs)
            body_grid.update()

            # VALUE_CHANGED forwarded by body_grid signalises that
            # either a different day or a different canteen was selected
            # (only the tabs utilise event handling)
            if body_grid.get_event() == Event.VALUE_CHANGED:
                # Fetches the data for the new day and/or canteen
                menu = get_menu(
                    raw_mensa(
                        mensa_tabs.get_cell(*mensa_tabs.get_opened_cell()).get_text(),
                    ),
                    *raw_date(
                        day_tabs.get_cell(*day_tabs.get_opened_cell()).get_text()
                    )
                )

                # Redraws menu_grid with the new data
                init_menu_grid(menu_grid, menu)

            # Resizes the UI based on the new size of the window
            if ((term.width, term.height) != main_grid.get_size()):
                main_grid.set_size(term.width, term.height)
            # Renders the screen and prints it in the terminal,
            # beginning from the top-right position ("home")
            print(term.home + screen(main_grid, term), end='')
            # Clears the buffer
            sys.stdout.flush()

    return 0


# Determines what should be displayed in each sell of the terminal screen
# Returns the whole frame
def screen(window: Widget, term: Terminal) -> str:
    out = ''
    for y in range(term.height):
        for x in range(term.width):
            out += window.get_char(x, y, term)
        out += '\n'
    return out[:-1]


# Fills menu_grid with the given data (usually called after a new day or canteen was selected)
def init_menu_grid(menu_grid: MenuGrid, menu: list[str, str, int]):
    # Determines and sets column widths and row heights
    max_category_width = max([len(category) for category, dish, price in menu])
    menu_grid.set_grid(
        [(3, Unit.CELLS)] * len(menu),
        [(max_category_width + 1, Unit.CELLS), (100, Unit.PERCENTS), (6, Unit.CELLS)]
    )

    # Fills the table with the given data
    # Since prices are given in cents, they are first formatted before being displayed
    for row in range(len(menu)):
        category, dish, price = menu[row]
        f_price = (f"{'-' if price == 0 else price // 100}"
                   ","
                   f"{'-' if price == 0 else price // 10 % 10}"
                   f"{'-' if price == 0 else price % 10} €")
        menu_grid.set_cell(0, row, TextLine(0, 0, category))
        menu_grid.set_cell(1, row, TextLine(0, 0, dish))
        menu_grid.set_cell(2, row, TextLine(0, 0, f_price))

    # Appearance parameters are set for menu_grid
    menu_grid.set_parameters({
        "active_background": (0, 0, 255),
        "inactive_background": (255, 255, 255),
        "active_text": (255, 255, 255),
        "inactive_text": (0, 0, 0)
    })
    menu_grid.set_parameter("active_background", (255, 255, 255), propagate=False)

    # Setting different background colors for odd and even rows makes them more legible
    for row in range(len(menu)):
        for column in range(3):
            menu_grid.get_cell(column, row).set_parameter(
                "inactive_background", (255, 255, 255) if row % 2 == 0 else (224, 224, 224)
            )


# Calls the main function with a new terminal window when the program is launched
if __name__ == "__main__":
    exit(main(Terminal()))
