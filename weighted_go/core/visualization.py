"""
Visualization utilities for Weighted Go.

Displays boards with territory using Unicode symbols.
Symbol definitions are in weighted_go.commons.resources.
"""

from typing import Set, Tuple
from .core import GamePosition, Stone, find_territory, Position
from ..commons.resources import (
    SYMBOL_BLACK_STONE,
    SYMBOL_WHITE_STONE,
    SYMBOL_BLACK_TERRITORY,
    SYMBOL_WHITE_TERRITORY,
    SYMBOL_CONTESTED,
    SYMBOL_EMPTY,
    get_symbol_legend,
)


def print_board_with_territory(pos: GamePosition, show_coordinates: bool = True):
    """
    Print the board showing stones and territory.

    See weighted_go.commons.resources for symbol definitions.

    Args:
        pos: GamePosition to display
        show_coordinates: Whether to show row/column coordinates
    """
    print(get_board_string(pos, show_coordinates))


def get_board_string(pos: GamePosition, show_coordinates: bool = True) -> str:
    """
    Get a string representation of the board with territory markers.

    See weighted_go.commons.resources for symbol definitions.

    Args:
        pos: GamePosition to display
        show_coordinates: Whether to show row/column coordinates

    Returns:
        String representation of the board
    """
    board = pos.board
    rows, cols = board.rows, board.cols

    # Determine territory ownership for all empty positions
    territory_map = {}
    assigned: Set[Position] = set()

    for i in range(rows):
        for j in range(cols):
            p = (i, j)
            if board.get(p) == Stone.EMPTY and p not in assigned:
                territory, owner = find_territory(board, p)
                for tp in territory:
                    assigned.add(tp)
                    territory_map[tp] = owner

    # Build the output string
    lines = []

    # Column headers (if requested)
    if show_coordinates:
        if cols <= 25:
            # Use letters for columns, skipping 'I' per Go convention
            col_labels = []
            for i in range(cols):
                label = chr(ord('A') + i)
                if label >= 'I':
                    label = chr(ord(label) + 1)  # Skip 'I'
                col_labels.append(label)
            header = "    " + " ".join(col_labels)
            lines.append(header)
        else:
            # Use numbers for many columns
            header = "    " + " ".join(f"{i:2}" for i in range(cols))
            lines.append(header)

    # Board rows
    for i in range(rows):
        row_parts = []

        # Row number (if requested) - 1-indexed for human readability
        if show_coordinates:
            row_parts.append(f"{i+1:2} ")

        # Row contents
        for j in range(cols):
            p = (i, j)
            stone = board.get(p)

            if stone == Stone.BLACK:
                symbol = SYMBOL_BLACK_STONE
            elif stone == Stone.WHITE:
                symbol = SYMBOL_WHITE_STONE
            else:
                # Empty - check territory
                owner = territory_map.get(p, Stone.EMPTY)
                if owner == Stone.BLACK:
                    symbol = SYMBOL_BLACK_TERRITORY
                elif owner == Stone.WHITE:
                    symbol = SYMBOL_WHITE_TERRITORY
                else:
                    symbol = SYMBOL_CONTESTED

            row_parts.append(symbol)

        lines.append(" ".join(row_parts))

    return "\n".join(lines)


def print_board_simple(pos: GamePosition, show_coordinates: bool = False):
    """
    Print the board with just stones (no territory).

    Args:
        pos: GamePosition to display
        show_coordinates: Whether to show row/column coordinates
    """
    board = pos.board
    rows, cols = board.rows, board.cols

    lines = []

    # Column headers (if requested)
    if show_coordinates:
        if cols <= 25:
            # Use letters for columns, skipping 'I' per Go convention
            col_labels = []
            for i in range(cols):
                label = chr(ord('A') + i)
                if label >= 'I':
                    label = chr(ord(label) + 1)  # Skip 'I'
                col_labels.append(label)
            header = "   " + " ".join(col_labels)
            lines.append(header)

    # Board rows
    for i in range(rows):
        row_parts = []

        if show_coordinates:
            row_parts.append(f"{i+1:2} ")

        for j in range(cols):
            stone = board.get((i, j))
            if stone == Stone.BLACK:
                symbol = SYMBOL_BLACK_STONE
            elif stone == Stone.WHITE:
                symbol = SYMBOL_WHITE_STONE
            else:
                symbol = SYMBOL_EMPTY

            row_parts.append(symbol)

        lines.append(" ".join(row_parts))

    print("\n".join(lines))


def print_score_summary(pos: GamePosition, weight_func, weight_name: str = ""):
    """
    Print a summary of the game including board and score.

    Args:
        pos: GamePosition to analyze
        weight_func: Weight function or matrix to use for scoring
        weight_name: Name of the weighting scheme (for display)
    """
    from .core import score

    print(f"{'='*60}")
    if weight_name:
        print(f"Weighting: {weight_name}")
    print(f"{'='*60}")
    print()

    print_board_with_territory(pos, show_coordinates=True)
    print()

    # Calculate score
    black_score, white_score = score(pos, weight_func)

    print(f"Score (Area Scoring):")
    print(f"  Black ({SYMBOL_BLACK_STONE}/{SYMBOL_BLACK_TERRITORY}): {black_score:.1f}")
    print(f"  White ({SYMBOL_WHITE_STONE}/{SYMBOL_WHITE_TERRITORY}): {white_score:.1f}")
    print(f"  Result: {'Black' if black_score > white_score else 'White'}+{abs(black_score - white_score):.1f}")

    # Show stone counts
    b_stones, w_stones = pos.board.count_stones()
    print(f"\nStone count: Black={b_stones}, White={w_stones}")
    print(f"{'='*60}")
