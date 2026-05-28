"""
Core logic for Weighted Go.

This module contains the fundamental game logic, SGF parsing, and visualization.
"""

from .core import (
    Stone,
    Board,
    GamePosition,
    Group,
    Position,
    WeightMatrix,
    WeightFunc,
    find_group,
    has_liberties,
    count_liberties,
    remove_group,
    uniform_weights,
    center_weights,
    aggressive_center_weights,
    score,
    score_with_territory,
    find_territory,
    matrix_to_func,
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

__all__ = [
    # Core classes
    "Stone",
    "Board",
    "GamePosition",
    "Group",
    "Position",
    "WeightMatrix",
    "WeightFunc",
    # Core functions
    "find_group",
    "has_liberties",
    "count_liberties",
    "remove_group",
    "uniform_weights",
    "center_weights",
    "aggressive_center_weights",
    "score",
    "score_with_territory",
    "find_territory",
    "matrix_to_func",
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
]
