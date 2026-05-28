# Area Scoring in Weighted Go

Weighted Go implements Chinese-style area scoring with a key invariant: **Black_score + White_score = Total board weight**.

This document explains the scoring algorithm and how it extends to weighted boards.

## Scoring Fundamentals

### Standard Go (Uniform Weights)

In standard Chinese rules with uniform weights (all positions weight 1.0):

1. **Stones count as territory** for the player who placed them
2. **Empty regions** belong to the player who surrounds them
3. **Contested regions** (touching both colors) are split equally
4. **Total score** = Occupied points + Controlled empty points

**Invariant**: Every point on the board belongs to Black, White, or is split 50-50.

**Example on 19×19**:
- Black controls 180.0 points
- White controls 181.0 points
- Total: 361.0 (= 19 × 19)

### Weighted Go Extension

With custom weights, the same principles apply but each position contributes its weight:

1. **Black stones** contribute their position weight to Black's score
2. **White stones** contribute their position weight to White's score
3. **Black territory** (empty, surrounded by Black) contributes to Black
4. **White territory** (empty, surrounded by White) contributes to White
5. **Contested territory** (touching both colors) splits its weight 50-50

**Invariant**: `Black_score + White_score = sum(all_weights)`

**Example on 19×19 with Center: Square weights**:
- Total weight: 1,330
- Black controls 607.0 points
- White controls 723.0 points
- Sum: 1,330.0 ✓

## Territory Detection Algorithm

Territory is determined via flood-fill:

1. **Start** from an empty position
2. **Expand** to all connected empty positions (via neighbors)
3. **Track borders**: Record all stone colors touching this region
4. **Classify**:
   - If only Black stones touch → **Black territory**
   - If only White stones touch → **White territory**
   - If both colors touch → **Contested territory**

### Flood-Fill Implementation

```python
def find_territory(board, start_pos):
    """
    Find territory starting from an empty position.
    
    Returns:
        (positions, owner) where:
        - positions: set of (row, col) tuples in this region
        - owner: Stone.BLACK, Stone.WHITE, or Stone.EMPTY (contested)
    """
    if board.get(start_pos) != Stone.EMPTY:
        return (set(), Stone.EMPTY)
    
    # Flood fill to find all connected empty positions
    territory = set()
    to_visit = [start_pos]
    border_colors = set()
    
    while to_visit:
        pos = to_visit.pop()
        if pos in territory:
            continue
        
        stone = board.get(pos)
        if stone == Stone.EMPTY:
            territory.add(pos)
            for neighbor in board.get_neighbors(pos):
                if neighbor not in territory:
                    to_visit.append(neighbor)
        else:
            # Hit a stone - record its color
            border_colors.add(stone)
    
    # Determine ownership
    if len(border_colors) == 0:
        owner = Stone.EMPTY  # Isolated (shouldn't happen in practice)
    elif len(border_colors) == 1:
        owner = border_colors.pop()  # Single color = that player's territory
    else:
        owner = Stone.EMPTY  # Both colors = contested
    
    return (territory, owner)
```

### Territory Matrix

The scoring function builds a full territory matrix by calling `find_territory()` for each empty region:

```python
# Initialize territory matrix (all empty initially)
territory = [[Stone.EMPTY for _ in range(cols)] for _ in range(rows)]

# Mark stones
for i in range(rows):
    for j in range(cols):
        stone = board.get((i, j))
        if stone != Stone.EMPTY:
            territory[i][j] = stone

# Find empty territories
visited = set()
for i in range(rows):
    for j in range(cols):
        if board.get((i, j)) == Stone.EMPTY and (i, j) not in visited:
            positions, owner = find_territory(board, (i, j))
            visited.update(positions)
            for pos in positions:
                territory[pos[0]][pos[1]] = owner
```

## Scoring Calculation

Once the territory matrix is built, scoring is straightforward:

```python
def score(position, weights):
    """Calculate area scores with weights."""
    # Build territory matrix
    territory = build_territory_matrix(position)
    
    black_score = 0.0
    white_score = 0.0
    
    for i in range(rows):
        for j in range(cols):
            weight = weights[i][j]
            owner = territory[i][j]
            
            if owner == Stone.BLACK:
                black_score += weight
            elif owner == Stone.WHITE:
                white_score += weight
            elif owner == Stone.EMPTY:
                # Contested - split 50-50
                black_score += weight / 2
                white_score += weight / 2
    
    return (black_score, white_score)
```

## Contested Territory

Contested territory occurs when an empty region touches both Black and White stones.

**Example (uniform weights)**:
```
● ● ○ ○
● . . ○
● ● ○ ○
```

The two center points (`.`) touch both colors → contested.
- Each point has weight 1.0
- Black gets: 6 stones + 1.0 contested = 7.0
- White gets: 6 stones + 1.0 contested = 7.0
- Total: 14.0 = 7.0 + 7.0 ✓

**With weights** (e.g., center point weight = 5.0):
```
Weight matrix:        Territory:
1 1 1 1               ● ● ○ ○
1 5 5 1               ● ⬕ ⬕ ○
1 1 1 1               ● ● ○ ○
```

- Black: 6×1 + 2×2.5 = 11.0
- White: 6×1 + 2×2.5 = 11.0
- Total: 22.0 = 11.0 + 11.0 ✓

## Dead Stones

In the GUI, users can mark groups as dead. The scoring function treats dead stones as if they were removed:

```python
def score_with_dead_stones(position, weights, dead_stones):
    """Calculate scores with dead stones marked."""
    # Create modified board with dead stones removed
    modified_board = position.board.copy()
    for pos in dead_stones:
        modified_board.set(pos, Stone.EMPTY)
    
    # Create temporary position with modified board
    temp_position = GamePosition(rows, cols)
    temp_position.board = modified_board
    
    # Score normally
    return score(temp_position, weights)
```

Dead stones contribute to the opponent's score:
- Dead Black stones → removed → White controls that territory
- Dead White stones → removed → Black controls that territory

## Edge Cases

### 1. Fully Occupied Board

If the board is completely filled with stones and no empty territory exists:
- Black score = sum of weights at Black stone positions
- White score = sum of weights at White stone positions
- No contested territory possible

### 2. Empty Board

If the board is completely empty:
- All positions are contested (touching neither color)
- Black score = Total weight / 2
- White score = Total weight / 2

### 3. Single Color

If only one color has stones:
- That color owns all empty territory
- Opponent score = 0.0
- Winner score = Total weight

### 4. Non-Square Boards

The algorithm works identically on non-square boards (e.g., 13×9):
- Neighbors are found correctly via board boundaries
- Territory detection respects actual board shape
- Total weight = sum of all position weights

## Scoring Invariant Proof

**Claim**: For any position and any weight scheme, `Black_score + White_score = Total_weight`.

**Proof**:

Every position `(i, j)` with weight `w[i][j]` falls into exactly one category:

1. **Black stone**: Contributes `w[i][j]` to Black score
2. **White stone**: Contributes `w[i][j]` to White score
3. **Black territory**: Contributes `w[i][j]` to Black score
4. **White territory**: Contributes `w[i][j]` to White score
5. **Contested**: Contributes `w[i][j]/2` to Black, `w[i][j]/2` to White

In all cases, the position contributes exactly `w[i][j]` total across both players.

Therefore:
```
Black_score + White_score 
  = sum over all (i,j) of contribution to both players
  = sum over all (i,j) of w[i][j]
  = Total_weight
```

QED ∎

## Comparison with Territory Scoring

Traditional Japanese territory scoring counts:
- Empty points in your territory
- Captured stones

Key differences:
1. **Stones don't count** in territory scoring
2. **Captures matter** in territory scoring
3. **Komi adjustment** typically differs

Chinese area scoring (which Weighted Go extends):
- **Stones count** as territory
- **Captures don't affect score** (already removed from board)
- **Komi adjustment** typically 7.5 in standard Go

Weighted Go maintains area scoring principles but allows non-uniform position values.

## Examples

### Example 1: Simple Game (Uniform Weights, 9×9)

```
Final position:
  A B C D E F G H J
1 ● ● ● ○ ○ ○ . . .
2 ● . ● ○ . ○ . . .
3 ● ● ● ○ ○ ○ . . .
4 . . . . . . . . .
5 . . . . . . . . .
6 . . . . . . . . .
7 . . . . . . . . .
8 . . . . . . . . .
9 . . . . . . . . .

Territory analysis:
- Black stones: 8 points (weight 1 each) = 8.0
- Black territory: 1 point (B2) = 1.0
- White stones: 8 points (weight 1 each) = 8.0
- White territory: 1 point (E2) = 1.0
- Contested: 63 empty points = 31.5 each

Scores:
- Black: 8.0 + 1.0 + 31.5 = 40.5
- White: 8.0 + 1.0 + 31.5 = 40.5
- Total: 81.0 (= 9×9) ✓
- Result: Tie
```

### Example 2: Weighted Game (Center: Diamond, 9×9)

Same position, but with Center: Diamond weights where center (E5) = 9.0.

Contested region includes high-value center positions, so:
- Black: 8 stones + 1 territory + contested share ≈ 80.0
- White: 8 stones + 1 territory + contested share ≈ 80.0
- Total: 160.0 (total weight for 9×9 with Center: Diamond) ✓

The center's higher weight makes contested regions more valuable.

## Implementation Notes

1. **Efficiency**: Territory detection is O(n) where n = board positions
   - Each position visited at most once via flood-fill
   - Total scoring: O(n) for territory + O(n) for summation

2. **Accuracy**: All scores use floating-point arithmetic
   - Ensures precise 50-50 splits for contested territory
   - Maintains invariant even with fractional weights

3. **Non-square boards**: Algorithm naturally handles rectangular boards
   - Neighbor finding respects actual board dimensions
   - No special cases needed

4. **GUI integration**: Territory is recalculated when dead stones change
   - Allows interactive scoring adjustments
   - Updates scores in real-time

## See Also

- [weights.md](weights.md) - Weight scheme details
- [CLAUDE.md](../CLAUDE.md) - Implementation architecture
- [README.md](../README.md) - Quick start guide
