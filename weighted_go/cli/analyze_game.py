"""
Analyze a game with all three weighting schemes and beautiful visualization.
"""

import sys
from weighted_go import (
    read_sgf_file,
    print_board_with_territory, get_board_string,
    score,
    UniformWeight, CenterSquareWeight, CenterDiamondWeight,
    BoardSize,
)
from weighted_go.commons.resources import get_symbol_legend


def analyze_game(sgf_path: str, show_full_boards: bool = False):
    """
    Analyze a game from an SGF file with all weighting schemes.

    Args:
        sgf_path: Path to SGF file
        show_full_boards: Whether to show full boards for each weighting
    """
    # Read the game
    pos, last_move_color = read_sgf_file(sgf_path)
    rows, cols = pos.board.rows, pos.board.cols

    # Fixed banner width
    banner_width = 68

    def display_width(s: str) -> int:
        """Calculate display width accounting for East Asian characters."""
        import unicodedata
        width = 0
        for char in s:
            ea_width = unicodedata.east_asian_width(char)
            if ea_width in ('F', 'W'):  # Fullwidth or Wide
                width += 2
            else:
                width += 1
        return width

    def format_row(label: str, value: str) -> str:
        """Format a row with fixed width, truncating value if needed."""
        label_prefix = f"  {label}: "
        max_value_width = banner_width - display_width(label_prefix) - 2  # 2 for "║" borders

        # Truncate value if it's too wide
        while display_width(value) > max_value_width and len(value) > 3:
            value = value[:len(value)-4] + "..."

        content = label_prefix + value
        content_width = display_width(content)
        padding = banner_width - content_width
        return f"║{content}{' ' * padding}║"

    print("╔" + "═" * banner_width + "╗")
    print("║" + "Weighted Go Game Analysis".center(banner_width) + "║")
    print("╠" + "═" * banner_width + "╣")

    # Format file path with truncation if needed
    print(format_row("File", sgf_path))

    # Board size
    print(format_row("Board Size", f"{rows}×{cols}"))

    # Count stones
    b_stones, w_stones = pos.board.count_stones()
    print(format_row("Stones", f"Black={b_stones}, White={w_stones}"))

    print("╚" + "═" * banner_width + "╝")
    print()

    # Show the board with territory
    print("Final Position (with territory markers):")
    print(get_symbol_legend())
    print()
    print_board_with_territory(pos, show_coordinates=True)
    print()

    # Calculate scores with all three weighting schemes
    board_size = BoardSize(rows, cols)
    weights_schemes = [
        ("Uniform (Standard)", UniformWeight()),
        ("Center Weights", CenterSquareWeight()),
        ("Aggressive Weights", CenterDiamondWeight()),
    ]

    results = []
    for name, weight in weights_schemes:
        black_score, white_score = score(pos, weight)
        total = weight.total_weight(board_size)
        results.append((name, black_score, white_score, total))

    # Print results table with fixed column widths
    # Column widths: scheme=22, black=11, white=11, result=13, total=8 (total=67 + borders=3 = 70)
    w_scheme, w_black, w_white, w_result, w_total = 20, 11, 11, 13, 8
    total_width = w_scheme + w_black + w_white + w_result + w_total + 2  # +2 for outer borders

    print("┌" + "─" * total_width + "──┐")
    print("│ " + "Scoring Results (Area Scoring)".center(total_width) + " │")
    print("├" + "─" * w_scheme + "┬" + "─" * w_black + "┬" + "─" * w_white + "┬" + "─" * w_result + "┬" + "─" * w_total + "┤")
    print("│ Weighting Scheme   │   Black   │   White   │    Result   │  Total │")
    print("├" + "─" * w_scheme + "┼" + "─" * w_black + "┼" + "─" * w_white + "┼" + "─" * w_result + "┼" + "─" * w_total + "┤")

    for name, black, white, total in results:
        result = f"W+{white - black:.1f}" if white > black else f"B+{black - white:.1f}"
        total_str = f"{total:.0f}" if total else "N/A"
        # Format with exact column widths
        scheme_col = f" {name:<{w_scheme-1}}"
        black_col = f" {black:>{w_black-2}.1f} "
        white_col = f" {white:>{w_white-2}.1f} "
        result_col = f" {result:>{w_result-2}} "
        total_col = f" {total_str:>{w_total-2}} "
        print(f"│{scheme_col}│{black_col}│{white_col}│{result_col}│{total_col}│")

    print("└" + "─" * w_scheme + "┴" + "─" * w_black + "┴" + "─" * w_white + "┴" + "─" * w_result + "┴" + "─" * w_total + "┘")
    print()

    # Verification
    print("Verification (totals should equal total board weight):")
    for name, black, white, total in results:
        check = "✓" if total and abs(black + white - total) < 0.01 else "✗"
        total_str = f"{total:.0f}" if total else "0"
        print(f"  {check} {name}: {black:.1f} + {white:.1f} = {black + white:.1f} (expected {total_str})")
    print()

    # Show detailed boards for each weighting if requested
    if show_full_boards:
        for name, weight in weights_schemes:
            print(f"\n{'=' * 70}")
            print(f"{name} - Detailed View")
            print(f"{'=' * 70}\n")

            black_score, white_score = score(pos, weight)
            print(get_board_string(pos, show_coordinates=True))
            print(f"\nScore: Black={black_score:.1f}, White={white_score:.1f}, Result={'W' if white_score > black_score else 'B'}+{abs(white_score - black_score):.1f}")


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        # Use default game
        sgf_path = "data/[2137HLE]vs[sistina喵]1779897572030032210.sgf"
    else:
        sgf_path = sys.argv[1]

    show_full = "--full" in sys.argv or "-f" in sys.argv

    try:
        analyze_game(sgf_path, show_full_boards=show_full)
    except FileNotFoundError:
        print(f"Error: File not found: {sgf_path}")
        print("\nUsage: python analyze_game.py [sgf_file] [--full]")
        print("  --full: Show detailed boards for each weighting scheme")
        sys.exit(1)
    except Exception as e:
        print(f"Error analyzing game: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
