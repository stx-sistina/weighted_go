"""
Weighted Go - Core game logic.

Handles groups, liberties, captures, position validation, territory detection, and scoring.
"""

from typing import List, Tuple, Set, Optional

from .board import Stone, Board, Position, BoardSize
from .weight import Weight


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
    visited = set()

    def dfs(p: Position):
        if p in visited or not board.is_valid(p):
            return
        visited.add(p)

        current_stone = board.get(p)
        if current_stone == stone:
            group.stones.add(p)
            for neighbor in board.get_neighbors(p):
                dfs(neighbor)
        elif current_stone == Stone.EMPTY:
            group.liberties.add(p)

    dfs(pos)
    return group


def has_liberties(board: Board, pos: Position) -> bool:
    """Check if the group at this position has any liberties."""
    group = find_group(board, pos)
    return group is not None and len(group.liberties) > 0


def count_liberties(board: Board, pos: Position) -> int:
    """Count the liberties of the group at this position."""
    group = find_group(board, pos)
    return len(group.liberties) if group else 0


def remove_group(board: Board, pos: Position) -> None:
    """Remove the group at the given position from the board."""
    group = find_group(board, pos)
    if group:
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
        if self.board.get(pos) != Stone.EMPTY:
            return False

        # Temporarily place the stone
        self.board.set(pos, stone)

        # Check for captures
        opponent = stone.opponent()
        for neighbor in self.board.get_neighbors(pos):
            if self.board.get(neighbor) == opponent:
                if not has_liberties(self.board, neighbor):
                    remove_group(self.board, neighbor)

        # Check for suicide (illegal unless it captured)
        if not has_liberties(self.board, pos):
            # This is suicide - undo the move
            self.board.set(pos, Stone.EMPTY)
            return False

        return True


def score(pos: GamePosition, weight: Weight) -> Tuple[float, float]:
    """
    Calculate score using area scoring.

    In area scoring, Black's score is the sum of:
    - Weights of all intersections with black stones
    - Weights of all empty territory controlled by black

    Same for White. This ensures Black + White = total board weight.

    Args:
        pos: The game position
        weight: Weight scheme to use for scoring

    Returns:
        Tuple of (black_score, white_score)
    """
    board_size = BoardSize(pos.board.rows, pos.board.cols)
    weight_func = weight.as_function(board_size)

    black_score = 0.0
    white_score = 0.0
    assigned: Set[Position] = set()

    # First, score all stones
    for i in range(pos.board.rows):
        for j in range(pos.board.cols):
            p = (i, j)
            w = weight_func(p)
            stone = pos.board.get(p)

            if stone == Stone.BLACK:
                black_score += w
                assigned.add(p)
            elif stone == Stone.WHITE:
                white_score += w
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
                w = weight_func(tp)
                if owner == Stone.BLACK:
                    black_score += w
                elif owner == Stone.WHITE:
                    white_score += w
                else:
                    # Contested territory splits 50-50
                    black_score += w * 0.5
                    white_score += w * 0.5

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
    else:
        owner = Stone.EMPTY  # Contested or empty

    return territory, owner


def is_valid_position(pos: GamePosition) -> bool:
    """
    Check if a game position is valid.
    A position is valid if all groups on the board have at least one liberty.

    Args:
        pos: The game position to validate

    Returns:
        True if valid, False otherwise
    """
    checked: Set[Position] = set()

    for i in range(pos.board.rows):
        for j in range(pos.board.cols):
            p = (i, j)
            stone = pos.board.get(p)

            if stone != Stone.EMPTY and p not in checked:
                # Check this group
                group = find_group(pos.board, p)
                if group is None or len(group.liberties) == 0:
                    return False

                # Mark all stones in this group as checked
                checked.update(group.stones)

    return True
