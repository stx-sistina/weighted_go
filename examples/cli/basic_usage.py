"""
Example usage of the weighted_go module.
"""

from weighted_go import (
    Stone, GamePosition,
    uniform_weights, center_weights, aggressive_center_weights,
    score, score_with_territory,
    is_valid_position
)


def print_board(pos: GamePosition, title: str = ""):
    """Print the board with a title."""
    if title:
        print(f"\n{title}")
    print(pos.board)
    print()


def main():
    print("=== Weighted Go Example ===\n")

    # Create a 9x9 board
    pos = GamePosition(9, 9)

    # Play some moves
    moves = [
        ((2, 2), Stone.BLACK),
        ((2, 6), Stone.WHITE),
        ((3, 3), Stone.BLACK),
        ((3, 5), Stone.WHITE),
        ((4, 4), Stone.BLACK),
        ((4, 4), Stone.WHITE),  # Should fail - occupied
        ((6, 6), Stone.WHITE),
        ((6, 2), Stone.BLACK),
    ]

    for pos_move, stone in moves:
        if pos.place_stone(pos_move, stone):
            print(f"Placed {stone} at {pos_move}")
        else:
            print(f"Failed to place {stone} at {pos_move}")

    print_board(pos, "Current board:")

    # Calculate scores with uniform weights
    print("=== Scoring with Uniform Weights ===")
    weights_uniform = uniform_weights(9, 9)
    black_score, white_score = score(pos, weights_uniform)
    print(f"Black: {black_score:.1f}, White: {white_score:.1f}\n")

    # Calculate scores with center-weighted board
    print("=== Scoring with Center Weights ===")
    weights_center = center_weights(9, 9)
    black_score, white_score = score(pos, weights_center)
    print(f"Black: {black_score:.1f}, White: {white_score:.1f}\n")

    # Print the weight matrix for visualization
    print("Center weight matrix (9x9):")
    for row in weights_center:
        print(" ".join(f"{w:2.0f}" for w in row))
    print()

    # Calculate scores with aggressive center weights
    print("=== Scoring with Aggressive Center Weights ===")
    weights_aggressive = aggressive_center_weights(9, 9)
    black_score, white_score = score(pos, weights_aggressive)
    print(f"Black: {black_score:.1f}, White: {white_score:.1f}\n")

    # Print the aggressive weight matrix for visualization
    print("Aggressive center weight matrix (9x9):")
    for row in weights_aggressive:
        print(" ".join(f"{w:2.0f}" for w in row))
    print()

    # Score with territory
    print("=== Scoring with Territory (Uniform Weights) ===")
    black_score, white_score = score_with_territory(pos, weights_uniform)
    print(f"Black: {black_score:.1f}, White: {white_score:.1f}\n")

    # Demonstrate capture
    print("=== Capture Example ===")
    capture_pos = GamePosition(5, 5)
    capture_pos.board.set((2, 2), Stone.WHITE)
    capture_pos.board.set((1, 2), Stone.BLACK)
    capture_pos.board.set((3, 2), Stone.BLACK)
    capture_pos.board.set((2, 1), Stone.BLACK)

    print_board(capture_pos, "Before capture:")

    capture_pos.place_stone((2, 3), Stone.BLACK)

    print_board(capture_pos, "After capture (White stone at (2,2) should be removed):")

    # Custom weight function example
    print("=== Custom Weight Function ===")
    pos_custom = GamePosition(5, 5)
    pos_custom.place_stone((0, 0), Stone.BLACK)
    pos_custom.place_stone((2, 2), Stone.WHITE)
    pos_custom.place_stone((4, 4), Stone.BLACK)

    # Weight = distance from (0,0)
    def distance_weight(p):
        return (p[0]**2 + p[1]**2) ** 0.5

    black_score, white_score = score(pos_custom, distance_weight)
    print_board(pos_custom, "Board:")
    print(f"Using weight = distance from (0,0):")
    print(f"Black: {black_score:.2f}, White: {white_score:.2f}")
    print(f"  (0,0) has weight {distance_weight((0, 0)):.2f}")
    print(f"  (2,2) has weight {distance_weight((2, 2)):.2f}")
    print(f"  (4,4) has weight {distance_weight((4, 4)):.2f}")

    # Demonstrate validation
    print("\n=== Position Validation ===")
    print(f"Current position is valid: {is_valid_position(pos)}")

    # Create an invalid position manually (for demonstration only)
    invalid_pos = GamePosition(5, 5)
    invalid_pos.board.set((2, 2), Stone.WHITE)
    invalid_pos.board.set((1, 2), Stone.BLACK)
    invalid_pos.board.set((3, 2), Stone.BLACK)
    invalid_pos.board.set((2, 1), Stone.BLACK)
    invalid_pos.board.set((2, 3), Stone.BLACK)

    print_board(invalid_pos, "Invalid position (white stone has no liberties):")
    print(f"This position is valid: {is_valid_position(invalid_pos)}")
    print("Note: place_stone() will never create such invalid positions")

    # Non-square board example
    print("\n=== Non-Square Board Example (5x9) ===")
    rect_pos = GamePosition(5, 9)
    rect_pos.place_stone((0, 0), Stone.BLACK)
    rect_pos.place_stone((4, 8), Stone.WHITE)
    rect_pos.place_stone((2, 4), Stone.BLACK)
    rect_pos.place_stone((1, 6), Stone.WHITE)

    print_board(rect_pos, "5x9 Board:")

    # Score with different weights
    uniform_rect = uniform_weights(5, 9)
    black_score, white_score = score(rect_pos, uniform_rect)
    print(f"Uniform weights - Black: {black_score:.1f}, White: {white_score:.1f}")

    aggressive_rect = aggressive_center_weights(5, 9)
    black_score, white_score = score(rect_pos, aggressive_rect)
    print(f"Aggressive weights - Black: {black_score:.1f}, White: {white_score:.1f}")

    print("\nAggressive weights for 5x9 board:")
    for row in aggressive_rect:
        print(" ".join(f"{w:2.0f}" for w in row))


if __name__ == "__main__":
    main()
