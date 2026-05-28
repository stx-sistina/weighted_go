#!/usr/bin/env python
"""Quick test script to verify edit mode functionality."""

import tkinter as tk
from weighted_go.gui.app import WeightedGoApp

# Create and run the GUI
root = tk.Tk()
app = WeightedGoApp(root)

# Print initial state
print("GUI initialized successfully")
print(f"App mode: {app.app_mode}")
print(f"Position: {app.position.board.rows}x{app.position.board.cols}")
print(f"Edit mode var: {app.edit_mode_var.get()}")
print(f"Next stone color: {app.next_stone_color}")
print("\nGUI is ready - close the window to exit")

# Run the GUI
root.mainloop()
