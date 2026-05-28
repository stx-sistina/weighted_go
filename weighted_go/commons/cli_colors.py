"""
ANSI color codes for terminal/CLI display in Weighted Go.

These constants define the color schemes used for terminal output.
Includes ANSI escape codes, color schemes for Go elements, and helper functions.
"""

# ==============================================================================
# ANSI Control Sequences
# ==============================================================================

ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_ITALIC = "\033[3m"
ANSI_UNDERLINE = "\033[4m"
ANSI_BLINK = "\033[5m"
ANSI_REVERSE = "\033[7m"
ANSI_HIDDEN = "\033[8m"
ANSI_STRIKETHROUGH = "\033[9m"


# ==============================================================================
# Foreground (Text) Colors - Standard 16 Colors
# ==============================================================================

ANSI_FG_BLACK = "\033[30m"
ANSI_FG_RED = "\033[31m"
ANSI_FG_GREEN = "\033[32m"
ANSI_FG_YELLOW = "\033[33m"
ANSI_FG_BLUE = "\033[34m"
ANSI_FG_MAGENTA = "\033[35m"
ANSI_FG_CYAN = "\033[36m"
ANSI_FG_WHITE = "\033[37m"
ANSI_FG_BRIGHT_BLACK = "\033[90m"  # Gray
ANSI_FG_BRIGHT_RED = "\033[91m"
ANSI_FG_BRIGHT_GREEN = "\033[92m"
ANSI_FG_BRIGHT_YELLOW = "\033[93m"
ANSI_FG_BRIGHT_BLUE = "\033[94m"
ANSI_FG_BRIGHT_MAGENTA = "\033[95m"
ANSI_FG_BRIGHT_CYAN = "\033[96m"
ANSI_FG_BRIGHT_WHITE = "\033[97m"


# ==============================================================================
# Background Colors - Standard 16 Colors
# ==============================================================================

ANSI_BG_BLACK = "\033[40m"
ANSI_BG_RED = "\033[41m"
ANSI_BG_GREEN = "\033[42m"
ANSI_BG_YELLOW = "\033[43m"
ANSI_BG_BLUE = "\033[44m"
ANSI_BG_MAGENTA = "\033[45m"
ANSI_BG_CYAN = "\033[46m"
ANSI_BG_WHITE = "\033[47m"
ANSI_BG_BRIGHT_BLACK = "\033[100m"  # Gray
ANSI_BG_BRIGHT_RED = "\033[101m"
ANSI_BG_BRIGHT_GREEN = "\033[102m"
ANSI_BG_BRIGHT_YELLOW = "\033[103m"
ANSI_BG_BRIGHT_BLUE = "\033[104m"
ANSI_BG_BRIGHT_MAGENTA = "\033[105m"
ANSI_BG_BRIGHT_CYAN = "\033[106m"
ANSI_BG_BRIGHT_WHITE = "\033[107m"


# ==============================================================================
# Default Colors
# ==============================================================================

ANSI_FG_DEFAULT = "\033[39m"
ANSI_BG_DEFAULT = "\033[49m"


# ==============================================================================
# Color Scheme for Go Elements
# ==============================================================================

# Stone colors (for terminal display)
COLOR_BLACK_STONE = ANSI_FG_BRIGHT_BLACK + ANSI_BOLD
COLOR_WHITE_STONE = ANSI_FG_BRIGHT_WHITE + ANSI_BOLD

# Territory colors
COLOR_BLACK_TERRITORY = ANSI_FG_BLACK
COLOR_WHITE_TERRITORY = ANSI_FG_WHITE
COLOR_CONTESTED = ANSI_FG_YELLOW

# Board elements
COLOR_BOARD_BACKGROUND = ANSI_BG_YELLOW + ANSI_FG_BLACK  # Traditional goban color
COLOR_COORDINATES = ANSI_FG_CYAN
COLOR_GRID_LINES = ANSI_FG_BRIGHT_BLACK

# Highlights
COLOR_LAST_MOVE = ANSI_BG_BRIGHT_BLUE
COLOR_HOVER = ANSI_BG_BRIGHT_GREEN
COLOR_INVALID_MOVE = ANSI_BG_RED + ANSI_FG_BRIGHT_WHITE
COLOR_CAPTURE_HIGHLIGHT = ANSI_BG_BRIGHT_RED

# Score display
COLOR_SCORE_BLACK = ANSI_FG_BRIGHT_BLACK + ANSI_BOLD
COLOR_SCORE_WHITE = ANSI_FG_BRIGHT_WHITE + ANSI_BOLD
COLOR_WINNER = ANSI_FG_BRIGHT_GREEN + ANSI_BOLD


# ==============================================================================
# Helper Functions for Colored Output
# ==============================================================================

def is_terminal() -> bool:
    """
    Check if output is going to a terminal (TTY).

    Returns:
        True if stdout is a terminal, False if redirected to file/pipe

    Examples:
        >>> is_terminal()  # In terminal
        True
        >>> is_terminal()  # When redirected: python script.py > output.txt
        False
    """
    import sys
    return hasattr(sys.stdout, 'isatty') and sys.stdout.isatty()


def colorize(text: str, *codes: str, force: bool = False) -> str:
    """
    Apply ANSI color/style codes to text.

    Args:
        text: Text to colorize
        *codes: ANSI escape codes to apply
        force: If True, apply colors even when not in terminal

    Returns:
        Colored text with reset at the end (if in terminal or forced)

    Examples:
        >>> colorize("Hello", ANSI_FG_RED, ANSI_BOLD)
        '\\033[31m\\033[1mHello\\033[0m'  # In terminal
        'Hello'  # When redirected to file

    Note:
        Colors are automatically disabled when output is redirected to a file
        unless force=True is specified.
    """
    if not codes:
        return text

    # Only use colors if outputting to terminal (unless forced)
    if not force and not is_terminal():
        return text

    return "".join(codes) + text + ANSI_RESET


def strip_ansi(text: str) -> str:
    """
    Remove all ANSI escape codes from text.

    Args:
        text: Text potentially containing ANSI codes

    Returns:
        Text with all ANSI codes removed

    Useful for calculating actual display width.
    """
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)


def colored_stone(stone_symbol: str, is_black: bool, force: bool = False) -> str:
    """
    Apply appropriate color to a stone symbol.

    Args:
        stone_symbol: The stone symbol to color
        is_black: True for black stone, False for white stone
        force: If True, apply colors even when not in terminal

    Returns:
        Colored stone symbol
    """
    if is_black:
        return colorize(stone_symbol, COLOR_BLACK_STONE, force=force)
    else:
        return colorize(stone_symbol, COLOR_WHITE_STONE, force=force)


def rgb_fg(r: int, g: int, b: int) -> str:
    """
    Generate ANSI escape code for 24-bit RGB foreground color.

    Args:
        r, g, b: RGB values (0-255)

    Returns:
        ANSI escape code for RGB foreground color

    Example:
        >>> rgb_fg(255, 100, 0)  # Orange
        '\\033[38;2;255;100;0m'
    """
    return f"\033[38;2;{r};{g};{b}m"


def rgb_bg(r: int, g: int, b: int) -> str:
    """
    Generate ANSI escape code for 24-bit RGB background color.

    Args:
        r, g, b: RGB values (0-255)

    Returns:
        ANSI escape code for RGB background color

    Example:
        >>> rgb_bg(50, 50, 50)  # Dark gray
        '\\033[48;2;50;50;50m'
    """
    return f"\033[48;2;{r};{g};{b}m"


def color_256_fg(color: int) -> str:
    """
    Generate ANSI escape code for 256-color foreground.

    Args:
        color: Color index (0-255)

    Returns:
        ANSI escape code for 256-color foreground

    Example:
        >>> color_256_fg(196)  # Bright red
        '\\033[38;5;196m'
    """
    return f"\033[38;5;{color}m"


def color_256_bg(color: int) -> str:
    """
    Generate ANSI escape code for 256-color background.

    Args:
        color: Color index (0-255)

    Returns:
        ANSI escape code for 256-color background

    Example:
        >>> color_256_bg(17)  # Dark blue
        '\\033[48;5;17m'
    """
    return f"\033[48;5;{color}m"
