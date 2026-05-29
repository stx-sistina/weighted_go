# Weighted Go

A Go variant where each board intersection has a configurable weight. Implements area scoring that extends the Chinese rule.

**This package provides tools for analyzing and scoring Go games with custom weight schemes. It does not offer gameplay.**

## Usage

Launch the GUI:
```bash
./scripts/run_gui.sh
# or
python -m weighted_go.gui.run_gui
```

### Features
- **Load SGF files** with metadata (player names, ranks, komi, result)
- **Position editing**:
  - Four editing modes: Alternating (validated), Black, White, Erase
  - Board size management (1-25, supports non-square boards)
  - Clear board and revert changes
- **Dead stone marking**: Click to mark/unmark groups
- **Weight schemes**: Uniform, Center: Square, Center: Diamond (see [docs/weights.md](docs/weights.md))
- **Display modes**: Stones Only, Territory Markers, Weight Heatmap
- **Live scoring** with automatic territory calculation

## Weight Schemes

The package includes three standard weight schemes:
- **Uniform (Standard)**: All positions weight 1.0 (standard Go)
- **Center: Square**: Moderate center bias with concentric square pattern
- **Center: Diamond**: Strong center bias with concentric diamond pattern

See [docs/weights.md](docs/weights.md) for formulas, visualizations, and examples.

## Documentation

- [docs/weights.md](docs/weights.md) - Weight scheme details and formulas
- [CLAUDE.md](CLAUDE.md) - Development guide and architecture
- [docs/AREA_SCORING.md](docs/AREA_SCORING.md) - Scoring algorithm details

## Contributing

**Coming Soon** - See [CONTRIBUTING.md](CONTRIBUTING.md)

---

<details>
<summary><h2>Advanced</h2></summary>

### CLI Tools

Analyze a game from SGF:
```bash
./scripts/run_cli.sh data/game.sgf
# or
python -m weighted_go.cli.analyze_game data/game.sgf

# Show detailed board state
./scripts/run_cli.sh data/game.sgf --full
```

Example output:
```
Scoring Results (Area Scoring)
│ Weighting Scheme     │  Black   │   White  │    Result    │  Total  │
├──────────────────────┼──────────┼──────────┼──────────────┼─────────┤
│ Uniform (Standard)   │    164.0 │     197.0 │      W+33.0  │    361  │
│ Center: Square       │    607.0 │     723.0 │     W+116.0  │   1330  │
│ Center: Diamond      │   1627.5 │    1811.5 │     W+184.0  │   3439  │
```

### Use as a Package

#### Installation
```bash
pip install -e .
```

#### Basic Usage

```python
from weighted_go import (
    GamePosition, Stone, BoardSize,
    UniformWeight, CenterSquareWeight, CenterDiamondWeight,
    score, read_sgf_file, print_board_with_territory
)

# Load a game
position, last_move = read_sgf_file("game.sgf")

# Display the board
print_board_with_territory(position)

# Score with different weights
board = BoardSize(19, 19)
weights = CenterSquareWeight().as_matrix(board)
black_score, white_score = score(position, weights)
print(f"Black: {black_score}, White: {white_score}")
```

#### Custom Weights

```python
from weighted_go import FunctionWeight, BoardSize, score

def edge_emphasis(row, col, board_size):
    """Weight edges more than center."""
    dist = min(row, col, board_size.rows-1-row, board_size.cols-1-col)
    return 10.0 - dist

custom = FunctionWeight("Edge Emphasis", edge_emphasis)
weights = custom.as_matrix(BoardSize(19, 19))
black_score, white_score = score(position, weights)
```

### Testing

```bash
# All tests (71 total)
pytest tests/ -v

# Specific modules
pytest tests/test_core.py -v        # 47 tests
pytest tests/test_sgf_reader.py -v  # 24 tests
```

</details>
