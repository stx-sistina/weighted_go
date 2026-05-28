# CLI Examples

Command-line examples demonstrating the Weighted Go core functionality.

## Running Examples

From the project root:

```bash
# Basic usage
PYTHONPATH=. python examples/cli/basic_usage.py

# SGF file usage
PYTHONPATH=. python examples/cli/sgf_usage.py

# Color/ANSI demonstration
PYTHONPATH=. python examples/cli/color_demo.py
```

Or after installing the package (`pip install -e .`):

```bash
python examples/cli/basic_usage.py
python examples/cli/sgf_usage.py
python examples/cli/color_demo.py
```

## Examples

- **basic_usage.py** - Basic board creation, move placement, and scoring
- **sgf_usage.py** - Loading and analyzing SGF files
- **color_demo.py** - Terminal color capabilities demonstration
- **weight_system_demo.py** - Weight system API and custom weight creation
