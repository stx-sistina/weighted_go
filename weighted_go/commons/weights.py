"""
Standard weight schemes for Weighted Go.

This module contains the concrete weight implementations that ship with the package.
"""

from ..core.board_size import BoardSize
from ..core.weight import Weight, FunctionWeight


class UniformWeight(Weight):
    """
    Uniform weights: all positions have weight 1.

    This corresponds to standard Go scoring.
    """

    def __init__(self):
        super().__init__(
            name="Uniform (Standard)",
            description="All positions have weight 1.0 (standard Go)"
        )

    def get_weight(self, row: int, col: int, board_size: BoardSize) -> float:
        """All positions have weight 1."""
        return 1.0


class CenterSquareWeight(Weight):
    """
    Center weights with square pattern.

    Weight increases towards the center using Manhattan distance from edges.
    Formula: w[i][j] = 1 + min(dist_from_row_edge, dist_from_col_edge)

    The pattern forms concentric squares.
    """

    def __init__(self):
        super().__init__(
            name="Center: Square",
            description="Square pattern favoring center positions"
        )

    def get_weight(self, row: int, col: int, board_size: BoardSize) -> float:
        """Weight based on minimum distance from any edge."""
        dist_from_row_edge = min(row, board_size.rows - 1 - row)
        dist_from_col_edge = min(col, board_size.cols - 1 - col)
        return 1.0 + min(dist_from_row_edge, dist_from_col_edge)


class CenterDiamondWeight(Weight):
    """
    Center weights with diamond pattern.

    Weight increases towards the center using sum of distances from edges.
    Formula: w[i][j] = 1 + dist_from_row_edge + dist_from_col_edge

    The pattern forms concentric diamonds with stronger center bias.
    """

    def __init__(self):
        super().__init__(
            name="Center: Diamond",
            description="Diamond pattern with aggressive center weighting"
        )

    def get_weight(self, row: int, col: int, board_size: BoardSize) -> float:
        """Weight based on sum of distances from edges."""
        dist_from_row_edge = min(row, board_size.rows - 1 - row)
        dist_from_col_edge = min(col, board_size.cols - 1 - col)
        return 1.0 + dist_from_row_edge + dist_from_col_edge


# Registry of standard weights
STANDARD_WEIGHTS = {
    'uniform': UniformWeight(),
    'center_square': CenterSquareWeight(),
    'center_diamond': CenterDiamondWeight(),
}


def get_weight_by_name(name: str) -> Weight:
    """
    Get a standard weight scheme by name.

    Args:
        name: Weight scheme name ('uniform', 'center_square', 'center_diamond')

    Returns:
        Weight instance

    Raises:
        KeyError: If name is not recognized
    """
    if name not in STANDARD_WEIGHTS:
        raise KeyError(f"Unknown weight scheme: {name}. Available: {list(STANDARD_WEIGHTS.keys())}")
    return STANDARD_WEIGHTS[name]


def list_weights() -> list:
    """
    List all available standard weight schemes.

    Returns:
        List of (key, Weight) tuples
    """
    return list(STANDARD_WEIGHTS.items())


