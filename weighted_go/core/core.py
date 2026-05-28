"""
Weighted Go - A Go variant where each board intersection has a weight.
Regular Go corresponds to w_ij = 1 for all i, j.
"""

from enum import Enum
from typing import List, Tuple, Set, Optional, Callable, Union
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


class Board:
    """Represents the game board."""

    def __init__(self, rows: int, cols: int):
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


class Group:
    """Represents a connected group of stones."""

    def __init__(self, color: Stone):
        self.stones: Set[Position] = set()
        self.color = color
        self.liberties: Set[Position] = set()


def find_group(board: Board, pos: Position) -> Optional[Group]:
    """Find all stones in the group containing the given position."""
    stone = board.get(pos)
    if stone == Stone.EMPTY:
        return None

    group = Group(stone)
    visited: Set[Position] = set()
    liberties: Set[Position] = set()

    def dfs(p: Position):
        if p in visited:
            return
        visited.add(p)

        if board.get(p) == stone:
            group.stones.add(p)
            for neighbor in board.get_neighbors(p):
                dfs(neighbor)
        elif board.get(p) == Stone.EMPTY:
            liberties.add(p)

    dfs(pos)
    group.liberties = liberties
    return group


def has_liberties(board: Board, pos: Position) -> bool:
    """Check if the group at the given position has any liberties."""
    group = find_group(board, pos)
    if group is None:
        return False
    return len(group.liberties) > 0


def count_liberties(board: Board, pos: Position) -> int:
    """Count the number of liberties for the group at the given position."""
    group = find_group(board, pos)
    if group is None:
        return 0
    return len(group.liberties)


def remove_group(board: Board, pos: Position) -> None:
    """Remove all stones in the group containing the given position."""
    group = find_group(board, pos)
    if group is None:
        return

    for stone_pos in group.stones:
        board.set(stone_pos, Stone.EMPTY)


class GamePosition:
    """Represents the current state of the game."""

    def __init__(self, rows: int, cols: int):
        self.board = Board(rows, cols)

    def place_stone(self, pos: Position, stone: Stone) -> bool:
        """
        Attempt to place a stone at the given position.
        Returns True if successful, False otherwise.
        """
        if not self.board.is_valid(pos) or self.board.get(pos) != Stone.EMPTY:
            return False

        # Create a temporary board to test the move
        temp_board = self.board.copy()
        temp_board.set(pos, stone)

        # Capture opponent groups with no liberties
        opponent = stone.opponent()
        for neighbor in temp_board.get_neighbors(pos):
            if temp_board.get(neighbor) == opponent:
                if not has_liberties(temp_board, neighbor):
                    remove_group(temp_board, neighbor)

        # Check if our own group has liberties (suicide rule)
        if not has_liberties(temp_board, pos):
            return False

        # Move is valid, update the actual board
        self.board = temp_board
        return True

    def copy(self) -> "GamePosition":
        """Create a deep copy of the game position."""
        new_pos = GamePosition(self.board.rows, self.board.cols)
        new_pos.board = self.board.copy()
        return new_pos


# Weight function type
WeightFunc = Callable[[Position], float]
WeightMatrix = List[List[float]]


def uniform_weights(rows: int, cols: int) -> WeightMatrix:
    """Create a weight matrix where all positions have weight 1."""
    return [[1.0 for _ in range(cols)] for _ in range(rows)]


def center_weights(rows: int, cols: int) -> WeightMatrix:
    """
    Create weights where w_ij = 1 + min(min(x, M-1-x), min(y, N-1-y)).
    This gives higher values to center positions.
    Convention: corners/edges start at 1, not 0.
    For a 9x9 board, weights range from 1 to 5.
    """
    weights = []
    for i in range(rows):
        row = []
        for j in range(cols):
            dist_from_row_edge = min(i, rows - 1 - i)
            dist_from_col_edge = min(j, cols - 1 - j)
            weight = 1 + min(dist_from_row_edge, dist_from_col_edge)
            row.append(float(weight))
        weights.append(row)
    return weights


def aggressive_center_weights(rows: int, cols: int) -> WeightMatrix:
    """
    Create weights that reward the center more aggressively.

    Weight at position (i,j) is the sum of (1-indexed) distances from edges:
    w[i][j] = (1 + min(i, rows-1-i)) + (1 + min(j, cols-1-j))
            = 1 + min(i, rows-1-i) + 1 + min(j, cols-1-j)
            = 2 + min(i, rows-1-i) + min(j, cols-1-j)

    Equivalently: (m) + (n) where m = 1+min(i, rows-1-i), n = 1+min(j, cols-1-j)

    This gives symmetric weights that diminish toward all four corners.

    Four corners have weight 1+1 = 2... wait, let me recalculate.

    For corners (0,0): min(0, M-1) = 0, min(0, N-1) = 0, so we need weight = 1
    So formula should be: 1 + min(i, rows-1-i) + min(j, cols-1-j)

    For a 5x5 board:
    - Corner (0,0): 1 + 0 + 0 = 1
    - Edge (0,2): 1 + 0 + 2 = 3
    - Center (2,2): 1 + 2 + 2 = 5

    For a 19x19 board, center (9,9): 1 + 9 + 9 = 19

    Args:
        rows: Number of rows
        cols: Number of columns

    Returns:
        Weight matrix where w[i][j] = 1 + dist_from_row_edge + dist_from_col_edge
    """
    weights = []
    for i in range(rows):
        row = []
        for j in range(cols):
            dist_from_row_edge = min(i, rows - 1 - i)
            dist_from_col_edge = min(j, cols - 1 - j)
            weight = 1 + dist_from_row_edge + dist_from_col_edge
            row.append(float(weight))
        weights.append(row)
    return weights


def matrix_to_func(weights: WeightMatrix) -> WeightFunc:
    """Convert a weight matrix to a weight function."""
    def weight_func(pos: Position) -> float:
        row, col = pos
        if 0 <= row < len(weights) and 0 <= col < len(weights[row]):
            return weights[row][col]
        return 0.0
    return weight_func


def score(pos: GamePosition, w: Union[WeightMatrix, WeightFunc]) -> Tuple[float, float]:
    """
    Calculate the weighted score for both players using area scoring (Chinese-style).

    In area scoring:
    - Black gets: black stones + black territory
    - White gets: white stones + white territory
    - Contested territory is split 50-50
    - Total scores always add up to total board weight

    Args:
        pos: The game position
        w: Either a weight matrix (List[List[float]]) or a weight function (Callable)

    Returns:
        Tuple of (black_score, white_score)
    """
    # Convert matrix to function if needed
    if isinstance(w, list):
        weight_func = matrix_to_func(w)
    else:
        weight_func = w

    black_score = 0.0
    white_score = 0.0
    assigned: Set[Position] = set()

    # First, score all stones
    for i in range(pos.board.rows):
        for j in range(pos.board.cols):
            p = (i, j)
            stone = pos.board.get(p)

            if stone != Stone.EMPTY:
                weight = weight_func(p)
                assigned.add(p)
                if stone == Stone.BLACK:
                    black_score += weight
                elif stone == Stone.WHITE:
                    white_score += weight

    # Score empty territory
    for i in range(pos.board.rows):
        for j in range(pos.board.cols):
            p = (i, j)
            if p in assigned:
                continue

            # Find the territory containing this position
            territory, owner = find_territory(pos.board, p)

            # Score the territory
            for tp in territory:
                assigned.add(tp)
                weight = weight_func(tp)
                if owner == Stone.BLACK:
                    black_score += weight
                elif owner == Stone.WHITE:
                    white_score += weight
                else:
                    # Contested territory - split 50-50
                    black_score += weight / 2.0
                    white_score += weight / 2.0

    return black_score, white_score


def score_with_territory(pos: GamePosition, w: Union[WeightMatrix, WeightFunc]) -> Tuple[float, float]:
    """
    Calculate score including territory.
    Territory is determined using flood-fill from each color.

    Args:
        pos: The game position
        w: Either a weight matrix or a weight function

    Returns:
        Tuple of (black_score, white_score)
    """
    # Convert matrix to function if needed
    if isinstance(w, list):
        weight_func = matrix_to_func(w)
    else:
        weight_func = w

    black_score = 0.0
    white_score = 0.0
    assigned: Set[Position] = set()

    # First, score all stones
    for i in range(pos.board.rows):
        for j in range(pos.board.cols):
            p = (i, j)
            weight = weight_func(p)
            stone = pos.board.get(p)

            if stone == Stone.BLACK:
                black_score += weight
                assigned.add(p)
            elif stone == Stone.WHITE:
                white_score += weight
                assigned.add(p)

    # Score empty territory
    for i in range(pos.board.rows):
        for j in range(pos.board.cols):
            p = (i, j)
            if p in assigned or pos.board.get(p) != Stone.EMPTY:
                continue

            # Find the territory containing this position
            territory, owner = find_territory(pos.board, p)

            # Score the territory
            for tp in territory:
                assigned.add(tp)
                weight = weight_func(tp)
                if owner == Stone.BLACK:
                    black_score += weight
                elif owner == Stone.WHITE:
                    white_score += weight

    return black_score, white_score


def find_territory(board: Board, start: Position) -> Tuple[List[Position], Stone]:
    """
    Find a connected region of empty spaces and determine its owner.

    Returns:
        Tuple of (territory_positions, owner_stone)
        Owner is EMPTY if territory is contested.
    """
    if board.get(start) != Stone.EMPTY:
        return [], Stone.EMPTY

    visited: Set[Position] = set()
    territory: List[Position] = []
    adjacent_colors: Set[Stone] = set()

    def dfs(p: Position):
        if p in visited or not board.is_valid(p):
            return
        visited.add(p)

        stone = board.get(p)
        if stone == Stone.EMPTY:
            territory.append(p)
            for neighbor in board.get_neighbors(p):
                dfs(neighbor)
        else:
            adjacent_colors.add(stone)

    dfs(start)

    # Determine owner: if territory touches only one color, that color owns it
    if len(adjacent_colors) == 1:
        owner = list(adjacent_colors)[0]
        return territory, owner

    # Territory is contested or neutral
    return territory, Stone.EMPTY


def is_valid_position(pos: GamePosition) -> bool:
    """
    Validate that a game position is legal.
    All groups on the board must have at least one liberty.

    Args:
        pos: The game position to validate

    Returns:
        True if the position is valid, False otherwise
    """
    visited: Set[Position] = set()

    for i in range(pos.board.rows):
        for j in range(pos.board.cols):
            p = (i, j)
            stone = pos.board.get(p)

            # Skip empty positions and already-visited stones
            if stone == Stone.EMPTY or p in visited:
                continue

            # Find the group and check if it has liberties
            group = find_group(pos.board, p)
            if group is None:
                continue

            # Check that this group has at least one liberty
            if len(group.liberties) == 0:
                return False

            # Mark all stones in this group as visited
            for stone_pos in group.stones:
                visited.add(stone_pos)

    return True
