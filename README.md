# Weighted Go

A Go variant where each intersection on the board has a configurable weight. Regular Go corresponds to `w_ij = 1` for all positions.

**Visualization**: The board displays with Unicode symbols:
- ● Black stones  ○ White stones
- ■ Black territory  □ White territory  ⬕ Contested

## Features

- **Area Scoring**: Chinese-style scoring where Black + White = total board weight
- **Multiple Weight Schemes**: Uniform, center-weighted (square/diamond patterns)
- **SGF Support**: Read and analyze real Go games from SGF files
- **GUI Application**: Tkinter-based GUI with dead stone marking, territory visualization, and weight heatmaps
- **CLI Tools**: Command-line game analysis
- **Non-square Boards**: Full support for rectangular boards
- **Capture Logic**: Automatic capture, suicide prevention, position validation
- **Beautiful Visualization**: Unicode symbols and ANSI colors for terminal display

## Quick Start

### Installation

```bash
# Install the package
pip install -e .

# Or with development dependencies
pip install -e . -r requirements-dev.txt
```

### GUI Application

```bash
./run_gui.sh
```

Features:
- Load SGF files with game metadata
- Click to mark dead stone groups
- Live territory and score updates
- Three weight schemes: Uniform, Center: Square, Center: Diamond
- Display modes: Stones Only, Territory Markers, Weight Heatmap

### Analyze a Game (CLI)

```bash
./run_cli.sh data/[2137HLE]vs[sistina喵]1779897572030032210.sgf
```

Example output:
```
Final Position (with territory markers):
  ● Black stones  ○ White stones
  ■ Black territory  □ White territory  ⬕ Contested

Scoring Results (Area Scoring)
│ Weighting Scheme     │  Black   │   White  │    Result    │  Total  │
├──────────────────────┼──────────┼───────────┼─────────────┼────────┤
│ Uniform (Standard)   │    164.0 │     197.0 │      W+33.0  │    361  │
│ Center: Square       │    607.0 │     723.0 │     W+116.0  │   1330  │
│ Center: Diamond      │   1627.5 │    1811.5 │     W+184.0  │   3439  │
```

### As a Library

```python
from weighted_go import (
    GamePosition, Stone,
    score, center_weights, aggressive_center_weights
)
from weighted_go.sgf_reader import read_sgf_file
from weighted_go.visualization import print_board_with_territory

# Load a game
pos = read_sgf_file("game.sgf")

# Display the board
print_board_with_territory(pos)

# Score with center weights
weights = center_weights(19, 19)
black_score, white_score = score(pos, weights)
print(f"Black: {black_score}, White: {white_score}")
```

## Core Components

### weighted_go.core
- `Board`: Board state management
- `GamePosition`: Game state with move validation and captures
- `Stone`: Enum for Black, White, Empty
- Weight functions: `uniform_weights()`, `center_weights()`, `aggressive_center_weights()`
- `score()`: Area scoring ensuring Black + White = total board weight
- `find_territory()`: Territory detection via flood-fill

### weighted_go.sgf_reader
- `read_sgf()`: Parse SGF strings
- `read_sgf_file()`: Load from file
- Handles handicap stones (AB/AW properties)
- Validates final positions

### weighted_go.visualization
- `print_board_with_territory()`: Display board with territory markers
- `get_board_string()`: Get string representation
- Unicode symbols: ● ○ ■ □ ⬕
- Standard Go convention: Column labels skip 'I' (A-H, J-T)

## Weight Schemes

### Uniform Weights
All positions have weight 1 (standard Go):
```python
weights = uniform_weights(19, 19)
```

### Center Weights
Moderate rewards for central positions:
```python
weights = center_weights(19, 19)
```
Formula: `w[i][j] = 1 + min(dist_from_top/bottom, dist_from_left/right)`

### Aggressive Center Weights
Strong rewards for positions far from all corners:
```python
weights = aggressive_center_weights(19, 19)
```
Formula: `w[i][j] = 1 + min(i, rows-1-i) + min(j, cols-1-j)`

### Custom Weights
Define your own weight function:
```python
def custom_weight(pos):
    i, j = pos
    return i + j + 1

black_score, white_score = score(game_pos, custom_weight)
```

## Testing

Run all tests (71 total):
```bash
pytest tests/ -v
```

Run specific test modules:
```bash
pytest tests/test_core.py -v        # 47 tests
pytest tests/test_sgf_reader.py -v  # 24 tests
```

## Examples

```bash
# Basic usage examples
PYTHONPATH=. python examples/cli/basic_usage.py

# SGF reading examples
PYTHONPATH=. python examples/cli/sgf_usage.py

# Color/ANSI demonstration
PYTHONPATH=. python examples/cli/color_demo.py

# Analyze real games with detailed output
./run_cli.sh data/game.sgf --full
```

## Area Scoring

Weighted Go uses **Chinese-style area scoring** where every point on the board belongs to Black, White, or is shared (contested territory split 50-50).

This ensures: **Black_score + White_score = Total board weight**

For a 19×19 board:
- Uniform weights: 361 total
- Center weights: 1,330 total
- Aggressive weights: 3,439 total

See [docs/AREA_SCORING.md](docs/AREA_SCORING.md) for details.

## Implementation Details

- Groups detected via depth-first search
- Automatic capture when groups lose all liberties
- Suicide prevention (unless it captures opponent stones)
- Territory detection via flood-fill algorithm
- Contested territory (touching both colors) split 50-50
- SGF parser handles main path only, supports handicap stones
- Position validation ensures all groups have ≥1 liberty

## Project Structure

```
weighted_go/
├── weighted_go/          # Main package
│   ├── core/             # Core game logic
│   ├── commons/          # Shared resources (symbols, colors)
│   ├── cli/              # CLI tools
│   └── gui/              # GUI application
├── tests/                # Test suite (71 tests)
├── examples/             # Example scripts
│   ├── cli/              # CLI examples
│   └── gui/              # GUI examples
├── docs/                 # Documentation
├── data/                 # Sample SGF files
├── run_cli.sh            # CLI launcher script
└── run_gui.sh            # GUI launcher script
```

See [CLAUDE.md](CLAUDE.md) for detailed architecture and development guidance.

## Documentation

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Project organization
- [docs/AREA_SCORING.md](docs/AREA_SCORING.md) - Area scoring explanation
- [docs/WEIGHT_SCHEMES.md](docs/WEIGHT_SCHEMES.md) - Weight scheme details
- [docs/GAME_ANALYSIS.md](docs/GAME_ANALYSIS.md) - Real game analysis
