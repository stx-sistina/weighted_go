#!/usr/bin/env python3
"""
Launch the Weighted Go GUI application.

Usage:
    python -m weighted_go.gui.run_gui
    # Or from project root:
    python weighted_go/gui/run_gui.py
"""

import tkinter as tk
from . import WeightedGoApp


def main():
    """Main entry point."""
    root = tk.Tk()
    app = WeightedGoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
