# Weight Schemes

Weighted Go allows each board intersection to have a configurable weight. This document describes the standard weight schemes included with the package.

## Standard Weights

### Uniform (Standard)

**Description**: Standard Go with all positions having weight 1.0.

**Formula**: `w[i][j] = 1.0`

**Total weight on 19×19**: 361

**Pattern**: Flat uniform grid.

**Use case**: Standard Go scoring, baseline for comparison.

**Example (9×9)**:
```
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
1 1 1 1 1 1 1 1 1
```

---

### Center: Square

**Description**: Moderate center bias using concentric square pattern.

**Formula**: `w[i][j] = 1 + min(dist_from_row_edge, dist_from_col_edge)`

where:
- `dist_from_row_edge = min(row, rows - 1 - row)`
- `dist_from_col_edge = min(col, cols - 1 - col)`

**Total weight on 19×19**: 1,330

**Pattern**: Concentric squares with weight increasing toward center.

**Use case**: Games where central control is important but not dominant.

**Example (9×9)**:
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

**19×19 characteristics**:
- Corner (0,0): weight = 1
- Edge center (0,9): weight = 1
- Tengen (9,9): weight = 10
- Maximum weight: 10 (center point on 19×19)

---

### Center: Diamond

**Description**: Strong center bias using concentric diamond pattern.

**Formula**: `w[i][j] = 1 + dist_from_row_edge + dist_from_col_edge`

where:
- `dist_from_row_edge = min(row, rows - 1 - row)`
- `dist_from_col_edge = min(col, cols - 1 - col)`

**Total weight on 19×19**: 3,439

**Pattern**: Concentric diamonds with aggressive center weighting.

**Use case**: Games where central territory is highly valuable.

**Example (9×9)**:
```
1 2 3 4 5 4 3 2 1
2 3 4 5 6 5 4 3 2
3 4 5 6 7 6 5 4 3
4 5 6 7 8 7 6 5 4
5 6 7 8 9 8 7 6 5
4 5 6 7 8 7 6 5 4
3 4 5 6 7 6 5 4 3
2 3 4 5 6 5 4 3 2
1 2 3 4 5 4 3 2 1
```

**19×19 characteristics**:
- Corner (0,0): weight = 1
- Edge center (0,9): weight = 10
- Tengen (9,9): weight = 19
- Maximum weight: 19 (center point on 19×19)

---

## Using Weight Schemes

### In Python

```python
from weighted_go import (
    UniformWeight,
    CenterSquareWeight,
    CenterDiamondWeight,
    BoardSize,
    score,
)

# Create weight instances
uniform = UniformWeight()
center_sq = CenterSquareWeight()
center_dia = CenterDiamondWeight()

# Get weight matrix for scoring
board = BoardSize(19, 19)
weights = center_sq.as_matrix(board)

# Score a position
black_score, white_score = score(position, weights)
```

### In GUI

Select from the **Weight Scheme** radio buttons:
- Uniform (Standard)
- Center: Square
- Center: Diamond

Scores update automatically when you mark dead stones or change the weight scheme.

### In CLI

All three schemes are displayed automatically:

```bash
./run_cli.sh data/game.sgf
```

Output shows scoring under all three schemes for comparison.

---

## Custom Weight Schemes

You can create custom weight schemes using `FunctionWeight` or `MatrixWeight`:

### Using FunctionWeight

```python
from weighted_go import FunctionWeight, BoardSize

def custom_weight(row, col, board_size):
    """Your custom formula here."""
    # Example: linear gradient from top to bottom
    return 1.0 + row

custom = FunctionWeight("Top to Bottom", custom_weight)
weights = custom.as_matrix(BoardSize(19, 19))
```

### Using MatrixWeight

```python
from weighted_go import MatrixWeight
import numpy as np

# Create custom weight matrix
matrix = np.random.rand(19, 19) * 10  # Random weights 0-10
custom = MatrixWeight("Random", matrix)

# Use directly
black_score, white_score = score(position, matrix)
```

---

## Weight System Architecture

The weight system has three layers:

1. **Board dimensions** (`BoardSize`): Represents board size (rows, cols)
2. **Weight abstraction** (`Weight` base class): Interface for all weight schemes
3. **Standard weights** (`UniformWeight`, `CenterSquareWeight`, `CenterDiamondWeight`)

All weight schemes implement:
- `get_weight(row, col, board_size)`: Get weight at a specific position
- `as_matrix(board_size)`: Generate full weight matrix for scoring
- `as_function()`: Convert to callable function
- `total_weight(board_size)`: Calculate total board weight

---

## Scoring Invariant

All weight schemes maintain the invariant:

**Black_score + White_score = Total board weight**

This ensures that every point on the board is accounted for:
- Stones count as territory for the player who placed them
- Empty points belong to Black, White, or are contested
- Contested territory (touching both colors) is split 50-50

See [AREA_SCORING.md](AREA_SCORING.md) for details on the scoring algorithm.
