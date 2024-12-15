from blessed import Terminal
from enums import *


# Widget is the superclass of all elements of the UI
# Every method of this class needs to be implemented by
# the subclasses for the program to function properly
# Attributes:
# - self.width - int, the width of the widget in cells
# - self.height - int, the height of the widget in cells
# - self.active - bool, tells if the widget is selected and can be interacted with
# - self.parameters - dict, determines the appearance and behaviour of the widget
# - self.event - Event, used for event handling (read enums.py)
# Parameters:
# - active_background - (int, int, int), the background color when the widget is active
# - inactive_background - (int, int, int), the background color when the widget is inactive
# - active_text - (int, int, int), the foreground color when the widget is active
# - inactive_text - (int, int, int), the foreground color when the widget is inactive
class Widget:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.active = False
        self.parameters = dict()
        self.parameters["active_background"] = (0, 0, 255)
        self.parameters["inactive_background"] = (0, 0, 0)
        self.parameters["active_text"] = (255, 255, 255)
        self.parameters["inactive_text"] = (128, 128, 128)
        self.event = Event.NONE

    # Sets new width and height of the widget
    # Grids do that to their children for them to fit into cells
    def set_size(self, new_width: int, new_height: int):
        self.width = new_width
        self.height = new_height

    # Sets the self.active flag to a new value
    def set_active(self, new_active: bool):
        self.active = new_active

    # Getter for the widget size
    def get_size(self) -> tuple[int, int]:
        return self.width, self.height

    def get_active(self) -> bool:
        return self.active

    # Sets new parameter values for given parameter keys
    # Note: values of the keys not mentioned in the parameters dict
    #       remain unchanged
    def set_parameters(self, parameters: dict):
        for key in parameters:
            self.parameters[key] = parameters[key]

    # Sets a value for one given parameter
    def set_parameter(self, key: str, value):
        self.parameters[key] = value

    # Update is used by the subclasses for unconditioned actions
    # that need to happen every program cycle,
    # for example, text scrolling
    def update(self):
        pass

    # Tells the parent widget if the cursor movement was handled
    # or needs to be handled by it
    # Widget always tells the parent to MOVE the cursor in the according direction
    def move_cursor(self, key_name: str) -> CursorMoveResult:
        if key_name == "KEY_LEFT":
            return CursorMoveResult.MOVED_LEFT
        if key_name == "KEY_RIGHT":
            return CursorMoveResult.MOVED_RIGHT
        if key_name == "KEY_UP":
            return CursorMoveResult.MOVED_UP
        if key_name == "KEY_DOWN":
            return CursorMoveResult.MOVED_DOWN
        return CursorMoveResult.INSIDE

    # Returns the character that is to be displayed in the cell at the (x, y) coordinate
    # (relative to the top-left corner of the widget)
    # out determines the back- and foreground colors of the cell
    def get_char(self, x: int, y: int, term: Terminal) -> str:
        out = term.on_color_rgb(*self.parameters[("" if self.active else "in") + "active_background"])

        return out + ' '

    # Returns self.event
    # Implementations in the subclasses usually contain handling
    # the events of the child classes (e.g. read grid.py)
    def get_event(self) -> Event:
        return self.event

    # Setter for self.event
    def set_event(self, new: Event):
        self.event = new
