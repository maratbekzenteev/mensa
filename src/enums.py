from enum import Enum


# Enums needed for different widgets to function properly
# All serve the purpose of making the code more legible
# (As opposed to ordinal values for different states,
# which need to be memorised)


# In a Grid, the width of each column and the height of each row
# is specified either absolutely (i.e. in cells)
# or relatively (in percents of the so-called whole width/height (read grid.py))
class Unit(Enum):
    CELLS = 0
    PERCENTS = 1


# When a cursor movement occurs, it is recursively forwarded from the
# parent widget to the child (usually the active one).
# Then the child needs to tell how it has handled the cursor movement:
# - either it was handled INSIDE the child widget (the parent doesn't need to do anything)
# - or the cursor was MOVED out of the child widget and this needs to be handled by the parent
class CursorMoveResult(Enum):
    INSIDE = 0
    MOVED_LEFT = 1
    MOVED_RIGHT = 2
    MOVED_UP = 3
    MOVED_DOWN = 4


# Events are needed to propagate important state
# changes of child widgets to their parents
class Event:
    NONE = 0
    VALUE_CHANGED = 1
