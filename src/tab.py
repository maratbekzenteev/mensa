from textLine import TextLine
from blessed import Terminal


# Tab is a TextLine used in navigation elements such as VerticalTabs and HorizontalTabs
# Unlike a TextLine, it distinguishes two properties: opened and active (see abstractTabs.py)
# When a tab is active, the active style is used,
# when not active but opened, the opened style is used,
# when neither, the inactive style is used
# Attributes:
# - self.opened - bool
# Parameters:
# - opened_text - (int, int, int), the foreground color when the tab is opened
# - opened_background - (int, int, int), the background color ...
class Tab(TextLine):
    def __init__(self, width: int, height: int, text=""):
        # Initialises the attributes and the parameters
        super().__init__(width, height, text)
        self.opened = False
        self.parameters["opened_text"] = (0, 0, 0)
        self.parameters["opened_background"] = (255, 255, 255)

    # Returns the character that is to be displayed at the coordinates (x, y)
    def get_char(self, x: int, y: int, term: Terminal) -> str:
        # Determines the fore- and background color of the cell
        if self.active:
            out = term.on_color_rgb(*self.parameters["active_background"])
            out += term.color_rgb(*self.parameters["active_text"])
        elif self.opened:
            out = term.on_color_rgb(*self.parameters["opened_background"])
            out += term.color_rgb(*self.parameters["opened_text"])
        else:
            out = term.on_color_rgb(*self.parameters["inactive_background"])
            out += term.color_rgb(*self.parameters["inactive_text"])

        vertical_center = (self.height - 1) // 2
        if y != vertical_center:
            return out + ' '

        # Scrolling, as in TextLine, is only activated if the widget is active
        if len(self.text) > self.width and self.active:
            return out + self.get_text_char((x + self.offset) % (len(self.text) + 1))
        # The standard case without scrolling
        return out + self.get_text_char(x)

    # Setter for self.opened
    def set_opened(self, new: bool):
        self.opened = new

    # Getter for self.opened
    def get_opened(self) -> bool:
        return self.opened
