#!/usr/bin/env python3
"""
Standalone entry point for Weighted Go GUI application.

This file uses absolute imports and works as a PyInstaller entry point.
"""

import sys
import tkinter as tk
from weighted_go.gui import WeightedGoApp


def main():
    """Main entry point."""
    root = tk.Tk()
    app = WeightedGoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
