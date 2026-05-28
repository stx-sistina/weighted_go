"""
Core logic for Weighted Go.

This module contains the fundamental game logic, SGF parsing, and visualization.
"""

from .board import (
    Stone,
    Board,
    BoardSize,
    Position,
)

from .game import (
    Group,
    find_group,
    has_liberties,
    count_liberties,
    remove_group,
    GamePosition,
    score,
    find_territory,
    is_valid_position,
)

from .sgf_reader import (
    read_sgf,
    read_sgf_file,
    sgf_to_coords,
    parse_sgf_properties,
    extract_main_path_moves,
    InvalidPositionError,
    SGFError,
)

from .visualization import (
    print_board_with_territory,
    get_board_string,
    print_board_simple,
    print_score_summary,
)

from .weight import (
    Weight,
    MatrixWeight,
    FunctionWeight,
)

__all__ = [
    # Board
    "Stone",
    "Board",
    "BoardSize",
    "Position",
    # Core classes
    "Group",
    "GamePosition",
    # Core functions
    "find_group",
    "has_liberties",
    "count_liberties",
    "remove_group",
    "score",
    "find_territory",
    "is_valid_position",
    # SGF reader
    "read_sgf",
    "read_sgf_file",
    "sgf_to_coords",
    "parse_sgf_properties",
    "extract_main_path_moves",
    "InvalidPositionError",
    "SGFError",
    # Visualization
    "print_board_with_territory",
    "get_board_string",
    "print_board_simple",
    "print_score_summary",
    # Weight system
    "Weight",
    "MatrixWeight",
    "FunctionWeight",
]
