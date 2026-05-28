"""
Weight system for Weighted Go.

Defines the weight abstraction for assigning numeric weights to board positions.
"""

from typing import Callable, List, Tuple
from abc import ABC, abstractmethod

from .board_size import BoardSize


Position = Tuple[int, int]


class Weight(ABC):
    """
    Abstract base class for weight schemes.

    A weight scheme assigns a numeric weight to each position on the board.
    """

    def __init__(self, name: str, description: str = ""):
        """
        Initialize a weight scheme.

        Args:
            name: Display name
            description: Longer description of the scheme
        """
        self.name = name
        self.description = description

    @abstractmethod
    def get_weight(self, row: int, col: int, board_size: BoardSize) -> float:
        """
        Get the weight for a specific position.

        Args:
            row: Row index (0-based)
            col: Column index (0-based)
            board_size: Board dimensions

        Returns:
            Weight value for this position
        """
        pass

    def as_matrix(self, board_size: BoardSize) -> List[List[float]]:
        """
        Generate weight matrix for a board size.

        Args:
            board_size: Board dimensions

        Returns:
            2D list of weights
        """
        return [
            [self.get_weight(row, col, board_size) for col in range(board_size.cols)]
            for row in range(board_size.rows)
        ]

    def as_function(self, board_size: BoardSize) -> Callable[[Position], float]:
        """
        Generate weight function for a board size.

        Args:
            board_size: Board dimensions

        Returns:
            Function that takes (row, col) and returns weight
        """
        def weight_func(pos: Position) -> float:
            row, col = pos
            return self.get_weight(row, col, board_size)

        return weight_func

    def total_weight(self, board_size: BoardSize) -> float:
        """
        Calculate total weight for a board.

        Args:
            board_size: Board dimensions

        Returns:
            Sum of all weights
        """
        matrix = self.as_matrix(board_size)
        return sum(sum(row) for row in matrix)

    def is_applicable(self, board_size: BoardSize) -> bool:
        """
        Check if this weight scheme is applicable to a board size.

        Default implementation: applicable to all sizes.
        Subclasses can override to restrict to specific sizes.

        Args:
            board_size: Board dimensions

        Returns:
            True if applicable
        """
        return True

    def __str__(self) -> str:
        """String representation."""
        return self.name

    def __repr__(self) -> str:
        """Developer representation."""
        return f"{self.__class__.__name__}(name='{self.name}')"


class MatrixWeight(Weight):
    """
    Weight scheme defined by a pre-computed matrix.

    Useful for irregular or pre-calculated weight patterns.
    """

    def __init__(self, name: str, matrix: List[List[float]], description: str = ""):
        """
        Initialize with a weight matrix.

        Args:
            name: Display name
            matrix: 2D list of weights
            description: Longer description
        """
        super().__init__(name, description)
        self.matrix = matrix
        self.board_size = BoardSize(len(matrix), len(matrix[0]) if matrix else 0)

    def get_weight(self, row: int, col: int, board_size: BoardSize) -> float:
        """Get weight from the matrix."""
        if board_size != self.board_size:
            raise ValueError(f"MatrixWeight is only valid for {self.board_size}, not {board_size}")

        if not (0 <= row < len(self.matrix)):
            raise IndexError(f"Row {row} out of range")
        if not (0 <= col < len(self.matrix[0])):
            raise IndexError(f"Column {col} out of range")

        return self.matrix[row][col]

    def is_applicable(self, board_size: BoardSize) -> bool:
        """MatrixWeight only applies to its specific size."""
        return board_size == self.board_size

    def as_matrix(self, board_size: BoardSize) -> List[List[float]]:
        """Return the matrix directly."""
        if board_size != self.board_size:
            raise ValueError(f"MatrixWeight is only valid for {self.board_size}, not {board_size}")
        return self.matrix


class FunctionWeight(Weight):
    """
    Weight scheme defined by a mathematical function.

    The function signature is: (row, col, board_size) -> weight
    """

    def __init__(
        self,
        name: str,
        func: Callable[[int, int, BoardSize], float],
        description: str = ""
    ):
        """
        Initialize with a weight function.

        Args:
            name: Display name
            func: Function that computes weight for (row, col, board_size)
            description: Longer description
        """
        super().__init__(name, description)
        self.func = func

    def get_weight(self, row: int, col: int, board_size: BoardSize) -> float:
        """Compute weight using the function."""
        return self.func(row, col, board_size)


# Type alias for backwards compatibility
WeightMatrix = List[List[float]]
WeightFunc = Callable[[Position], float]
