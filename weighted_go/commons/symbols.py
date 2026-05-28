"""
Unicode symbols for Weighted Go visualization.

These constants define the Unicode symbols used for terminal board display.
Changing these values will update all CLI visualizations.
"""

# ==============================================================================
# Stone Symbols
# ==============================================================================

SYMBOL_BLACK_STONE = "●"  # U+25CF Black Circle
SYMBOL_WHITE_STONE = "○"  # U+25CB White Circle


# ==============================================================================
# Territory Symbols
# ==============================================================================

SYMBOL_BLACK_TERRITORY = "■"  # U+25A0 Black Square
SYMBOL_WHITE_TERRITORY = "□"  # U+25A1 White Square
SYMBOL_CONTESTED = "⬕"  # U+2B55 Heavy Circle with Stroke


# ==============================================================================
# Board Symbols
# ==============================================================================

# Empty intersection (used in simple board display)
SYMBOL_EMPTY = "·"  # U+00B7 Middle Dot


# ==============================================================================
# Symbol Metadata
# ==============================================================================

# Symbol width information (for alignment calculations)
# All symbols above have East Asian Width property 'A' (Ambiguous) or 'N' (Neutral)
# which renders as single-width in most terminals
SYMBOL_DISPLAY_WIDTH = 1  # All symbols are single-width for consistent alignment


# ==============================================================================
# Helper Functions
# ==============================================================================

def get_symbol_legend() -> str:
    """
    Get a formatted legend of all symbols.

    Returns:
        String showing all symbols with their meanings
    """
    return (
        f"  {SYMBOL_BLACK_STONE} Black stones  {SYMBOL_WHITE_STONE} White stones\n"
        f"  {SYMBOL_BLACK_TERRITORY} Black territory  "
        f"{SYMBOL_WHITE_TERRITORY} White territory  "
        f"{SYMBOL_CONTESTED} Contested"
    )
