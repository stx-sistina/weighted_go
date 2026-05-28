"""
Color manipulation utilities for Weighted Go.

Helper functions for color blending, conversion, and calculation.
"""

from typing import Tuple


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """
    Convert hex color string to RGB tuple.

    Args:
        hex_color: Hex color string (e.g., "#RRGGBB" or "RRGGBB")

    Returns:
        Tuple of (r, g, b) values (0-255)

    Examples:
        >>> hex_to_rgb("#DCB35C")
        (220, 179, 92)
        >>> hex_to_rgb("FFFFFF")
        (255, 255, 255)
    """
    # Remove '#' if present
    hex_color = hex_color.lstrip('#')

    # Parse hex string
    r = int(hex_color[0:2], 16)
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)

    return (r, g, b)


def rgb_to_hex(r: int, g: int, b: int) -> str:
    """
    Convert RGB values to hex color string.

    Args:
        r, g, b: RGB values (0-255)

    Returns:
        Hex color string (e.g., "#RRGGBB")

    Examples:
        >>> rgb_to_hex(220, 179, 92)
        '#DCB35C'
        >>> rgb_to_hex(255, 255, 255)
        '#FFFFFF'
    """
    return f"#{r:02X}{g:02X}{b:02X}"


def blend_colors(foreground: str, background: str, alpha: float) -> str:
    """
    Alpha blend two colors.

    Uses the formula: result = alpha × foreground + (1 - alpha) × background

    Args:
        foreground: Foreground color in hex format (e.g., "#FFFFFF")
        background: Background color in hex format (e.g., "#DCB35C")
        alpha: Alpha value (0.0 = fully background, 1.0 = fully foreground)

    Returns:
        Blended color in hex format

    Examples:
        >>> blend_colors("#000000", "#DCB35C", 0.45)  # 45% black on goban
        '#796233'
        >>> blend_colors("#FFFFFF", "#DCB35C", 0.17)  # 17% white on goban
        '#E1BF77'
    """
    # Parse colors to RGB
    fg_r, fg_g, fg_b = hex_to_rgb(foreground)
    bg_r, bg_g, bg_b = hex_to_rgb(background)

    # Alpha blend
    r = int(alpha * fg_r + (1 - alpha) * bg_r)
    g = int(alpha * fg_g + (1 - alpha) * bg_g)
    b = int(alpha * fg_b + (1 - alpha) * bg_b)

    return rgb_to_hex(r, g, b)


def calculate_dead_stone_colors(alpha: float, goban_color: str = "#DCB35C") -> Tuple[str, str, str, str]:
    """
    Calculate dead stone colors for both black and white stones.

    Args:
        alpha: Alpha value for blending (0.0-1.0)
        goban_color: Background goban color in hex format

    Returns:
        Tuple of (dead_black_color, dead_black_outline, dead_white_color, dead_white_outline)

    Examples:
        >>> calculate_dead_stone_colors(0.45)
        ('#796233', '#897243', '#E1BF77', '#D1BF77')
    """
    # Calculate blended colors
    dead_black = blend_colors("#000000", goban_color, alpha)
    dead_white = blend_colors("#FFFFFF", goban_color, alpha)

    # Calculate outlines (slightly lighter for black, darker for white)
    black_r, black_g, black_b = hex_to_rgb(dead_black)
    dead_black_outline = rgb_to_hex(
        min(255, black_r + 0x10),
        min(255, black_g + 0x10),
        min(255, black_b + 0x10)
    )

    white_r, white_g, white_b = hex_to_rgb(dead_white)
    dead_white_outline = rgb_to_hex(
        max(0, white_r - 0x10),
        white_g,
        white_b
    )

    return (dead_black, dead_black_outline, dead_white, dead_white_outline)


def print_dead_stone_colors(black_alpha: float, white_alpha: float, goban_color: str = "#DCB35C"):
    """
    Print dead stone color calculations for easy copy-paste into gui_colors.py.

    Args:
        black_alpha: Alpha value for black dead stones
        white_alpha: Alpha value for white dead stones
        goban_color: Background goban color in hex format

    Examples:
        >>> print_dead_stone_colors(0.45, 0.17)
        DEAD_BLACK_STONE_COLOR = "#796233"  # 45% black blended with goban
        DEAD_BLACK_STONE_OUTLINE = "#897243"
        DEAD_WHITE_STONE_COLOR = "#E1BF77"  # 17% white blended with goban
        DEAD_WHITE_STONE_OUTLINE = "#D1BF77"
    """
    black_color = blend_colors("#000000", goban_color, black_alpha)
    white_color = blend_colors("#FFFFFF", goban_color, white_alpha)

    # Calculate outlines
    black_r, black_g, black_b = hex_to_rgb(black_color)
    black_outline = rgb_to_hex(
        min(255, black_r + 0x10),
        min(255, black_g + 0x10),
        min(255, black_b + 0x10)
    )

    white_r, white_g, white_b = hex_to_rgb(white_color)
    white_outline = rgb_to_hex(
        max(0, white_r - 0x10),
        white_g,
        white_b
    )

    print(f'DEAD_BLACK_STONE_COLOR = "{black_color}"  # {black_alpha:.0%} black blended with goban')
    print(f'DEAD_BLACK_STONE_OUTLINE = "{black_outline}"')
    print(f'DEAD_WHITE_STONE_COLOR = "{white_color}"  # {white_alpha:.0%} white blended with goban')
    print(f'DEAD_WHITE_STONE_OUTLINE = "{white_outline}"')


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Calculate dead stone colors for Weighted Go GUI.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument(
        "--black_alpha",
        type=float,
        default=0.5,
        help="Alpha value for black dead stones (0.0-1.0)"
    )
    parser.add_argument(
        "--white_alpha",
        type=float,
        default=0.5,
        help="Alpha value for white dead stones (0.0-1.0)"
    )
    parser.add_argument(
        "--goban_color",
        type=str,
        default="#DCB35C",
        help="Goban background color in hex format"
    )

    args = parser.parse_args()

    # Validate alpha values
    if not (0.0 <= args.black_alpha <= 1.0):
        parser.error("black_alpha must be between 0.0 and 1.0")
    if not (0.0 <= args.white_alpha <= 1.0):
        parser.error("white_alpha must be between 0.0 and 1.0")

    # Print calculated colors
    print(f"Dead stone colors with {args.black_alpha:.0%} black and {args.white_alpha:.0%} white:")
    print_dead_stone_colors(args.black_alpha, args.white_alpha, args.goban_color)
