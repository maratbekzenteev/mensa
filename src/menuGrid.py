from grid import Grid
from enums import CursorMoveResult


# MenuGrid is a class used for displaying the menu itself
# Its only differences from the Grid class are in the way cells are activated
# Namely, the whole row on which self.active_cell lies is displayed as active
# It also reacts to cursor movements differently, as if it had only one column
class MenuGrid(Grid):
    # Reacts to cursor movement
    # If it is moved left or right, it always propagates the movement
    # to the parent widget. Otherwise behaves the same way as a normal Grid
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
        return CursorMoveResult.INSIDE

    # Setter for self.active_cell
    # Also sets the whole row of self.active_cell as active
    # Deactivation works analogously
    def set_active_cell(self, new: tuple[int, int]):
        for column in range(len(self.columns)):
            self.get_cell(column, self.active_cell[1]).set_active(False)
        self.active_cell = new
        for column in range(len(self.columns)):
            self.get_cell(column, self.active_cell[1]).set_active(True)

    # (De)activates the whole grid
    # When being activated, sets self.active_cell to (0, 0)
    # When being deactivated, sets the previously active row of self.active_cell as inactive
    def set_active(self, new_active: bool):
        super().set_active(new_active)
        if new_active:
            self.set_active_cell((0, 0))
            return

        for column in range(len(self.columns)):
            self.get_cell(column, self.active_cell[1]).set_active(False)
