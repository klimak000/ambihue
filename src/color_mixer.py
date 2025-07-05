import logging
from typing import Any, Dict, List

from src.colors import Color

logger = logging.getLogger(__name__)


class ColorMixer:
    """Class to mix colors from a tab into a single color."""

    def __init__(self) -> None:

        # Data structure to hold colors:
        # [4] 0Top  [5]1T  [6]2T  [7]3T  [8]4T  [9]5T  [10]6T  [11]7T   [12] 8Top
        # [3] 3Left                                                     [13] 0Right
        # [2] 2Left                                                     [14] 1Right
        # [1] 1Left                                                     [15] 2Right
        # [0] 0Left                                                     [16] 3Right
        self._colors: List[Color] = []
        self._num_of_left_right_colors = -1  # Number of left/right colors

    def apply_tv_data(self, data: Dict[str, Any]) -> None:
        self._colors = []  # reset colors
        self._num_of_left_right_colors = 0

        for color in data["layer1"]["left"].values():
            self._colors.append(Color(*color.values()))
            self._num_of_left_right_colors += 1

        for color in data["layer1"]["top"].values():
            self._colors.append(Color(*color.values()))

        right_colors = list(data["layer1"]["right"].values())
        for color in right_colors[::-1]:  # invert RIGHT order!
            self._colors.append(Color(*color.values()))

        # print(f"TAB:\n{self._colors}\n")

    def get_average_color(self, positions: List[int]) -> Color:
        """Calculate the average color from the collected colors."""
        assert self._colors, "Colors have not been set yet."
        assert isinstance(positions, list)
        assert all(isinstance(pos, int) for pos in positions)
        assert all(
            0 <= pos < len(self._colors) for pos in positions
        ), "Position indices are out of bounds."

        color = Color(0, 0, 0)
        for pos in positions:
            color.red += self._colors[pos].red
            color.green += self._colors[pos].green
            color.blue += self._colors[pos].blue

        color.red //= len(positions)
        color.green //= len(positions)
        color.blue //= len(positions)
        return color

    def print_colors(self) -> None:
        """Print the colors in a formatted way."""
        assert self._colors, "Colors have not been set yet."

        if logger.getEffectiveLevel() != logging.DEBUG:
            return  # only print if debug is enabled

        top_colors = self._colors[self._num_of_left_right_colors : -self._num_of_left_right_colors]

        # First line with top colors
        logger.debug(" | ".join(color.get_css_color_name_colored() for color in top_colors))

        # Next lines with left and right colors
        for color_height in range(self._num_of_left_right_colors):  # 0, 1, 2, 3
            left_color = self._colors[self._num_of_left_right_colors - color_height - 1]
            right_color = self._colors[-(color_height + 1)]

            logger.debug(
                f"{left_color.get_css_color_name_colored()} | \t\t\t\t\t\t\t\t\t"
                f"{right_color.get_css_color_name_colored()}"
            )
