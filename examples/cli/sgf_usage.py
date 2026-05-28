"""
Example demonstrating SGF file reading and scoring.
"""

from weighted_go import (
    read_sgf, read_sgf_file, SGFError, InvalidPositionError,
    score, uniform_weights, center_weights, aggressive_center_weights
)


def main():
    print("=== SGF Reader Examples ===\n")

    # Example 1: Read from string
    print("Example 1: Simple 9x9 game from string")
    sgf_string = """(;GM[1]FF[4]SZ[9]KM[5.5]
    ;B[ee]
    ;W[cc]
    ;B[gg]
    ;W[cg]
    ;B[ge]
    ;W[ec])"""

    try:
        pos = read_sgf(sgf_string)
        print("Final position:")
        print(pos.board)
        print()

        # Score with different schemes
        b_count, w_count = pos.board.count_stones()
        print(f"Stone count: Black={b_count}, White={w_count}")

        center_w = center_weights(9, 9)
        b_center, w_center = score(pos, center_w)
        print(f"Center weights: Black={b_center:.0f}, White={w_center:.0f}")

        aggressive_w = aggressive_center_weights(9, 9)
        b_agg, w_agg = score(pos, aggressive_w)
        print(f"Aggressive weights: Black={b_agg:.0f}, White={w_agg:.0f}\n")

    except (SGFError, InvalidPositionError) as e:
        print(f"Error: {e}\n")

    # Example 2: Handicap game
    print("Example 2: Handicap game")
    handicap_sgf = "(;SZ[9]HA[2]AB[cc][gg];W[ee];B[ge];W[ec])"

    try:
        pos = read_sgf(handicap_sgf)
        print("Final position (with handicap stones):")
        print(pos.board)
        print()

        b_count, w_count = pos.board.count_stones()
        print(f"Stone count: Black={b_count}, White={w_count}\n")

    except (SGFError, InvalidPositionError) as e:
        print(f"Error: {e}\n")

    # Example 3: Game with capture
    print("Example 3: Game with capture")
    capture_sgf = "(;SZ[5];B[bb];W[bc];B[cb];W[cc];B[ac];W[bd];B[ad];W[cd];B[ab])"

    try:
        pos = read_sgf(capture_sgf)
        print("Final position (after captures):")
        print(pos.board)
        print()

    except (SGFError, InvalidPositionError) as e:
        print(f"Error: {e}\n")

    # Example 4: Invalid position (should raise error)
    print("Example 4: Invalid position detection")
    invalid_sgf = "(;SZ[5]AB[bb]AW[ab][ba][bc][cb])"

    try:
        pos = read_sgf(invalid_sgf)
        print("This should not print!")
    except InvalidPositionError as e:
        print(f"Correctly detected invalid position: {e}\n")
    except SGFError as e:
        print(f"SGF Error: {e}\n")

    # Example 5: Read from file
    print("Example 5: Reading from file")
    try:
        pos = read_sgf_file('sample_game.sgf')
        print("Loaded sample_game.sgf:")
        print(pos.board)
        print()

        # Score the game
        center_w = center_weights(pos.board.rows, pos.board.cols)
        b_score, w_score = score(pos, center_w)
        print(f"Final score (center weights): Black={b_score:.0f}, White={w_score:.0f}")

    except FileNotFoundError:
        print("sample_game.sgf not found")
    except (SGFError, InvalidPositionError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
