#!/bin/bash
# Launcher script for Weighted Go CLI tools

# Default to analyze_game if no arguments provided
if [ $# -eq 0 ]; then
    echo "Usage: ./run_cli.sh <sgf_file> [--full]"
    echo "Example: ./run_cli.sh data/game.sgf"
    exit 1
fi

# Run the analyze_game CLI tool
python -m weighted_go.cli.analyze_game "$@"
