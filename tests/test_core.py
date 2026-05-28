"""
Tests for weighted_go.core module.
"""

import pytest
from weighted_go.core import (
    Stone, Board, GamePosition, Group,
    find_group, has_liberties, count_liberties, remove_group,
    uniform_weights, center_weights, aggressive_center_weights,
    score, score_with_territory,
    find_territory, matrix_to_func, is_valid_position
)


class TestBoard:
    def test_create_board(self):
        board = Board(9, 9)
        assert board.rows == 9
        assert board.cols == 9
        assert board.get((0, 0)) == Stone.EMPTY

    def test_set_get(self):
        board = Board(5, 5)
        board.set((2, 2), Stone.BLACK)
        assert board.get((2, 2)) == Stone.BLACK

    def test_is_valid(self):
        board = Board(5, 5)
        assert board.is_valid((0, 0))
        assert board.is_valid((4, 4))
        assert not board.is_valid((-1, 0))
        assert not board.is_valid((5, 0))
        assert not board.is_valid((0, 5))

    def test_get_neighbors(self):
        board = Board(5, 5)
        # Center has 4 neighbors
        neighbors = board.get_neighbors((2, 2))
        assert len(neighbors) == 4

        # Corner has 2 neighbors
        neighbors = board.get_neighbors((0, 0))
        assert len(neighbors) == 2
        assert (0, 1) in neighbors
        assert (1, 0) in neighbors

    def test_copy(self):
        board = Board(3, 3)
        board.set((1, 1), Stone.BLACK)
        board_copy = board.copy()

        assert board_copy.get((1, 1)) == Stone.BLACK
        board_copy.set((1, 1), Stone.WHITE)
        assert board.get((1, 1)) == Stone.BLACK  # Original unchanged

    def test_count_stones(self):
        board = Board(3, 3)
        board.set((0, 0), Stone.BLACK)
        board.set((0, 1), Stone.BLACK)
        board.set((1, 1), Stone.WHITE)

        black, white = board.count_stones()
        assert black == 2
        assert white == 1

    def test_non_square_board(self):
        # Test rectangular board
        board = Board(5, 9)
        assert board.rows == 5
        assert board.cols == 9
        assert board.is_valid((0, 0))
        assert board.is_valid((4, 8))
        assert not board.is_valid((5, 0))
        assert not board.is_valid((0, 9))

    def test_non_square_neighbors(self):
        board = Board(3, 7)
        # Test corner neighbors
        neighbors = board.get_neighbors((0, 0))
        assert len(neighbors) == 2
        assert (0, 1) in neighbors
        assert (1, 0) in neighbors

        # Test edge neighbors on longer side
        neighbors = board.get_neighbors((1, 5))
        assert len(neighbors) == 4


class TestGroup:
    def test_find_group_single(self):
        board = Board(5, 5)
        board.set((2, 2), Stone.BLACK)

        group = find_group(board, (2, 2))
        assert group is not None
        assert len(group.stones) == 1
        assert (2, 2) in group.stones
        assert group.color == Stone.BLACK
        assert len(group.liberties) == 4

    def test_find_group_multiple(self):
        board = Board(5, 5)
        board.set((2, 2), Stone.BLACK)
        board.set((2, 3), Stone.BLACK)
        board.set((3, 2), Stone.BLACK)

        group = find_group(board, (2, 2))
        assert len(group.stones) == 3
        assert (2, 2) in group.stones
        assert (2, 3) in group.stones
        assert (3, 2) in group.stones

    def test_find_group_empty(self):
        board = Board(5, 5)
        group = find_group(board, (2, 2))
        assert group is None

    def test_has_liberties_surrounded(self):
        board = Board(5, 5)
        # Surround a white stone with black
        board.set((2, 2), Stone.WHITE)
        board.set((1, 2), Stone.BLACK)
        board.set((3, 2), Stone.BLACK)
        board.set((2, 1), Stone.BLACK)
        board.set((2, 3), Stone.BLACK)

        assert not has_liberties(board, (2, 2))

    def test_has_liberties_corner(self):
        board = Board(5, 5)
        board.set((0, 0), Stone.BLACK)

        assert has_liberties(board, (0, 0))
        assert count_liberties(board, (0, 0)) == 2

    def test_count_liberties_group(self):
        board = Board(5, 5)
        board.set((2, 2), Stone.BLACK)
        board.set((2, 3), Stone.BLACK)

        liberties = count_liberties(board, (2, 2))
        assert liberties == 6

    def test_remove_group(self):
        board = Board(5, 5)
        board.set((2, 2), Stone.BLACK)
        board.set((2, 3), Stone.BLACK)
        board.set((3, 2), Stone.BLACK)

        remove_group(board, (2, 2))

        assert board.get((2, 2)) == Stone.EMPTY
        assert board.get((2, 3)) == Stone.EMPTY
        assert board.get((3, 2)) == Stone.EMPTY

    def test_find_group_non_square(self):
        board = Board(5, 9)
        board.set((2, 4), Stone.BLACK)
        board.set((2, 5), Stone.BLACK)
        board.set((3, 4), Stone.BLACK)

        group = find_group(board, (2, 4))
        assert len(group.stones) == 3
        assert group.color == Stone.BLACK

    def test_liberties_non_square_edge(self):
        # Test on a rectangular board
        board = Board(4, 10)
        board.set((0, 5), Stone.BLACK)

        # Top edge of rectangular board
        liberties = count_liberties(board, (0, 5))
        assert liberties == 3  # down, left, right (no up)


class TestGamePosition:
    def test_place_stone_basic(self):
        pos = GamePosition(5, 5)
        assert pos.place_stone((2, 2), Stone.BLACK)
        assert pos.board.get((2, 2)) == Stone.BLACK

    def test_place_stone_on_occupied(self):
        pos = GamePosition(5, 5)
        pos.place_stone((2, 2), Stone.BLACK)
        assert not pos.place_stone((2, 2), Stone.WHITE)

    def test_place_stone_out_of_bounds(self):
        pos = GamePosition(5, 5)
        assert not pos.place_stone((-1, 0), Stone.BLACK)
        assert not pos.place_stone((5, 0), Stone.BLACK)

    def test_capture(self):
        pos = GamePosition(5, 5)
        # Set up a white stone that can be captured
        pos.board.set((2, 2), Stone.WHITE)
        pos.board.set((1, 2), Stone.BLACK)
        pos.board.set((3, 2), Stone.BLACK)
        pos.board.set((2, 1), Stone.BLACK)

        # This move should capture the white stone
        assert pos.place_stone((2, 3), Stone.BLACK)
        assert pos.board.get((2, 2)) == Stone.EMPTY

    def test_suicide_not_allowed(self):
        pos = GamePosition(5, 5)
        # Set up a position where placing a stone would be suicide
        pos.board.set((1, 0), Stone.WHITE)
        pos.board.set((0, 1), Stone.WHITE)

        assert not pos.place_stone((0, 0), Stone.BLACK)

    def test_suicide_allowed_if_captures(self):
        pos = GamePosition(5, 5)
        # Set up where what looks like suicide actually captures
        pos.board.set((0, 1), Stone.WHITE)
        pos.board.set((1, 0), Stone.WHITE)
        pos.board.set((1, 1), Stone.BLACK)
        pos.board.set((0, 2), Stone.BLACK)
        pos.board.set((2, 0), Stone.BLACK)

        # This should work because it captures the white stones
        assert pos.place_stone((0, 0), Stone.BLACK)

    def test_non_square_game(self):
        pos = GamePosition(6, 10)
        assert pos.place_stone((2, 5), Stone.BLACK)
        assert pos.place_stone((2, 6), Stone.WHITE)
        assert pos.board.get((2, 5)) == Stone.BLACK
        assert pos.board.get((2, 6)) == Stone.WHITE

    def test_capture_on_non_square(self):
        pos = GamePosition(5, 8)
        # Set up capture on rectangular board
        pos.board.set((2, 3), Stone.WHITE)
        pos.board.set((1, 3), Stone.BLACK)
        pos.board.set((3, 3), Stone.BLACK)
        pos.board.set((2, 2), Stone.BLACK)

        # Capture
        assert pos.place_stone((2, 4), Stone.BLACK)
        assert pos.board.get((2, 3)) == Stone.EMPTY


class TestWeights:
    def test_uniform_weights(self):
        weights = uniform_weights(3, 3)
        for row in weights:
            for w in row:
                assert w == 1.0

    def test_center_weights(self):
        weights = center_weights(5, 5)
        # Corner should have weight 1
        assert weights[0][0] == 1.0
        # Center should have weight 3
        assert weights[2][2] == 3.0
        # Edge positions should have weight 1
        assert weights[0][2] == 1.0

    def test_center_weights_9x9(self):
        weights = center_weights(9, 9)
        # Corner should be 1
        assert weights[0][0] == 1.0
        # Center should be 5
        assert weights[4][4] == 5.0

    def test_uniform_weights_non_square(self):
        weights = uniform_weights(5, 9)
        assert len(weights) == 5
        assert len(weights[0]) == 9
        for row in weights:
            for w in row:
                assert w == 1.0

    def test_center_weights_non_square(self):
        weights = center_weights(5, 9)
        # Corners should be 1
        assert weights[0][0] == 1.0
        assert weights[0][8] == 1.0
        assert weights[4][0] == 1.0
        assert weights[4][8] == 1.0
        # Center-ish position (2, 4) - limited by shorter dimension
        # dist_from_row_edge = min(2, 2) = 2
        # dist_from_col_edge = min(4, 4) = 4
        # weight = 1 + min(2, 4) = 3
        assert weights[2][4] == 3.0

    def test_aggressive_center_weights_basic(self):
        weights = aggressive_center_weights(5, 5)
        # Corner (0,0): 1 + min(0,4) + min(0,4) = 1 + 0 + 0 = 1
        assert weights[0][0] == 1.0
        # (1,1): 1 + min(1,3) + min(1,3) = 1 + 1 + 1 = 3
        assert weights[1][1] == 3.0
        # Center (2,2): 1 + min(2,2) + min(2,2) = 1 + 2 + 2 = 5
        assert weights[2][2] == 5.0
        # Edge (0,2): 1 + 0 + 2 = 3
        assert weights[0][2] == 3.0
        # Another corner (4,4): 1 + 0 + 0 = 1
        assert weights[4][4] == 1.0

    def test_aggressive_center_weights_19x19(self):
        weights = aggressive_center_weights(19, 19)
        # Corner (0,0): 1 + 0 + 0 = 1
        assert weights[0][0] == 1.0
        # Center (9,9): 1 + min(9,9) + min(9,9) = 1 + 9 + 9 = 19
        assert weights[9][9] == 19.0
        # Opposite corner (18,18): 1 + min(18,0) + min(18,0) = 1 + 0 + 0 = 1
        assert weights[18][18] == 1.0

    def test_aggressive_center_weights_non_square(self):
        weights = aggressive_center_weights(5, 9)
        # All four corners should be 1
        assert weights[0][0] == 1.0  # top-left
        assert weights[0][8] == 1.0  # top-right
        assert weights[4][0] == 1.0  # bottom-left
        assert weights[4][8] == 1.0  # bottom-right
        # Center-ish (2,4): 1 + min(2,2) + min(4,4) = 1 + 2 + 4 = 7
        assert weights[2][4] == 7.0
        # Edge position (0,4): 1 + 0 + 4 = 5
        assert weights[0][4] == 5.0


class TestScoring:
    def test_score_basic_uniform(self):
        # Test area scoring (stones + territory)
        pos = GamePosition(3, 3)
        pos.board.set((0, 0), Stone.BLACK)
        pos.board.set((0, 1), Stone.BLACK)
        pos.board.set((1, 1), Stone.WHITE)

        weights = uniform_weights(3, 3)
        black_score, white_score = score(pos, weights)

        # Area scoring: scores include stones + territory
        # Total should equal board size (9)
        assert black_score + white_score == 9.0
        assert black_score == 5.0  # 2 stones + 3 territory
        assert white_score == 4.0  # 1 stone + 3 territory

    def test_score_weighted(self):
        pos = GamePosition(5, 5)
        # Place stones at center and corner
        pos.board.set((2, 2), Stone.BLACK)  # Center, weight 3
        pos.board.set((0, 0), Stone.WHITE)  # Corner, weight 1

        weights = center_weights(5, 5)
        black_score, white_score = score(pos, weights)

        # With area scoring, total should equal sum of all weights
        total_weights = sum(sum(row) for row in weights)
        assert black_score + white_score == total_weights
        # Black should have center advantage with center weights
        assert black_score > white_score

    def test_score_with_function(self):
        pos = GamePosition(3, 3)
        pos.board.set((0, 0), Stone.BLACK)
        pos.board.set((1, 1), Stone.WHITE)

        # Custom weight function: weight = row + col
        def weight_func(p):
            return float(p[0] + p[1])

        black_score, white_score = score(pos, weight_func)

        # Total should equal sum of all weights: 0+1+2+1+2+3+2+3+4 = 18
        assert black_score + white_score == 18.0
        # With this weighting and area scoring, black gets lower-weighted territory
        assert black_score < white_score

    def test_score_area_totals(self):
        # Test that area scoring always adds up to total board weight
        pos = GamePosition(5, 5)
        # Create a simple surrounded territory
        # Black surrounds top-left corner
        pos.board.set((0, 2), Stone.BLACK)
        pos.board.set((1, 2), Stone.BLACK)
        pos.board.set((2, 0), Stone.BLACK)
        pos.board.set((2, 1), Stone.BLACK)
        pos.board.set((2, 2), Stone.BLACK)

        # Test with all three weight schemes
        weights_uniform = uniform_weights(5, 5)
        b_u, w_u = score(pos, weights_uniform)
        assert b_u + w_u == 25.0  # 5x5 board

        weights_center = center_weights(5, 5)
        b_c, w_c = score(pos, weights_center)
        total_center = sum(sum(row) for row in weights_center)
        assert b_c + w_c == total_center

        weights_agg = aggressive_center_weights(5, 5)
        b_a, w_a = score(pos, weights_agg)
        total_agg = sum(sum(row) for row in weights_agg)
        assert b_a + w_a == total_agg

    def test_score_aggressive_weights(self):
        pos = GamePosition(5, 5)
        # Place stones at different positions
        pos.board.set((0, 0), Stone.BLACK)  # Corner, weight = 1
        pos.board.set((2, 2), Stone.WHITE)  # Center, weight = 5
        pos.board.set((1, 3), Stone.BLACK)  # weight = 1 + 1 + 1 = 3

        weights = aggressive_center_weights(5, 5)
        black_score, white_score = score(pos, weights)

        # With area scoring, total should equal sum of all weights
        total_weights = sum(sum(row) for row in weights)
        assert black_score + white_score == total_weights
        # Center stone should give white advantage
        assert white_score > black_score

    def test_score_non_square_board(self):
        pos = GamePosition(5, 9)
        pos.board.set((0, 0), Stone.BLACK)
        pos.board.set((4, 8), Stone.WHITE)
        pos.board.set((2, 4), Stone.BLACK)

        weights = uniform_weights(5, 9)
        black_score, white_score = score(pos, weights)

        # Total should be 5*9 = 45
        assert black_score + white_score == 45.0

    def test_score_aggressive_non_square(self):
        pos = GamePosition(5, 9)
        pos.board.set((0, 0), Stone.BLACK)    # weight = 1 (corner)
        pos.board.set((4, 8), Stone.WHITE)    # weight = 1 (corner)
        pos.board.set((2, 4), Stone.BLACK)    # weight = 7

        weights = aggressive_center_weights(5, 9)
        black_score, white_score = score(pos, weights)

        # Total should equal sum of all weights
        total_weights = sum(sum(row) for row in weights)
        assert black_score + white_score == total_weights


class TestTerritory:
    def test_find_territory(self):
        board = Board(5, 5)
        # Create a black-surrounded region
        board.set((0, 2), Stone.BLACK)
        board.set((1, 2), Stone.BLACK)
        board.set((2, 0), Stone.BLACK)
        board.set((2, 1), Stone.BLACK)
        board.set((2, 2), Stone.BLACK)

        territory, owner = find_territory(board, (0, 0))

        assert owner == Stone.BLACK
        assert len(territory) == 4

    def test_find_territory_contested(self):
        board = Board(5, 5)
        # Create a contested region (touches both colors)
        board.set((0, 0), Stone.BLACK)
        board.set((0, 2), Stone.WHITE)

        territory, owner = find_territory(board, (0, 1))

        assert owner == Stone.EMPTY


class TestValidation:
    def test_valid_position_empty_board(self):
        pos = GamePosition(5, 5)
        assert is_valid_position(pos)

    def test_valid_position_normal_game(self):
        pos = GamePosition(5, 5)
        pos.place_stone((2, 2), Stone.BLACK)
        pos.place_stone((2, 3), Stone.WHITE)
        pos.place_stone((3, 2), Stone.BLACK)
        assert is_valid_position(pos)

    def test_invalid_position_no_liberties(self):
        pos = GamePosition(5, 5)
        # Manually create an invalid position with a surrounded stone
        pos.board.set((2, 2), Stone.WHITE)
        pos.board.set((1, 2), Stone.BLACK)
        pos.board.set((3, 2), Stone.BLACK)
        pos.board.set((2, 1), Stone.BLACK)
        pos.board.set((2, 3), Stone.BLACK)

        # This position is invalid - white stone has no liberties
        assert not is_valid_position(pos)

    def test_valid_after_moves(self):
        pos = GamePosition(5, 5)
        # Set up and complete a capture
        pos.board.set((2, 2), Stone.WHITE)
        pos.board.set((1, 2), Stone.BLACK)
        pos.board.set((3, 2), Stone.BLACK)
        pos.board.set((2, 1), Stone.BLACK)

        # Before capturing move, position is valid
        assert is_valid_position(pos)

        # After capture, position should still be valid
        pos.place_stone((2, 3), Stone.BLACK)
        assert is_valid_position(pos)

    def test_place_stone_maintains_validity(self):
        # Verify that place_stone never creates invalid positions
        pos = GamePosition(5, 5)

        # These moves should all succeed and maintain validity
        moves = [
            ((2, 2), Stone.BLACK),
            ((2, 3), Stone.WHITE),
            ((3, 2), Stone.BLACK),
            ((1, 2), Stone.WHITE),
        ]

        for move_pos, stone in moves:
            result = pos.place_stone(move_pos, stone)
            if result:  # If move was accepted
                assert is_valid_position(pos), f"Position invalid after placing {stone} at {move_pos}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
