"""
Tests for SGF reader functionality.
"""

import pytest
from weighted_go import (
    read_sgf, sgf_to_coords, parse_sgf_properties,
    extract_main_path_moves, SGFError, InvalidPositionError,
    Stone
)


class TestSGFCoordinates:
    def test_sgf_to_coords_basic(self):
        # 'aa' should be (0, 0)
        assert sgf_to_coords('aa', 19) == (0, 0)

    def test_sgf_to_coords_tengen(self):
        # 'jj' on 19x19 is (9, 9) - tengen/center
        assert sgf_to_coords('jj', 19) == (9, 9)

    def test_sgf_to_coords_corner(self):
        # 'ss' on 19x19 is (18, 18)
        assert sgf_to_coords('ss', 19) == (18, 18)

    def test_sgf_to_coords_9x9(self):
        # 'ee' on 9x9 is center (4, 4)
        assert sgf_to_coords('ee', 9) == (4, 4)

    def test_sgf_to_coords_non_square(self):
        # 'ai' on 5x9 board: col a(0), row i(8) = (8, 0)
        # But row i is out of bounds for 5 rows!
        # Use 'ad' instead: col a(0), row d(3) = (3, 0)
        assert sgf_to_coords('ad', 5, 9) == (3, 0)

    def test_sgf_to_coords_invalid_length(self):
        with pytest.raises(SGFError):
            sgf_to_coords('a', 19)

    def test_sgf_to_coords_out_of_bounds(self):
        with pytest.raises(SGFError):
            sgf_to_coords('zz', 19)


class TestSGFProperties:
    def test_parse_size_19(self):
        sgf = "(;GM[1]FF[4]SZ[19])"
        props = parse_sgf_properties(sgf)
        assert props['size'] == 19

    def test_parse_size_9(self):
        sgf = "(;SZ[9])"
        props = parse_sgf_properties(sgf)
        assert props['size'] == 9

    def test_parse_default_size(self):
        sgf = "(;GM[1]FF[4])"
        props = parse_sgf_properties(sgf)
        assert props['size'] == 19

    def test_parse_komi(self):
        sgf = "(;SZ[19]KM[6.5])"
        props = parse_sgf_properties(sgf)
        assert props['komi'] == 6.5

    def test_parse_handicap(self):
        sgf = "(;SZ[19]HA[4])"
        props = parse_sgf_properties(sgf)
        assert props['handicap'] == 4


class TestExtractMoves:
    def test_extract_simple_moves(self):
        sgf = "(;B[dd];W[pp];B[pd];W[dp])"
        moves = extract_main_path_moves(sgf)
        assert len(moves) == 4
        assert moves[0] == ('B', 'dd')
        assert moves[1] == ('W', 'pp')
        assert moves[2] == ('B', 'pd')
        assert moves[3] == ('W', 'dp')

    def test_extract_no_moves(self):
        sgf = "(;GM[1]FF[4]SZ[19])"
        moves = extract_main_path_moves(sgf)
        assert len(moves) == 0

    def test_extract_with_comments(self):
        sgf = "(;B[dd]C[Good move];W[pp]C[Standard response])"
        moves = extract_main_path_moves(sgf)
        assert len(moves) == 2
        assert moves[0] == ('B', 'dd')
        assert moves[1] == ('W', 'pp')


class TestReadSGF:
    def test_read_empty_game(self):
        sgf = "(;GM[1]FF[4]SZ[9])"
        pos = read_sgf(sgf)
        assert pos.board.rows == 9
        assert pos.board.cols == 9
        # All positions should be empty
        for i in range(9):
            for j in range(9):
                assert pos.board.get((i, j)) == Stone.EMPTY

    def test_read_simple_game(self):
        # Simple game on 5x5 board
        sgf = "(;SZ[5];B[bb];W[cc];B[cb])"
        pos = read_sgf(sgf)

        # Check stones are in correct positions
        # In SGF: first char = column, second char = row
        # 'bb' = col b(1), row b(1) = (1, 1)
        assert pos.board.get((1, 1)) == Stone.BLACK
        # 'cc' = col c(2), row c(2) = (2, 2)
        assert pos.board.get((2, 2)) == Stone.WHITE
        # 'cb' = col c(2), row b(1) = (1, 2)
        assert pos.board.get((1, 2)) == Stone.BLACK

    def test_read_with_handicap(self):
        # Game with handicap stones
        sgf = "(;SZ[9]HA[2]AB[cc][gg];W[ee])"
        pos = read_sgf(sgf)

        # Handicap stones
        assert pos.board.get((2, 2)) == Stone.BLACK
        assert pos.board.get((6, 6)) == Stone.BLACK
        # White move
        assert pos.board.get((4, 4)) == Stone.WHITE

    def test_read_with_capture(self):
        # Set up a capture scenario
        sgf = "(;SZ[5];B[bb];W[bc];B[cb];W[cc];B[ac];W[bd];B[ad];W[cd];B[ab])"
        pos = read_sgf(sgf)

        # After this sequence, some stones should be captured
        # The final position should be valid
        assert pos is not None

    def test_invalid_move_out_of_bounds(self):
        sgf = "(;SZ[5];B[zz])"
        with pytest.raises(SGFError):
            read_sgf(sgf)

    def test_invalid_position_no_liberties(self):
        # Manually create SGF that would result in invalid position
        # This is a contrived example - normal play wouldn't create this
        sgf_invalid = "(;SZ[5]AB[bb]AW[ab][ba][bc][cb])"
        # Black stone at bb surrounded by white with no liberties
        # This should be caught by validation
        with pytest.raises(InvalidPositionError):
            read_sgf(sgf_invalid)

    def test_read_9x9_game(self):
        # A more realistic 9x9 game opening
        sgf = """(;GM[1]FF[4]SZ[9]
        ;B[ee]
        ;W[cc]
        ;B[gg]
        ;W[cg]
        ;B[ge]
        ;W[ec])"""
        pos = read_sgf(sgf)

        assert pos.board.rows == 9
        assert pos.board.get((4, 4)) == Stone.BLACK  # ee
        assert pos.board.get((2, 2)) == Stone.WHITE  # cc
        assert pos.board.get((6, 6)) == Stone.BLACK  # gg

    def test_non_square_board(self):
        # SGF with non-square board (5 rows, 9 cols)
        # 'ia' = col i(8), row a(0) = (0, 8)
        sgf = "(;SZ[5:9];B[aa];W[ia])"
        pos = read_sgf(sgf)

        assert pos.board.rows == 5
        assert pos.board.cols == 9
        assert pos.board.get((0, 0)) == Stone.BLACK
        assert pos.board.get((0, 8)) == Stone.WHITE


class TestRealWorldSGF:
    def test_standard_opening(self):
        # Standard opening pattern
        sgf = """(;GM[1]FF[4]SZ[19]KM[6.5]
        ;B[pd]
        ;W[dp]
        ;B[pp]
        ;W[dd]
        ;B[fc]
        ;W[cn])"""
        pos = read_sgf(sgf)

        # Check some key stones (SGF format: column-row)
        assert pos.board.get((3, 15)) == Stone.BLACK  # pd = col p(15), row d(3)
        assert pos.board.get((15, 3)) == Stone.WHITE  # dp = col d(3), row p(15)
        assert pos.board.get((15, 15)) == Stone.BLACK  # pp = col p(15), row p(15)
        assert pos.board.get((3, 3)) == Stone.WHITE   # dd = col d(3), row d(3)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
