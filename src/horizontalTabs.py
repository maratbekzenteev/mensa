from abstractTabs import AbstractTabs
from enums import Event, CursorMoveResult, Unit
from tab import Tab


# HorizontalTabs is a subclass of AbstractTabs that implements
# the navigation element of horizontally aligned tabs
# Unlike its superclass, it can be instantiated
class HorizontalTabs(AbstractTabs):
    # Handles movements of the cursor
    # All vertical movements are propagated to the parent widget
    # Horizontal movements either change the opened and active tab
    # or are propagated to the parent widget (in boundary cases)
    def move_cursor(self, key_name: str) -> CursorMoveResult:
        active_x, active_y = self.active_cell
        if key_name == "KEY_UP":
            return CursorMoveResult.MOVED_UP

        if key_name == "KEY_DOWN":
            return CursorMoveResult.MOVED_DOWN

        if key_name == "KEY_LEFT":
            if active_x == 0:
                return CursorMoveResult.MOVED_LEFT
            active_x -= 1
        if key_name == "KEY_RIGHT":
            if active_x == len(self.columns) - 1:
                return CursorMoveResult.MOVED_RIGHT
            active_x += 1

        self.set_active_cell((active_x, active_y))
        self.set_opened_cell((active_x, active_y))
        self.set_event(Event.VALUE_CHANGED)
        return CursorMoveResult.INSIDE

    # Sets up the tabs, their names and the grid layout needed to fit them
    # Every tab is one cell wider than the text it displays
    def set_tabs(self, tabs: list[str]):
        self.set_grid([(100, Unit.PERCENTS)], [(len(tab) + 1, Unit.CELLS) for tab in tabs])
        for column in range(len(tabs)):
            self.set_cell(column, 0, Tab(0, 0, tabs[column]))
        self.set_opened_cell((0, 0))
