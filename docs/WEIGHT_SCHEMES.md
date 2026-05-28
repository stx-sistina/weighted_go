# Weight Schemes for Weighted Go

This document describes the three weight schemes implemented for weighted Go.

## 1. Uniform Weights (Standard Go)

```python
weights = uniform_weights(rows, cols)
```

All positions have weight 1. This is equivalent to standard Go scoring.

**Example (5x5):**
```
1 1 1 1 1
1 1 1 1 1
1 1 1 1 1
1 1 1 1 1
1 1 1 1 1
```

## 2. Center Weights (Conservative)

```python
weights = center_weights(rows, cols)
```

**Formula:** `w[i][j] = 1 + min(min(i, M-1-i), min(j, N-1-j))`

Weights increase toward the center based on distance from the nearest edge. This gives a moderate advantage to central positions.

**Characteristics:**
- Corners and edges have weight 1
- Weight increases toward center
- 9x9 board: weights range from 1 to 5
- 19x19 board: weights range from 1 to 10

**Example (5x5):**
```
1 1 1 1 1
1 2 2 2 1
1 2 3 2 1
1 2 2 2 1
1 1 1 1 1
```

**Example (9x9):**
```
1 1 1 1 1 1 1 1 1
1 2 2 2 2 2 2 2 1
1 2 3 3 3 3 3 2 1
1 2 3 4 4 4 3 2 1
1 2 3 4 5 4 3 2 1
1 2 3 4 4 4 3 2 1
1 2 3 3 3 3 3 2 1
1 2 2 2 2 2 2 2 1
1 1 1 1 1 1 1 1 1
```

## 3. Aggressive Center Weights

```python
weights = aggressive_center_weights(rows, cols)
```

**Formula:** `w[i][j] = 1 + min(i, rows-1-i) + min(j, cols-1-j)`

This is the sum of (1-indexed) distances from all edges. Weights increase symmetrically toward the center and diminish when approaching any of the four corners.

**Characteristics:**
- All four corners have weight 1
- Weights are symmetric around the center
- Sum of distances from edges creates aggressive center advantage
- 5x5 board: weights range from 1 to 5
- 9x9 board: weights range from 1 to 9
- 19x19 board: center has weight 19

**Example (5x5):**
```
1 2 3 2 1
2 3 4 3 2
3 4 5 4 3
2 3 4 3 2
1 2 3 2 1
```

**Example (4x6):**
```
1 2 3 3 2 1
2 3 4 4 3 2
2 3 4 4 3 2
1 2 3 3 2 1
```

**Example (9x9):**
```
 1  2  3  4  5  4  3  2  1
 2  3  4  5  6  5  4  3  2
 3  4  5  6  7  6  5  4  3
 4  5  6  7  8  7  6  5  4
 5  6  7  8  9  8  7  6  5
 4  5  6  7  8  7  6  5  4
 3  4  5  6  7  6  5  4  3
 2  3  4  5  6  5  4  3  2
 1  2  3  4  5  4  3  2  1
```

**Key positions for 19x19:**
- All corners (0,0), (0,18), (18,0), (18,18): weight = 1
- (1,1): weight = 3
- Center (9,9): weight = 19

## Comparison

For a 9x9 board with stones at:
- Black at (4,4) - center
- White at (0,0) - corner
- Black at (2,6) - off-center
- White at (8,8) - opposite corner

**Scores:**
- Uniform weights: Black = 2, White = 2
- Center weights: Black = 8, White = 2
- Aggressive weights: Black = 14, White = 2

**Weight values at these positions:**

| Position | Uniform | Center | Aggressive |
|----------|---------|--------|------------|
| (4,4)    | 1       | 5      | 9          |
| (0,0)    | 1       | 1      | 1          |
| (2,6)    | 1       | 3      | 5          |
| (8,8)    | 1       | 1      | 1          |

## Non-Square Boards

All three weight schemes work on non-square boards.

**Example (5x9) with aggressive weights:**
```
1 2 3 4 5 4 3 2 1
2 3 4 5 6 5 4 3 2
3 4 5 6 7 6 5 4 3
2 3 4 5 6 5 4 3 2
1 2 3 4 5 4 3 2 1
```

For both center and aggressive weights on non-square boards, the weight is limited by the shorter dimension, creating symmetric patterns.

## Usage

```python
from weighted_go import (
    GamePosition, Stone,
    uniform_weights, center_weights, aggressive_center_weights,
    score
)

# Create game
pos = GamePosition(9, 9)
pos.place_stone((4, 4), Stone.BLACK)

# Score with different schemes
black, white = score(pos, uniform_weights(9, 9))
black, white = score(pos, center_weights(9, 9))
black, white = score(pos, aggressive_center_weights(9, 9))
```

## Design Philosophy

- **Uniform**: Standard Go - all positions equal
- **Center**: Conservative center advantage - symmetric, bounded growth
- **Aggressive**: Strong center advantage - unbounded diagonal growth, heavily rewards central and off-diagonal positions
