from textLine import TextLine
from blessed import Terminal


# Header is a TextLine used for fancier display of headers
# Appearance-wise, it centers the displayed text and draws two gradients from
# the left and right borders of the widget to left and right borders of the text
# (in order to maintain good readability)
# Parameters:
# - accent - (int, int, int) - the gradient color (fully visible at the widget borders)
class Header(TextLine):
    def __init__(self, width: int, height: int, text=""):
        super().__init__(width, height, text)
        self.parameters["accent"] = (0, 0, 255)

    def get_char(self, x: int, y: int, term: Terminal) -> str:
        gradient_width = max(0, (self.width - len(self.text)) // 2)
        vertical_center = (self.height - 1) // 2

        if gradient_width <= x < self.width - gradient_width:
            if self.active:
                out = (term.color_rgb(*self.parameters["active_text"]) +
                       term.on_color_rgb(*self.parameters["active_background"]))
            else:
                out = (term.color_rgb(*self.parameters["inactive_text"]) +
                       term.on_color_rgb(*self.parameters["inactive_background"]))
            out += (self.get_text_char(x - gradient_width)
                    if y == vertical_center
                    else ' ')
            return out

        cell_color = [int((1 - min(x, self.width - x - 1) / gradient_width) * self.parameters["accent"][i])
                      for i in range(3)]
        return term.color_rgb(*cell_color) + '█'
