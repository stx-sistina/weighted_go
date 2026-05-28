"""
Weighted Go - A Go variant where board intersections have configurable weights.

This package implements weighted Go with area scoring, where every point on the
board belongs to Black, White, or is shared (contested territory split 50-50).
"""

from .core import (
    Stone,
    Board,
    BoardSize,
    GamePosition,
    Group,
    Position,
    Weight,
    MatrixWeight,
    FunctionWeight,
    find_group,
    has_liberties,
    count_liberties,
    remove_group,
    score,
    find_territory,
    is_valid_position,
    read_sgf,
    read_sgf_file,
    sgf_to_coords,
    parse_sgf_properties,
    extract_main_path_moves,
    InvalidPositionError,
    SGFError,
    print_board_with_territory,
    get_board_string,
    print_board_simple,
    print_score_summary,
)

from .commons.resources import (
    SYMBOL_BLACK_STONE,
    SYMBOL_WHITE_STONE,
    SYMBOL_BLACK_TERRITORY,
    SYMBOL_WHITE_TERRITORY,
    SYMBOL_CONTESTED,
    SYMBOL_EMPTY,
    get_symbol_legend,
)

from .commons.weights import (
    UniformWeight,
    CenterSquareWeight,
    CenterDiamondWeight,
    STANDARD_WEIGHTS,
    get_weight_by_name,
    list_weights,
)

__version__ = "0.1.0"

__all__ = [
    # Core classes
    "Stone",
    "Board",
    "BoardSize",
    "GamePosition",
    "Group",
    "Position",
    # Weight system
    "Weight",
    "MatrixWeight",
    "FunctionWeight",
    "UniformWeight",
    "CenterSquareWeight",
    "CenterDiamondWeight",
    "STANDARD_WEIGHTS",
    "get_weight_by_name",
    "list_weights",
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
    # Symbols
    "SYMBOL_BLACK_STONE",
    "SYMBOL_WHITE_STONE",
    "SYMBOL_BLACK_TERRITORY",
    "SYMBOL_WHITE_TERRITORY",
    "SYMBOL_CONTESTED",
    "SYMBOL_EMPTY",
    "get_symbol_legend",
]
