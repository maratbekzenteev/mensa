from widget import Widget
from enums import Unit, Event
from enums import CursorMoveResult
from blessed import Terminal


# Grid is a class primarily needed for arranging other widgets in a grid.
# Each child widget has a cell corresponding to it
# (One child widget cannot span across multiple cells)
# The layout of the grid is determined by the number of rows and columns
# and their heights and widths, respectively.
# They can be given either absolutely (in cells),
# or relatively (in percents of the so-called whole size
# that consists of the whole width and whole height)
# E.g. the whole width is self.width - abs_columns_sum,
# where abs_columns_sum is the sum of widths of columns with widths specified in cells
# Such a system is needed for proper rescaling of the grid
# Attributes:
# - self.rows - [(size: int, unit: Unit)], the list of row heights specified as discussed above
# - self.columns - [(size: int, unit: Unit)], the list of column width specified as above
# - self.pref_heights - [int], the i-th element states the sum of row heights on the i-th prefix
# - - (that is, of all rows before and including the i-th) in cells
# - self.pref_widths - [int], same as for self.pref_heights, but for columns and widths
# - self.widget_grid - [[Widget]], the array of child widgets
# - - The widget with the coordinate (x, y) is at self.widget_grid[y][x]
# - - Better use getters self.get_cell or self.get_by_label to access your widgets directly
# - self.labels - dict<str, (int, int)>, used for getting the child widget's coords by its label
# - self.active_cell - (int, int), coordinates of the selected grid cell
# - self.x_offset - int, used for scrolling the grid,
# - - mainly when its contents are bigger than its actual size
# - self.y_offset - int, see the explnataion above
# Parameters:
# - Grid doesn't have any parameters that are specific to it
# - For inherited parameters see widget.py
class Grid(Widget):
    # Initialises the grid, sets it to a 1-element grid 100% by 100%
    def __init__(self, width: int, height: int):
        super().__init__(width, height)
        self.rows = []  # [(size, unit), ..., (size, unit)]
        self.columns = []  # [(size, unit), ..., (size, unit)]
        self.pref_heights = []
        self.pref_widths = []
        self.widget_grid = []  # Size: len(rows) by len(columns), every element is a widget
        self.labels = dict()
        self.set_grid([(100, Unit.PERCENTS)], [(100, Unit.PERCENTS)])
        self.active_cell = (0, 0)
        self.set_cell(0, 0, Widget(0, 0))
        self.x_offset = 0
        self.y_offset = 0

    # Returns the absolute size (that is, in cells) of a row or a column,
    # according to its given size and the whole size
    @staticmethod
    def get_abs_size(size: int, unit: Unit, whole_size) -> int:
        return size if unit == Unit.CELLS else whole_size * size // 100

    # Returns the widget at coordinates (x, y)
    # The preferred way of directly accessing widgets in the grid cells
    # Returns a dummy widget when nonsensical coordinates are given
    def get_cell(self, x: int, y: int) -> Widget:
        if x < 0 or y < 0 or x >= len(self.columns) or y >= len(self.rows):
            return Widget(0, 0)
        return self.widget_grid[y][x]

    # Returns the widget by its label
    # Returns a dummy widget if the label was not defined
    def get_by_label(self, label: str) -> Widget:
        if label not in self.labels:
            return Widget(0, 0)
        return self.get_cell(*self.labels[label])

    # Sets a label for the grid cell (x, y), if the coordinates make sense
    def set_label(self, x: int, y: int, label: str):
        if x < 0 or y < 0 or x >= len(self.columns) or y >= len(self.rows):
            return
        self.labels[label] = (x, y)

    # Sets a new height for a given row index, if it's valid
    def set_row_height(self, index: int, size: int, unit: Unit):
        if index < 0 or index >= len(self.rows):
            return
        self.rows[index] = (size, unit)
        self.update_pref_heights()

    # Sets a new width for a given column index, if it's valid
    def set_column_width(self, index: int, size: int, unit: Unit):
        if index < 0 or index >= len(self.columns):
            return
        self.columns[index] = (size, unit)
        self.update_pref_widths()

    # Sets new parameter values for given parameter keys
    # Depending on the value of propagate, also sets the parameters for its child widgets
    # Note: values of the keys not mentioned in the parameters dict
    #       remain unchanged
    def set_parameters(self, parameters: dict, propagate=True):
        super().set_parameters(parameters)

        if not propagate:
            return

        for row in range(len(self.rows)):
            for column in range(len(self.columns)):
                self.get_cell(column, row).set_parameters(parameters)

    # Sets a value for one given parameter
    # Depending on the value of propagate, also sets the parameter for its child widgets
    def set_parameter(self, key: str, value, propagate=True):
        super().set_parameter(key, value)

        if not propagate:
            return

        for row in range(len(self.rows)):
            for column in range(len(self.columns)):
                self.get_cell(column, row).set_parameter(key, value)

    # Updates the offset and forwards the update to its children
    def update(self):
        super().update()

        self.update_offset()

        for row in range(len(self.rows)):
            for column in range(len(self.columns)):
                self.widget_grid[row][column].update()

    # Returns the whole size (for the definition: see above)
    def get_whole_size(self) -> tuple[int, int]:
        abs_rows_sum = sum([size for size, unit
                            in self.rows
                            if unit == Unit.CELLS])
        whole_height = self.height - abs_rows_sum

        abs_columns_sum = sum([size for size, unit
                               in self.columns
                               if unit == Unit.CELLS])
        whole_width = self.width - abs_columns_sum

        return whole_width, whole_height

    # Is called when the grid itself was (de)activated by its parent widget
    # Additionally resets the selected cell to (0, 0) when being activated
    # When being deactivated, it also deactivates the selected cell
    def set_active(self, new_active: bool):
        super().set_active(new_active)
        if new_active:
            self.set_active_cell((0, 0))
            self.widget_grid[0][0].set_active(True)
            return

        self.get_cell(*self.active_cell).set_active(False)

    # Sets the new "actual"/"displayed" size and recalculates the grid cell sizes accordingly
    def set_size(self, new_width: int, new_height: int):
        super().set_size(new_width, new_height)
        self.active_cell = (0, 0)

        whole_width, whole_height = self.get_whole_size()

        for row in range(len(self.rows)):
            for column in range(len(self.columns)):
                cell_width = self.columns[column]
                cell_height = self.rows[row]

                self.widget_grid[row][column].set_size(
                    self.get_abs_size(cell_width[0], cell_width[1], whole_width),
                    self.get_abs_size(cell_height[0], cell_height[1], whole_height)
                )

    # Puts a given widget into the cell with given coordinates
    # If the coordinates are invalid or if the given thing is no widget, does nothing
    def set_cell(self, x: int, y: int, w: Widget):
        if x < 0 or x >= len(self.columns) or y < 0 or y >= len(self.rows):
            return
        if not isinstance(w, Widget):
            return

        self.widget_grid[y][x] = w

        whole_width, whole_height = self.get_whole_size()

        cell_width = self.columns[x]
        cell_height = self.rows[y]

        self.widget_grid[y][x].set_size(
            self.get_abs_size(cell_width[0], cell_width[1], whole_width),
            self.get_abs_size(cell_height[0], cell_height[1], whole_height)
        )

        self.widget_grid[y][x].set_active(self.active_cell == (x, y) and self.active)

    # Deactivates the old selected cell, activates the new selected cell
    def set_active_cell(self, new: tuple[int, int]):
        if new == self.active_cell:
            return

        self.widget_grid[self.active_cell[1]][self.active_cell[0]].set_active(False)
        self.active_cell = new
        self.widget_grid[self.active_cell[1]][self.active_cell[0]].set_active(True)

    # Moves the cursor and returns if the movement was resolved inside the grid
    # or if the cursor should be moved by the parent widget (see enums.py)
    def move_cursor(self, key_name: str) -> CursorMoveResult:
        active_x, active_y = self.active_cell

        if key_name == "KEY_LEFT":
            if active_x != 0:
                move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
                if move_result == CursorMoveResult.MOVED_LEFT:
                    active_x -= 1
                    self.set_active_cell((active_x, active_y))
                return CursorMoveResult.INSIDE

            move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
            if move_result == CursorMoveResult.MOVED_LEFT:
                return CursorMoveResult.MOVED_LEFT
            return CursorMoveResult.INSIDE

        if key_name == "KEY_RIGHT":
            if active_x != len(self.columns) - 1:
                move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
                if move_result == CursorMoveResult.MOVED_RIGHT:
                    active_x += 1
                    self.set_active_cell((active_x, active_y))
                return CursorMoveResult.INSIDE

            move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
            if move_result == CursorMoveResult.MOVED_RIGHT:
                return CursorMoveResult.MOVED_RIGHT
            return CursorMoveResult.INSIDE

        if key_name == "KEY_UP":
            if active_y != 0:
                move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
                if move_result == CursorMoveResult.MOVED_UP:
                    active_y -= 1
                    self.set_active_cell((active_x, active_y))
                return CursorMoveResult.INSIDE

            move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
            if move_result == CursorMoveResult.MOVED_UP:
                return CursorMoveResult.MOVED_UP
            return CursorMoveResult.INSIDE

        if key_name == "KEY_DOWN":
            if active_y != len(self.rows) - 1:
                move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
                if move_result == CursorMoveResult.MOVED_DOWN:
                    active_y += 1
                    self.set_active_cell((active_x, active_y))
                return CursorMoveResult.INSIDE

            move_result = self.widget_grid[active_y][active_x].move_cursor(key_name)
            if move_result == CursorMoveResult.MOVED_DOWN:
                return CursorMoveResult.MOVED_DOWN
            return CursorMoveResult.INSIDE

        return CursorMoveResult.INSIDE

    # Returns the character that is to be displayed at the coordinates (x, y)
    # (relative to the top-left corner of the grid)
    # Since a grid has no characters on its own, the get_char call gets recurrently propagated
    # to a child widget in one of the cells
    # The offsets are also taken into account
    # If the coordinates given are invalid, the space is returned
    def get_char(self, x: int, y: int, term: Terminal) -> str:
        # out determines the back- and foreground colors of the output cell
        # (used only in case of invalid coordinates, if not, colors of the child widget are used instead)
        out = term.on_color_rgb(*self.parameters[("" if self.active else "in") + "active_background"])
        x += self.x_offset
        y += self.y_offset

        # Handles the case of invalid coordinates
        if (x < 0 or y < 0 or
            y >= self.pref_heights[-1] or x >= self.pref_widths[-1]):
            return out + ' '

        # Determines how many full rows lie above the needed coordinate
        row = 0
        len_rows = len(self.rows)
        while True:
            if row == len_rows or self.pref_heights[row] > y:
                break
            row += 1
        # Calculates how many cells to subtract to get the needed coordinates for the child widget
        pref_height = self.pref_heights[row - 1] if row > 0 else 0

        # Determines how many full columns lie to the left of the needed coordinate
        column = 0
        len_columns = len(self.columns)
        while True:
            if column == len_columns or self.pref_widths[column] > x:
                break
            column += 1
        # Calculates how many cells to subtract to get the needed coordinates for the child widget
        pref_width = self.pref_widths[column - 1] if column > 0 else 0

        return self.widget_grid[row][column].get_char(x - pref_width,
                                                      y - pref_height,
                                                      term)

    # Sets a new layout for the grid
    # All contents of the grid cells are erased, selected coordinates are set to (0, 0)
    def set_grid(self, rows, columns):
        if len(rows) == 0 or len(columns) == 0:
            return

        self.rows = rows
        self.columns = columns
        self.labels = dict()

        whole_width, whole_height = self.get_whole_size()

        self.active_cell = (0, 0)
        self.widget_grid = [[Widget(
            self.get_abs_size(self.columns[column][0],
                              self.columns[column][1],
                              whole_width),
            self.get_abs_size(self.rows[row][0],
                              self.rows[row][1],
                              whole_height)
        ) for column in range(len(columns))] for row in range(len(rows))]

        self.update_pref_heights()
        self.update_pref_widths()

    # Updates prefix heights. Is used after the row layout has been changed
    # (e.g. in self.set_row_height or in self.set_grid)
    # (for the definition of prefix heights: see attributes)
    def update_pref_heights(self):
        whole_height = self.get_whole_size()[1]

        self.pref_heights = []
        current_height = 0
        for size, unit in self.rows:
            current_height += self.get_abs_size(size, unit, whole_height)
            self.pref_heights.append(current_height)

    # Updates prefix widths. Is used after the column layout has been changed
    # (e.g. in self.set_column_width or in self.set_grid)
    # (for the definition of prefix widths: see attributes)
    def update_pref_widths(self):
        whole_width = self.get_whole_size()[0]

        self.pref_widths = []
        current_width = 0
        for size, unit in self.columns:
            current_width += self.get_abs_size(size, unit, whole_width)
            self.pref_widths.append(current_width)

    # Updates self.x_offset and self.y_offset. Used in self.update
    def update_offset(self):
        active_x, active_y = self.active_cell

        # If the offset is too low (the active cell is below the visible part of the grid)
        if self.pref_heights[active_y] > self.y_offset + self.height:
            self.y_offset = self.pref_heights[active_y] - self.height

        # If the offset is too high (the active cell is above the visible part of the grid)
        if (self.pref_heights[active_y - 1] if active_y != 0 else 0) < self.y_offset:
            self.y_offset = (self.pref_heights[active_y - 1] if active_y != 0 else 0)

        # If the offset is too left (the active cell is to the right of the visible part of the grid)
        if self.pref_widths[active_x] > self.x_offset + self.width:
            self.x_offset = self.pref_widths[active_x] - self.width

        # If the offset is too right (the active cell is to the left of the visible part of the grid)
        if (self.pref_widths[active_x - 1] if active_x != 0 else 0) < self.x_offset:
            self.x_offset = (self.pref_widths[active_x - 1] if active_x != 0 else 0)

    # If one of the child widgets has an event, it moves it to self.event
    # and erases it from the child widget
    # Then it returns the event
    def get_event(self) -> Event:
        for row in range(len(self.rows)):
            for column in range(len(self.columns)):
                cell_event = self.get_cell(column, row).get_event()
                self.get_cell(column, row).set_event(Event.NONE)
                if cell_event != Event.NONE:
                    self.event = cell_event

        if self.event != Event.NONE:
            result = self.event
            self.event = Event.NONE
            return result

        return Event.NONE
