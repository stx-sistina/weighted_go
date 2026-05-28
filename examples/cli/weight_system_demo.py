"""
Demonstration of the Weight system.

Shows how to use the new Weight classes and create custom weight schemes.
"""

from weighted_go import (
    UniformWeight,
    CenterSquareWeight,
    CenterDiamondWeight,
    BoardSize,
    FunctionWeight,
    MatrixWeight,
    STANDARD_WEIGHTS,
    get_weight_by_name,
    list_weights,
)


def main():
    print("=" * 70)
    print("Weight System Demonstration".center(70))
    print("=" * 70)
    print()

    # Standard board sizes
    board_19 = BoardSize(19, 19)
    board_13 = BoardSize(13, 13)
    board_9 = BoardSize(9, 9)

    # Board size parsing
    print("1. Board Size Handling")
    print(f"   19x19 board: {board_19}")
    print(f"   Parsed '13': {BoardSize.from_string('13')}")
    print(f"   Parsed '9x9': {BoardSize.from_string('9x9')}")
    print(f"   Parsed '13:19': {BoardSize.from_string('13:19')}")
    print()

    # Standard weights
    print("2. Standard Weight Schemes")
    uniform = UniformWeight()
    center_sq = CenterSquareWeight()
    center_dia = CenterDiamondWeight()

    for weight in [uniform, center_sq, center_dia]:
        total = weight.total_weight(board_19)
        center_weight = weight.get_weight(9, 9, board_19)  # Center (tengen)
        corner_weight = weight.get_weight(0, 0, board_19)  # Corner
        print(f"   {weight.name}:")
        print(f"      Total: {total:.0f}")
        print(f"      Center (tengen): {center_weight:.1f}")
        print(f"      Corner: {corner_weight:.1f}")

    print()

    # Registry access
    print("3. Weight Registry")
    print(f"   Available weights: {list(STANDARD_WEIGHTS.keys())}")
    w = get_weight_by_name('center_square')
    print(f"   Retrieved 'center_square': {w.name}")
    print()

    # Custom function weight
    print("4. Custom Weight Function")

    def edge_weight_func(row, col, board_size):
        """Weight edges more heavily than center."""
        dist_to_edge = min(row, col, board_size.rows - 1 - row, board_size.cols - 1 - col)
        return 10.0 - dist_to_edge  # Higher on edges

    edge_weight = FunctionWeight(
        name="Edge Emphasis",
        func=edge_weight_func,
        description="Weights edges more heavily"
    )

    print(f"   {edge_weight.name}: {edge_weight.description}")
    print(f"   Corner weight: {edge_weight.get_weight(0, 0, board_9)}")
    print(f"   Center weight: {edge_weight.get_weight(4, 4, board_9)}")
    print(f"   Total weight (9x9): {edge_weight.total_weight(board_9):.0f}")
    print()

    # Custom matrix weight
    print("5. Custom Matrix Weight (Small Board)")
    custom_matrix = [
        [1.0, 1.0, 1.0],
        [1.0, 5.0, 1.0],  # Center worth 5x
        [1.0, 1.0, 1.0],
    ]
    matrix_weight = MatrixWeight(
        name="Custom 3x3",
        matrix=custom_matrix,
        description="Hand-crafted 3x3 board weights"
    )
    board_3 = BoardSize(3, 3)
    print(f"   {matrix_weight.name}")
    print(f"   Total weight: {matrix_weight.total_weight(board_3)}")
    print("   Weight matrix:")
    for row in custom_matrix:
        print(f"      {row}")
    print()

    # Weight as matrix vs function
    print("6. Interfacing with Scoring")
    print("   Weights can be used in two ways:")
    print()
    print("   a) As a matrix (2D list):")
    matrix = uniform.as_matrix(board_9)
    print(f"      matrix = uniform.as_matrix(board_9)")
    print(f"      black_score, white_score = score(pos, matrix)")
    print()
    print("   b) As a function:")
    print(f"      weight_func = uniform.as_function(board_9)")
    print(f"      black_score, white_score = score(pos, weight_func)")
    print()

    # Display 5x5 weight pattern
    print("7. Visual Weight Pattern (5x5 Center: Square)")
    board_5 = BoardSize(5, 5)
    csw_5 = CenterSquareWeight()
    print()
    for row in range(5):
        weights_row = [csw_5.get_weight(row, col, board_5) for col in range(5)]
        print("   " + "  ".join(f"{w:.0f}" for w in weights_row))
    print()

    print("=" * 70)
    print("For more details, see:")
    print("  - weighted_go/core/weight.py (Weight abstraction)")
    print("  - weighted_go/commons/weights.py (Standard implementations)")
    print("=" * 70)


if __name__ == "__main__":
    main()
