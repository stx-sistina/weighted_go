"""
Demonstration of ANSI color capabilities for terminal display.

This shows how colors can be used in terminal output for enhanced visualization.
"""

from weighted_go.commons import (
    SYMBOL_BLACK_STONE,
    SYMBOL_WHITE_STONE,
    SYMBOL_BLACK_TERRITORY,
    SYMBOL_WHITE_TERRITORY,
    SYMBOL_CONTESTED,
    is_terminal,
    colorize,
    colored_stone,
    ANSI_BOLD,
    ANSI_FG_RED,
    ANSI_FG_GREEN,
    ANSI_FG_BLUE,
    ANSI_FG_YELLOW,
    ANSI_BG_YELLOW,
    COLOR_BLACK_STONE,
    COLOR_WHITE_STONE,
    COLOR_BLACK_TERRITORY,
    COLOR_WHITE_TERRITORY,
    COLOR_CONTESTED,
    COLOR_WINNER,
    rgb_fg,
    rgb_bg,
)


def main():
    print("=" * 70)
    print("ANSI Color Demonstration for Weighted Go".center(70))
    print("=" * 70)
    print()

    # Show terminal detection status
    print(f"Terminal detected: {is_terminal()}")
    if not is_terminal():
        print("⚠️  Colors are DISABLED (output is redirected to file/pipe)")
        print("   Run directly in terminal to see colors, or use force=True")
    else:
        print("✓  Colors are ENABLED (output is to terminal)")
    print()

    # Basic colors
    print("1. Basic Text Colors:")
    print(f"   {colorize('Red text', ANSI_FG_RED)}")
    print(f"   {colorize('Green text', ANSI_FG_GREEN)}")
    print(f"   {colorize('Blue text', ANSI_FG_BLUE)}")
    print(f"   {colorize('Yellow text', ANSI_FG_YELLOW)}")
    print(f"   {colorize('Bold text', ANSI_BOLD)}")
    print()

    # Stone colors
    print("2. Colored Go Stones:")
    print(f"   Black stone: {colored_stone(SYMBOL_BLACK_STONE, is_black=True)}")
    print(f"   White stone: {colored_stone(SYMBOL_WHITE_STONE, is_black=False)}")
    print()

    # Territory colors
    print("3. Colored Territory:")
    print(f"   Black territory: {colorize(SYMBOL_BLACK_TERRITORY, COLOR_BLACK_TERRITORY)}")
    print(f"   White territory: {colorize(SYMBOL_WHITE_TERRITORY, COLOR_WHITE_TERRITORY)}")
    print(f"   Contested: {colorize(SYMBOL_CONTESTED, COLOR_CONTESTED)}")
    print()

    # Board-like display
    print("4. Sample Board Row with Colors:")
    stones = [
        (SYMBOL_BLACK_STONE, True),
        (SYMBOL_WHITE_STONE, False),
        (SYMBOL_BLACK_TERRITORY, "black_territory"),
        (SYMBOL_WHITE_TERRITORY, "white_territory"),
        (SYMBOL_CONTESTED, "contested"),
    ]

    row = "   "
    for symbol, color_type in stones:
        if color_type is True:  # Black stone
            row += colored_stone(symbol, is_black=True) + " "
        elif color_type is False:  # White stone
            row += colored_stone(symbol, is_black=False) + " "
        elif color_type == "black_territory":
            row += colorize(symbol, COLOR_BLACK_TERRITORY) + " "
        elif color_type == "white_territory":
            row += colorize(symbol, COLOR_WHITE_TERRITORY) + " "
        elif color_type == "contested":
            row += colorize(symbol, COLOR_CONTESTED) + " "

    print(row)
    print()

    # RGB colors (24-bit true color - requires modern terminal)
    print("5. RGB True Colors (requires modern terminal):")
    print(f"   {colorize('Orange text', rgb_fg(255, 165, 0))}")
    print(f"   {colorize('Purple background', rgb_bg(128, 0, 128))}")
    print(f"   {colorize('Cyan on dark blue', rgb_fg(0, 255, 255), rgb_bg(0, 0, 100))}")
    print()

    # Winner highlight
    print("6. Game Result Display:")
    print(f"   {colorize('Black Wins!', COLOR_WINNER)}")
    print(f"   {colorize('White Wins!', COLOR_WINNER)}")
    print()

    # Background colors (board simulation)
    print("7. Board Background Simulation:")
    print(f"   {colorize(' Traditional board color ', ANSI_BG_YELLOW, ANSI_FG_RED)}")
    print()

    print("=" * 70)
    print("Notes:")
    print("  • Colors auto-disable when output is redirected to file")
    print("  • Use force=True parameter to always include ANSI codes")
    print("  • Colors may vary depending on your terminal theme")
    print("  • Some terminals may not support all features (especially RGB)")
    print()
    print("Examples:")
    print("  Direct:     python examples/color_demo.py")
    print("  To file:    python examples/color_demo.py > output.txt  (colors disabled)")
    print("  Force:      colorize('text', COLOR, force=True)  (always colored)")
    print("=" * 70)


if __name__ == "__main__":
    main()
