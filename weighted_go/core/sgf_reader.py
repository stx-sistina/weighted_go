"""
SGF (Smart Game Format) reader for Go games.

Parses SGF files and returns the final position of the main path.
"""

import re
from typing import Tuple, Optional
from .core import GamePosition, Stone, is_valid_position


class SGFError(Exception):
    """Exception raised for SGF parsing errors."""
    pass


class InvalidPositionError(Exception):
    """Exception raised when the final position is invalid."""
    pass


def sgf_to_coords(sgf_pos: str, rows: int, cols: Optional[int] = None) -> Tuple[int, int]:
    """
    Convert SGF coordinate notation to (row, col) tuple.

    SGF uses 'aa' for top-left, where 'a' = 0.
    For board sizes <= 19, uses letters a-s (skipping 'i' is not standard in SGF).

    Args:
        sgf_pos: Two-character SGF position (e.g., 'dd', 'pp')
        rows: Number of rows on the board
        cols: Number of columns (defaults to rows for square boards)

    Returns:
        Tuple of (row, col) in 0-indexed coordinates

    Raises:
        SGFError: If position is invalid
    """
    if cols is None:
        cols = rows

    if len(sgf_pos) != 2:
        raise SGFError(f"Invalid SGF position: {sgf_pos}")

    col = ord(sgf_pos[0]) - ord('a')
    row = ord(sgf_pos[1]) - ord('a')

    if row < 0 or row >= rows or col < 0 or col >= cols:
        raise SGFError(f"Position {sgf_pos} out of bounds for {rows}x{cols} board")

    return (row, col)


def parse_sgf_properties(sgf_text: str) -> dict:
    """
    Parse SGF property values.

    Args:
        sgf_text: SGF content as string

    Returns:
        Dictionary of properties and their values
    """
    properties = {}

    # Extract board size
    sz_match = re.search(r'SZ\[(\d+)\]', sgf_text)
    if sz_match:
        properties['size'] = int(sz_match.group(1))
    else:
        properties['size'] = 19  # Default to 19x19

    # Extract komi
    km_match = re.search(r'KM\[([\d.]+)\]', sgf_text)
    if km_match:
        properties['komi'] = float(km_match.group(1))

    # Extract handicap
    ha_match = re.search(r'HA\[(\d+)\]', sgf_text)
    if ha_match:
        properties['handicap'] = int(ha_match.group(1))

    # Extract player names
    pb_match = re.search(r'PB\[([^\]]*)\]', sgf_text)
    if pb_match:
        properties['black_player'] = pb_match.group(1)

    pw_match = re.search(r'PW\[([^\]]*)\]', sgf_text)
    if pw_match:
        properties['white_player'] = pw_match.group(1)

    # Extract player ranks
    br_match = re.search(r'BR\[([^\]]*)\]', sgf_text)
    if br_match:
        properties['black_rank'] = br_match.group(1)

    wr_match = re.search(r'WR\[([^\]]*)\]', sgf_text)
    if wr_match:
        properties['white_rank'] = wr_match.group(1)

    # Extract result
    re_match = re.search(r'RE\[([^\]]*)\]', sgf_text)
    if re_match:
        properties['result'] = re_match.group(1)

    # Extract date
    dt_match = re.search(r'DT\[([^\]]*)\]', sgf_text)
    if dt_match:
        properties['date'] = dt_match.group(1)

    # Extract event
    ev_match = re.search(r'EV\[([^\]]*)\]', sgf_text)
    if ev_match:
        properties['event'] = ev_match.group(1)

    return properties


def extract_main_path_moves(sgf_text: str) -> list:
    """
    Extract moves from the main path of an SGF game tree.

    Only follows the first variation at each node.

    Args:
        sgf_text: SGF content as string

    Returns:
        List of tuples: (color, position) where color is 'B' or 'W'
    """
    moves = []

    # Remove outer parentheses and split into nodes
    # SGF format: (;...;B[dd];W[pp];...)

    # Find all move properties (B[xx] or W[xx])
    # Use negative lookbehind to exclude AB and AW (setup properties)
    # Only match B or W that are not preceded by A
    move_pattern = r'(?<!A)([BW])\[([a-z]{2})\]'

    for match in re.finditer(move_pattern, sgf_text):
        color = match.group(1)
        position = match.group(2)
        moves.append((color, position))

    return moves


def read_sgf(sgf_content: str) -> GamePosition:
    """
    Read an SGF file and return the final position of the main path.

    Args:
        sgf_content: SGF file content as string

    Returns:
        GamePosition representing the final board state

    Raises:
        SGFError: If SGF format is invalid
        InvalidPositionError: If the final position is invalid (groups with no liberties)
    """
    # Parse properties
    properties = parse_sgf_properties(sgf_content)
    board_size = properties.get('size', 19)

    # Handle non-square boards if specified
    # Look for SZ[rows:cols] format
    sz_match = re.search(r'SZ\[(\d+):(\d+)\]', sgf_content)
    if sz_match:
        rows = int(sz_match.group(1))
        cols = int(sz_match.group(2))
        pos = GamePosition(rows, cols)
    else:
        pos = GamePosition(board_size, board_size)

    # Handle handicap stones (AB property)
    ab_pattern = r'AB(\[[a-z]{2}\])+'
    ab_match = re.search(ab_pattern, sgf_content)
    if ab_match:
        handicap_stones = re.findall(r'\[([a-z]{2})\]', ab_match.group(0))
        for stone_pos in handicap_stones:
            row, col = sgf_to_coords(stone_pos, pos.board.rows, pos.board.cols)
            pos.board.set((row, col), Stone.BLACK)

    # Handle initial white stones (AW property) if any
    aw_pattern = r'AW(\[[a-z]{2}\])+'
    aw_match = re.search(aw_pattern, sgf_content)
    if aw_match:
        white_stones = re.findall(r'\[([a-z]{2})\]', aw_match.group(0))
        for stone_pos in white_stones:
            row, col = sgf_to_coords(stone_pos, pos.board.rows, pos.board.cols)
            pos.board.set((row, col), Stone.WHITE)

    # Extract and play moves
    moves = extract_main_path_moves(sgf_content)

    for color, sgf_pos in moves:
        row, col = sgf_to_coords(sgf_pos, pos.board.rows, pos.board.cols)
        stone = Stone.BLACK if color == 'B' else Stone.WHITE

        # Use place_stone which handles captures and validation
        success = pos.place_stone((row, col), stone)
        if not success:
            raise SGFError(f"Invalid move: {color}[{sgf_pos}] at position ({row}, {col})")

    # Validate final position
    if not is_valid_position(pos):
        raise InvalidPositionError("Final position is invalid: some groups have no liberties")

    return pos


def read_sgf_file(filepath: str) -> GamePosition:
    """
    Read an SGF file from disk and return the final position.

    Args:
        filepath: Path to the SGF file

    Returns:
        GamePosition representing the final board state

    Raises:
        SGFError: If SGF format is invalid
        InvalidPositionError: If the final position is invalid
        FileNotFoundError: If file doesn't exist
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        sgf_content = f.read()

    return read_sgf(sgf_content)
