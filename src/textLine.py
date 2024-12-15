from widget import Widget
from blessed import Terminal


# Text line is a class that represents a single-line text label
# If the widget is taller than one cell, the line is vertically centered
# Attributes:
# - self.text - str, the displayed text line
# - self.offset - int, a number from 0 to len(self.text) inclusively,
# - - the offset with which the text line is displayed. Used for scrolling text
# Parameters:
# - active_background - (int, int, int), the background color when the widget is active
# - inactive_background - (int, int, int), the background color when the widget is inactive
# - active_text - (int, int, int), the foreground color when the widget is active
# - inactive_text - (int, int, int), the foreground color when the widget is inactive
# - scrolling - bool, determines if the text should be scrolled if it is longer than self.width
class TextLine(Widget):
    # Initialises the attributes and the parameters
    def __init__(self, width: int, height: int, text=""):
        super().__init__(width, height)
        self.text = text
        self.parameters["active_text"] = (255, 255, 255)
        self.parameters["inactive_text"] = (128, 128, 128)
        self.parameters["active_background"] = (0, 0, 0)
        self.parameters["inactive_background"] = (0, 0, 0)
        self.parameters["scrolling"] = True
        self.offset = 0

    # Setter for self.text
    def set_text(self, text: str):
        self.text = text

    # Getter for self.text
    def get_text(self) -> str:
        return self.text

    # Increments the offset if the text doesn't fit in self.width and should be scrolled
    def update(self):
        if len(self.text) > self.width and self.parameters["scrolling"]:
            self.offset = (self.offset + 1) % (len(self.text) + 1)

    # A safe method for getting a character of self.text by index
    # Returns a space if the index is out of bounds
    def get_text_char(self, index: int) -> str:
        try:
            return (' ' if self.text == "" or index >= len(self.text) or index < 0
                    else self.text[index])
        except KeyError:
            return ' '

    # Returns the character that is to be displayed at the coordinates (x, y)
    # (relative to the top-left corner of the widget)
    # The scrolling is taken into account
    def get_char(self, x: int, y: int, term: Terminal) -> str:
        # out determines the back- and foreground colors of the cell
        out = term.on_color_rgb(*self.parameters[("" if self.active else "in") + "active_background"])
        out += term.color_rgb(*self.parameters[("" if self.active else "in") + "active_text"])

        vertical_center = (self.height - 1) // 2
        if y != vertical_center:
            return out + ' '

        # Scrolling is only activated if the widget is active
        if len(self.text) > self.width and self.active:
            return out + self.get_text_char((x + self.offset) % (len(self.text) + 1))
        # The standard case without scrolling
        return out + self.get_text_char(x)
