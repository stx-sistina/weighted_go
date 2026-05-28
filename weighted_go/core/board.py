"""
Board representation for Weighted Go.

Contains the core board data structures: Stone, BoardSize, and Board.
"""

from enum import Enum
from typing import List, Tuple
from copy import deepcopy


class Stone(Enum):
    """Stone color on the board."""
    EMPTY = 0
    BLACK = 1
    WHITE = 2

    def __str__(self):
        return {Stone.EMPTY: ".", Stone.BLACK: "X", Stone.WHITE: "O"}[self]

    def opponent(self) -> "Stone":
        """Return the opponent's color."""
        if self == Stone.BLACK:
            return Stone.WHITE
        elif self == Stone.WHITE:
            return Stone.BLACK
        return Stone.EMPTY


Position = Tuple[int, int]


class BoardSize:
    """Represents a Go board size."""

    def __init__(self, rows: int, cols: int):
        """
        Create a board size specification.

        Args:
            rows: Number of rows
            cols: Number of columns

        Raises:
            ValueError: If rows or cols are not positive
        """
        if rows <= 0 or cols <= 0:
            raise ValueError(f"Invalid board size: {rows}x{cols}")

        self.rows = rows
        self.cols = cols

    def is_square(self) -> bool:
        """Check if this is a square board."""
        return self.rows == self.cols

    def is_standard(self) -> bool:
        """Check if this is a standard board size (9x9, 13x13, 19x19)."""
        return self.is_square() and self.rows in (9, 13, 19)

    def total_points(self) -> int:
        """Get total number of intersections on the board."""
        return self.rows * self.cols

    def __str__(self) -> str:
        """String representation."""
        if self.is_square():
            return f"{self.rows}x{self.rows}"
        return f"{self.rows}x{self.cols}"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"BoardSize({self.rows}, {self.cols})"

    def __eq__(self, other) -> bool:
        """Equality comparison."""
        if not isinstance(other, BoardSize):
            return False
        return self.rows == other.rows and self.cols == other.cols

    def __hash__(self) -> int:
        """Hash for use in sets/dicts."""
        return hash((self.rows, self.cols))

    @classmethod
    def from_string(cls, size_str: str) -> 'BoardSize':
        """
        Parse a board size from string.

        Supported formats:
        - "19" or "19x19" -> 19x19 square board
        - "13:9" or "13x9" -> 13x9 rectangular board

        Args:
            size_str: String representation

        Returns:
            BoardSize instance

        Raises:
            ValueError: If format is invalid

        Examples:
            >>> BoardSize.from_string("19")
            BoardSize(19, 19)
            >>> BoardSize.from_string("13x9")
            BoardSize(13, 9)
        """
        size_str = size_str.strip()

        # Try formats with separator
        for sep in ['x', 'X', ':']:
            if sep in size_str:
                parts = size_str.split(sep)
                if len(parts) == 2:
                    try:
                        rows = int(parts[0])
                        cols = int(parts[1])
                        return cls(rows, cols)
                    except ValueError:
                        pass

        # Try single number (square board)
        try:
            size = int(size_str)
            return cls(size, size)
        except ValueError:
            pass

        raise ValueError(f"Invalid board size format: {size_str}")

    @classmethod
    def standard_19(cls) -> 'BoardSize':
        """Create standard 19x19 board."""
        return cls(19, 19)

    @classmethod
    def standard_13(cls) -> 'BoardSize':
        """Create standard 13x13 board."""
        return cls(13, 13)

    @classmethod
    def standard_9(cls) -> 'BoardSize':
        """Create standard 9x9 board."""
        return cls(9, 9)


class Board:
    """Represents the game board."""

    def __init__(self, rows: int, cols: int):
        """
        Create a new board.

        Args:
            rows: Number of rows
            cols: Number of columns
        """
        self.rows = rows
        self.cols = cols
        self.grid = [[Stone.EMPTY for _ in range(cols)] for _ in range(rows)]

    def is_valid(self, pos: Position) -> bool:
        """Check if position is within board bounds."""
        row, col = pos
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get(self, pos: Position) -> Stone:
        """Get the stone at the given position."""
        if not self.is_valid(pos):
            return Stone.EMPTY
        row, col = pos
        return self.grid[row][col]

    def set(self, pos: Position, stone: Stone) -> None:
        """Set the stone at the given position."""
        if self.is_valid(pos):
            row, col = pos
            self.grid[row][col] = stone

    def get_neighbors(self, pos: Position) -> List[Position]:
        """Get the four orthogonal neighbors of a position."""
        row, col = pos
        neighbors = [
            (row - 1, col),
            (row + 1, col),
            (row, col - 1),
            (row, col + 1),
        ]
        return [n for n in neighbors if self.is_valid(n)]

    def copy(self) -> "Board":
        """Create a deep copy of the board."""
        new_board = Board(self.rows, self.cols)
        new_board.grid = deepcopy(self.grid)
        return new_board

    def __str__(self) -> str:
        """String representation of the board."""
        result = []
        for row in self.grid:
            result.append(" ".join(str(stone) for stone in row))
        return "\n".join(result)

    def count_stones(self) -> Tuple[int, int]:
        """Count stones for each color. Returns (black_count, white_count)."""
        black = sum(1 for row in self.grid for stone in row if stone == Stone.BLACK)
        white = sum(1 for row in self.grid for stone in row if stone == Stone.WHITE)
        return black, white
