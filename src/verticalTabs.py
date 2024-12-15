from abstractTabs import AbstractTabs
from enums import Event, CursorMoveResult, Unit
from tab import Tab


# VerticalTabs is a subclass of AbstractTabs that implements
# the navigation element of vertically aligned tabs
# Unlike its superclass, it can be instantiated
class VerticalTabs(AbstractTabs):
    # Handles movements of the cursor
    # All horizontal movements are propagated to the parent widget
    # Vertical movements either change the opened and active tab
    # or are propagated to the parent widget (in boundary cases)
    def move_cursor(self, key_name: str) -> CursorMoveResult:
        active_x, active_y = self.active_cell
        if key_name == "KEY_LEFT":
            return CursorMoveResult.MOVED_LEFT

        if key_name == "KEY_RIGHT":
            return CursorMoveResult.MOVED_RIGHT

        if key_name == "KEY_UP":
            if active_y == 0:
                return CursorMoveResult.MOVED_UP
            active_y -= 1
        if key_name == "KEY_DOWN":
            if active_y == len(self.rows) - 1:
                return CursorMoveResult.MOVED_DOWN
            active_y += 1

        self.set_active_cell((active_x, active_y))
        self.set_opened_cell((active_x, active_y))
        self.set_event(Event.VALUE_CHANGED)
        return CursorMoveResult.INSIDE

    # Sets up the tabs, their names and the grid layout needed to fit them
    def set_tabs(self, tabs: list[str]):
        self.set_grid([(2, Unit.CELLS)] * len(tabs), [(100, Unit.PERCENTS)])
        for row in range(len(tabs)):
            self.set_cell(0, row, Tab(0, 0, tabs[row]))
        self.set_opened_cell((0, 0))
