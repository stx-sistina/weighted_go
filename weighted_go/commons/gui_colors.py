"""
GUI Color Constants for Weighted Go.

These constants define the colors used in the Tkinter GUI.
All colors are in hexadecimal format (#RRGGBB).
"""

# ==============================================================================
# Board Colors
# ==============================================================================

# Goban (board) background
BOARD_COLOR = "#DCB35C"  # Traditional goban wood color
GRID_COLOR = "#000000"  # Black grid lines
STAR_POINT_COLOR = "#000000"  # Black star points (hoshi)
COORD_COLOR = "#333333"  # Dark gray coordinate labels


# ==============================================================================
# Stone Colors
# ==============================================================================

# Black stones
BLACK_STONE_COLOR = "#000000"
BLACK_STONE_OUTLINE = "#333333"  # Slightly lighter for depth

# White stones
WHITE_STONE_COLOR = "#FFFFFF"
WHITE_STONE_OUTLINE = "#CCCCCC"  # Slightly darker for depth

# Dead stones (faded/blended with goban)
DEAD_BLACK_STONE_COLOR = "#796233"  # 45% black blended with goban
DEAD_BLACK_STONE_OUTLINE = "#897243"
DEAD_WHITE_STONE_COLOR = "#EBD5A5"  # 45% white blended with goban
DEAD_WHITE_STONE_OUTLINE = "#DBD5A5"

# Ghost stones (for editing mode preview)
GHOST_BLACK_ALPHA = 0.45
GHOST_WHITE_ALPHA = 0.45


# ==============================================================================
# Territory Colors
# ==============================================================================

BLACK_TERRITORY_COLOR = "#000000"
WHITE_TERRITORY_COLOR = "#FFFFFF"
CONTESTED_TERRITORY_COLOR = "#808080"  # Gray


# ==============================================================================
# Highlight Colors
# ==============================================================================

# Invalid group highlighting
INVALID_GROUP_COLOR = "#FF0000"  # Red outline
INVALID_GROUP_WIDTH = 3  # Line width in pixels

# Dead stone marking (if needed)
DEAD_STONE_MARK_COLOR = "#FF0000"  # Red
DEAD_STONE_ALPHA = 0.5  # 50% opacity


# ==============================================================================
# UI Element Colors
# ==============================================================================

# File label colors
FILE_LABEL_NORMAL_COLOR = "black"
FILE_LABEL_EMPTY_COLOR = "gray"
