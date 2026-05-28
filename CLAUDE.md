# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Weighted Go is a Go variant where each board intersection has a configurable weight (regular Go has uniform weights w_ij = 1). The project implements Chinese-style area scoring where **Black_score + White_score = Total board weight**.

This is a Python package (`weighted_go`) with CLI tools, examples, tests, and a Tkinter GUI for game analysis.

## Development Commands

### Installation
```bash
pip install -e .
pip install -e ".[dev]"  # With dev dependencies
```

### Testing
```bash
# Run all tests (71 total)
pytest tests/ -v

# Specific test modules
pytest tests/test_core.py -v        # 47 core tests
pytest tests/test_sgf_reader.py -v  # 24 SGF tests
```

### Running the Application
```bash
# Analyze an SGF file (CLI)
./run_cli.sh data/[game_file].sgf
./run_cli.sh data/[game_file].sgf --full  # Show detailed boards
# Or directly:
python -m weighted_go.cli.analyze_game data/[game_file].sgf

# Launch GUI
./run_gui.sh
# Or directly:
python -m weighted_go.gui.run_gui

# Run examples
PYTHONPATH=. python examples/cli/basic_usage.py
PYTHONPATH=. python examples/cli/sgf_usage.py
PYTHONPATH=. python examples/cli/color_demo.py
PYTHONPATH=. python examples/cli/weight_system_demo.py
```

## Architecture

### Core Components

**[weighted_go/core/](weighted_go/core/)** - Core game logic module
- **[core.py](weighted_go/core/core.py)**: Game logic foundation
  - `Stone` (Enum): BLACK, WHITE, EMPTY with `opponent()` method
  - `Board`: Grid state, neighbor finding, stone placement/removal
  - `GamePosition`: Move validation, captures, suicide prevention
  - `Group`: Connected stone groups with liberty tracking
  - Weight functions: `uniform_weights()`, `center_weights()`, `aggressive_center_weights()`
  - Scoring: `score()` implements area scoring ensuring Black + White = total weight
  - `find_territory()`: Flood-fill algorithm determines territory ownership (Black, White, or contested)
  - `is_valid_position()`: Validates all groups have ≥1 liberty

- **[sgf_reader.py](weighted_go/core/sgf_reader.py)**: SGF file parsing
  - `read_sgf()` / `read_sgf_file()`: Parse SGF strings/files
  - `sgf_to_coords()`: Convert SGF notation (e.g., "dd") to (row, col)
  - Handles handicap stones (AB/AW properties), follows main path only
  - Validates final positions via `is_valid_position()`

- **[visualization.py](weighted_go/core/visualization.py)**: Board display
  - `print_board_with_territory()`: Display board with Unicode symbols
  - `get_board_string()`: Generate string representation
  - Uses symbols from `commons/symbols.py`: ● ○ ■ □ ⬕
  - Follows Go convention: column labels skip 'I' (A-H, J-T)

**[weighted_go/commons/](weighted_go/commons/)** - Shared constants and resources
- **[symbols.py](weighted_go/commons/symbols.py)**: Unicode symbols for terminal display
  - Stone symbols: `SYMBOL_BLACK_STONE`, `SYMBOL_WHITE_STONE`
  - Territory symbols: `SYMBOL_BLACK_TERRITORY`, `SYMBOL_WHITE_TERRITORY`, `SYMBOL_CONTESTED`
  - Board symbols: `SYMBOL_EMPTY`
  - Helper: `get_symbol_legend()` for displaying symbol meanings

- **[cli_colors.py](weighted_go/commons/cli_colors.py)**: ANSI color codes for terminal output
  - ANSI control sequences: `ANSI_RESET`, `ANSI_BOLD`, etc.
  - Standard 16-color codes for foreground/background
  - Color schemes for Go elements: `COLOR_BLACK_STONE`, `COLOR_WHITE_STONE`, etc.
  - Helper functions: `colorize()`, `strip_ansi()`, `colored_stone()`, `rgb_fg()`, etc.

- **[gui_colors.py](weighted_go/commons/gui_colors.py)**: Color constants for Tkinter GUI
  - Board colors: `BOARD_COLOR`, `GRID_COLOR`, `STAR_POINT_COLOR`, `COORD_COLOR`
  - Stone colors: `BLACK_STONE_COLOR`, `WHITE_STONE_COLOR` with outlines
  - Dead stone colors: `DEAD_BLACK_STONE_COLOR`, `DEAD_WHITE_STONE_COLOR`
  - Ghost stone alpha: `GHOST_BLACK_ALPHA`, `GHOST_WHITE_ALPHA`
  - Territory colors, highlight colors, UI element colors
  - All colors in hex format (#RRGGBB)

- **[resources.py](weighted_go/commons/resources.py)**: DEPRECATED re-export module
  - Re-exports from `symbols.py` and `cli_colors.py` for backward compatibility
  - New code should import directly from specific modules

**[weighted_go/core/board_size.py](weighted_go/core/board_size.py)** - Board dimension representation
- `BoardSize`: Represents board dimensions (rows, cols)
- Parse from strings: `BoardSize.from_string("19")`, `BoardSize.from_string("13x9")`
- Standard board factory methods: `BoardSize.standard_19()`, etc.
- Used throughout the system for board dimension handling

**[weighted_go/core/weight.py](weighted_go/core/weight.py)** - Weight system abstraction
- `Weight`: Abstract base class for weight schemes
- `FunctionWeight`: Weight defined by mathematical function
- `MatrixWeight`: Weight defined by pre-computed matrix
- Provides `as_matrix()` and `as_function()` for interfacing with scoring

**[weighted_go/commons/weights.py](weighted_go/commons/weights.py)** - Standard weight implementations
- `UniformWeight`: All positions weight 1.0 (standard Go)
- `CenterSquareWeight`: Square pattern (concentric squares)
- `CenterDiamondWeight`: Diamond pattern (stronger center bias)
- `STANDARD_WEIGHTS`: Registry of available weights
- Helper functions: `get_weight_by_name()`, `list_weights()`

**[weighted_go/gui/](weighted_go/gui/)** - Tkinter GUI application
- **[app.py](weighted_go/gui/app.py)**: Main application window
  - SGF loading with metadata extraction (player names, ranks, date, komi, result)
  - Weight scheme selection: Uniform, Center: Square, Center: Diamond
  - Dead stone marking via click (marks entire connected group)
  - Display modes: Stones Only, Territory Markers, Weight Heatmap
  - Live score updates when marking dead stones
- **[board_renderer.py](weighted_go/gui/board_renderer.py)**: Canvas-based board rendering
  - Automatic board scaling to fit canvas (no size cap)
  - Dead stones rendered with reduced opacity (black: 45%, white: 15%)
  - Territory markers: ■ (black), □ (white), ● (contested)
  - Territory calculation respects dead stones (treats them as empty)
  - Weight heatmap with diverging colormap supporting negative weights (blue→green→yellow→red)

### Package Exports

The main package (`weighted_go/__init__.py`) re-exports everything from `weighted_go.core`:
- Core classes: `Stone`, `Board`, `GamePosition`, `Group`, `Position`
- Weight types: `WeightMatrix`, `WeightFunc`
- Core functions: `find_group`, `has_liberties`, `score`, `find_territory`, etc.
- SGF functions: `read_sgf`, `read_sgf_file`, `sgf_to_coords`
- Visualization: `print_board_with_territory`, `get_board_string`
- Symbols: `SYMBOL_BLACK_STONE`, `SYMBOL_WHITE_STONE`, etc.

## Implementation Details

### Game Logic Flow
1. **Move placement**: `GamePosition.place_stone()` validates move legality
2. **Capture**: After placing, removes opponent groups with 0 liberties
3. **Suicide check**: Rejects moves that leave own group with 0 liberties (unless capturing)
4. **Group detection**: DFS via `find_group()` finds connected stones and their liberties
5. **Territory scoring**: `find_territory(board, start_pos)` flood-fills one empty region, returns `(positions, owner)`
   - Must be called for each empty region to build full territory matrix
   - Returns `Stone.EMPTY` for contested territory (touches both colors)

### Weight System Architecture
The weight system is organized into three layers:

1. **Board Dimension Layer** (`weighted_go/core/board_size.py`)
   - `BoardSize`: Fundamental board dimension representation
   - Used throughout the system (not just for weights)
   - Parse from strings: `BoardSize.from_string("19")`, `BoardSize.from_string("13x9")`
   - Factory methods: `BoardSize.standard_19()`, `BoardSize.standard_13()`, `BoardSize.standard_9()`

2. **Weight Abstraction Layer** (`weighted_go/core/weight.py`)
   - `Weight`: Base class defining the weight interface
   - `FunctionWeight`, `MatrixWeight`: Concrete implementations
   - Methods: `get_weight()`, `as_matrix()`, `as_function()`, `total_weight()`

3. **Standard Weights** (`weighted_go/commons/weights.py`)
   - `UniformWeight`: All positions weight 1.0 (standard Go)
   - `CenterSquareWeight`: `w[i][j] = 1 + min(dist_from_row_edge, dist_from_col_edge)` - concentric squares
   - `CenterDiamondWeight`: `w[i][j] = 1 + dist_from_row_edge + dist_from_col_edge` - concentric diamonds
   - Registry system: `STANDARD_WEIGHTS`, `get_weight_by_name()`, `list_weights()`

**Usage:**
```python
from weighted_go import UniformWeight, BoardSize, score

weight = UniformWeight()
board = BoardSize(19, 19)
matrix = weight.as_matrix(board)
black_score, white_score = score(position, matrix)
```

**Custom Weights:**
- Create `FunctionWeight` with custom formula
- Create `MatrixWeight` with pre-computed values
- Weights can be negative; heatmap visualization handles full range

**Note:** Legacy functions `uniform_weights(rows, cols)` are still available in `core.py` for internal use, but new code should use the Weight classes.

### Area Scoring Guarantees
- Every point is Black, White, or split 50-50 (contested)
- Total score invariant: `black_score + white_score == sum(all_weights)`
- Contested territory (touching both colors) splits evenly
- Stones count as territory for the player who placed them

### Non-square Boards
Full support via `Board(rows, cols)` and `GamePosition(rows, cols)`. SGF format `SZ[rows:cols]` is parsed correctly.

### GUI Development Notes
- **Dead stone marking**: Clicking a stone marks the entire connected group (via `find_group()`)
- **Territory updates**: Territory markers recalculate when dead stones change, treating dead positions as empty
- **Color blending for dead stones**: Calculated by blending stone color with goban background (#DCB35C)
  - Example: 45% black = blend(0.45 × #000000 + 0.55 × #DCB35C)
- **Board scaling**: No size cap on `cell_size`; board scales to fill available canvas space
- **Font consistency**: Use `TkDefaultFont` for consistent sizing across labels
- **Dynamic layout**: Game info labels use `pack_forget()` to hide/show based on SGF metadata availability

## Project Structure
```
weighted_go/
├── weighted_go/          # Main package
│   ├── core/             # Core game logic module
│   │   ├── __init__.py   # Re-exports all core functionality
│   │   ├── core.py       # Game logic
│   │   ├── sgf_reader.py # SGF parsing
│   │   └── visualization.py  # Display utilities
│   ├── commons/          # Shared resources
│   │   └── resources.py  # Unicode symbols, ANSI codes
│   ├── cli/              # CLI tools
│   │   ├── __init__.py
│   │   └── analyze_game.py  # Game analysis CLI
│   └── gui/              # GUI application
│       ├── __init__.py
│       ├── app.py        # Main window
│       ├── board_renderer.py  # Canvas rendering
│       └── run_gui.py    # GUI entry point
├── tests/                # Test suite (71 tests)
│   ├── test_core.py      # Core functionality tests
│   └── test_sgf_reader.py  # SGF parsing tests
├── examples/             # Example scripts
│   ├── cli/              # CLI examples
│   │   ├── basic_usage.py
│   │   ├── sgf_usage.py
│   │   └── color_demo.py
│   └── gui/              # GUI examples (future)
├── docs/                 # Documentation
├── data/                 # Sample SGF files
├── run_cli.sh            # CLI launcher script
├── run_gui.sh            # GUI launcher script
├── requirements.txt      # Production dependencies (none - stdlib only)
└── requirements-dev.txt  # Development dependencies (pytest)
```

## Testing Philosophy
- Tests validate game rules: captures, suicide prevention, ko
- Tests verify area scoring invariants (sum equals total weight)
- SGF tests use real game files and validate position legality
- No mocking of core game logic; tests use actual `Board` and `GamePosition` instances
