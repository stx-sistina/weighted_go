"""
Board rendering for the GUI.

Handles drawing the Go board, stones, territory markers, and weight heatmaps.
"""

import tkinter as tk
from typing import Optional, Set, Tuple, List
import colorsys

from ..core import Board, GamePosition, Stone, find_territory


class BoardRenderer:
    """Renders a Go board on a Tkinter canvas."""

    # Visual constants
    BOARD_COLOR = "#DCB35C"  # Traditional goban color
    GRID_COLOR = "#000000"
    STAR_POINT_COLOR = "#000000"
    COORD_COLOR = "#333333"

    # Stone colors
    BLACK_STONE_COLOR = "#000000"
    BLACK_STONE_OUTLINE = "#333333"
    WHITE_STONE_COLOR = "#FFFFFF"
    WHITE_STONE_OUTLINE = "#CCCCCC"

    # Dead stone marking
    DEAD_STONE_MARK_COLOR = "#FF0000"
    DEAD_STONE_ALPHA = 0.5

    # Territory colors (semi-transparent)
    BLACK_TERRITORY_COLOR = "#000000"
    WHITE_TERRITORY_COLOR = "#FFFFFF"
    CONTESTED_TERRITORY_COLOR = "#808080"

    def __init__(self, canvas: tk.Canvas):
        """
        Initialize board renderer.

        Args:
            canvas: Tkinter canvas to draw on
        """
        self.canvas = canvas
        self.board: Optional[Board] = None
        self.position: Optional[GamePosition] = None

        # Layout parameters (calculated on draw)
        self.margin = 40
        self.cell_size = 30
        self.stone_radius = 13
        self.star_point_radius = 4

        # Coordinate mapping
        self.board_offset_x = 0
        self.board_offset_y = 0

    def set_position(self, position: GamePosition):
        """Set the game position to render."""
        self.position = position
        self.board = position.board

    def calculate_layout(self):
        """Calculate board layout based on canvas size."""
        if not self.board:
            return

        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()

        # Calculate cell size to fit board
        available_width = canvas_width - 2 * self.margin
        available_height = canvas_height - 2 * self.margin

        max_cell_width = available_width // (self.board.cols - 1) if self.board.cols > 1 else available_width
        max_cell_height = available_height // (self.board.rows - 1) if self.board.rows > 1 else available_height

        self.cell_size = min(max_cell_width, max_cell_height)  # No cap - scale with window
        self.stone_radius = int(self.cell_size * 0.45)

        # Center the board
        board_width = (self.board.cols - 1) * self.cell_size
        board_height = (self.board.rows - 1) * self.cell_size

        self.board_offset_x = (canvas_width - board_width) // 2
        self.board_offset_y = (canvas_height - board_height) // 2

    def board_to_canvas(self, row: int, col: int) -> Tuple[int, int]:
        """
        Convert board coordinates to canvas pixel coordinates.

        Args:
            row, col: Board coordinates

        Returns:
            (x, y) canvas pixel coordinates
        """
        x = self.board_offset_x + col * self.cell_size
        y = self.board_offset_y + row * self.cell_size
        return x, y

    def canvas_to_board(self, x: int, y: int) -> Optional[Tuple[int, int]]:
        """
        Convert canvas pixel coordinates to board coordinates.

        Args:
            x, y: Canvas pixel coordinates

        Returns:
            (row, col) tuple or None if outside board
        """
        if not self.board:
            return None

        # Ensure layout is calculated
        if self.cell_size == 0 or self.board_offset_x == 0:
            self.calculate_layout()

        # Calculate board position
        board_x = x - self.board_offset_x
        board_y = y - self.board_offset_y

        # Find nearest intersection
        col = round(board_x / self.cell_size)
        row = round(board_y / self.cell_size)

        # Check bounds first
        if not (0 <= row < self.board.rows and 0 <= col < self.board.cols):
            return None

        # Check if click is close enough to intersection
        actual_x, actual_y = self.board_to_canvas(row, col)
        distance = ((x - actual_x) ** 2 + (y - actual_y) ** 2) ** 0.5

        if distance > self.stone_radius * 1.2:  # Click tolerance
            return None

        return (row, col)

    def draw_board(self, show_coordinates: bool = True):
        """
        Draw the board grid and coordinates.

        Args:
            show_coordinates: Whether to show coordinate labels
        """
        if not self.board:
            return

        self.calculate_layout()

        # Background
        self.canvas.config(bg=self.BOARD_COLOR)

        # Grid lines
        for row in range(self.board.rows):
            x1, y1 = self.board_to_canvas(row, 0)
            x2, y2 = self.board_to_canvas(row, self.board.cols - 1)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.GRID_COLOR, width=1)

        for col in range(self.board.cols):
            x1, y1 = self.board_to_canvas(0, col)
            x2, y2 = self.board_to_canvas(self.board.rows - 1, col)
            self.canvas.create_line(x1, y1, x2, y2, fill=self.GRID_COLOR, width=1)

        # Star points (for standard board sizes)
        star_points = self.get_star_points()
        for row, col in star_points:
            x, y = self.board_to_canvas(row, col)
            self.canvas.create_oval(
                x - self.star_point_radius, y - self.star_point_radius,
                x + self.star_point_radius, y + self.star_point_radius,
                fill=self.STAR_POINT_COLOR, outline=""
            )

        # Coordinates
        if show_coordinates:
            self.draw_coordinates()

    def get_star_points(self) -> List[Tuple[int, int]]:
        """Get star point positions for the current board size."""
        rows, cols = self.board.rows, self.board.cols

        # Standard star points for common board sizes
        if rows == 19 and cols == 19:
            return [(3, 3), (3, 9), (3, 15),
                   (9, 3), (9, 9), (9, 15),
                   (15, 3), (15, 9), (15, 15)]
        elif rows == 13 and cols == 13:
            return [(3, 3), (3, 9), (6, 6), (9, 3), (9, 9)]
        elif rows == 9 and cols == 9:
            return [(2, 2), (2, 6), (4, 4), (6, 2), (6, 6)]

        return []

    def draw_coordinates(self):
        """Draw coordinate labels (A-T, 1-19)."""
        if not self.board:
            return

        font_size = max(8, min(12, self.cell_size // 3))

        # Column labels (skip 'I' per Go convention)
        for col in range(self.board.cols):
            label = chr(ord('A') + col)
            if label >= 'I':
                label = chr(ord(label) + 1)

            x, y_top = self.board_to_canvas(0, col)
            x, y_bottom = self.board_to_canvas(self.board.rows - 1, col)

            # Top
            self.canvas.create_text(
                x, y_top - 20,
                text=label, fill=self.COORD_COLOR,
                font=("Helvetica", font_size)
            )
            # Bottom
            self.canvas.create_text(
                x, y_bottom + 20,
                text=label, fill=self.COORD_COLOR,
                font=("Helvetica", font_size)
            )

        # Row labels (1-indexed)
        for row in range(self.board.rows):
            label = str(row + 1)
            x_left, y = self.board_to_canvas(row, 0)
            x_right, y = self.board_to_canvas(row, self.board.cols - 1)

            # Left
            self.canvas.create_text(
                x_left - 20, y,
                text=label, fill=self.COORD_COLOR,
                font=("Helvetica", font_size)
            )
            # Right
            self.canvas.create_text(
                x_right + 20, y,
                text=label, fill=self.COORD_COLOR,
                font=("Helvetica", font_size)
            )

    def draw_stones(self, dead_stones: Set[Tuple[int, int]] = None, show_dead: bool = True):
        """
        Draw stones on the board.

        Args:
            dead_stones: Set of (row, col) coordinates marked as dead
            show_dead: Whether to draw dead stones (faded) or skip them entirely
        """
        if not self.board:
            return

        dead_stones = dead_stones or set()

        for row in range(self.board.rows):
            for col in range(self.board.cols):
                stone = self.board.get((row, col))
                if stone != Stone.EMPTY:
                    is_dead = (row, col) in dead_stones
                    if not is_dead or show_dead:
                        self.draw_stone(row, col, stone, is_dead=is_dead)

    def draw_stone(self, row: int, col: int, stone: Stone, is_dead: bool = False):
        """
        Draw a single stone.

        Args:
            row, col: Board coordinates
            stone: Stone color
            is_dead: Whether this stone is marked as dead
        """
        x, y = self.board_to_canvas(row, col)

        if is_dead:
            # Dead stones: use very light/faded colors
            # alpha = 0.45 for black, 0.15 for white
            if stone == Stone.BLACK:
                fill = "#796233"  # 45% black on goban background
                outline = "#897243"
            else:
                fill = "#EAE3D3"  # 20% white on goban background
                outline = "#DAE3D3"
        else:
            # Normal stones
            if stone == Stone.BLACK:
                fill = self.BLACK_STONE_COLOR
                outline = self.BLACK_STONE_OUTLINE
            else:
                fill = self.WHITE_STONE_COLOR
                outline = self.WHITE_STONE_OUTLINE

        # Draw stone
        self.canvas.create_oval(
            x - self.stone_radius, y - self.stone_radius,
            x + self.stone_radius, y + self.stone_radius,
            fill=fill, outline=outline, width=1,
            tags="stone"
        )

    def compute_territory_matrix(self, dead_stones: Set[Tuple[int, int]] = None):
        """
        Compute territory ownership for the entire board.

        Args:
            dead_stones: Set of (row, col) coordinates to treat as empty

        Returns:
            2D list where each element is Stone.BLACK, Stone.WHITE, or Stone.EMPTY (contested)
        """
        if not self.position:
            return []

        dead_stones = dead_stones or set()

        # Initialize territory matrix
        rows, cols = self.board.rows, self.board.cols
        territory_matrix = [[Stone.EMPTY for _ in range(cols)] for _ in range(rows)]
        assigned = set()

        # Mark stones (excluding dead stones)
        for row in range(rows):
            for col in range(cols):
                pos = (row, col)
                stone = self.board.get(pos)
                if stone != Stone.EMPTY and pos not in dead_stones:
                    territory_matrix[row][col] = stone
                    assigned.add(pos)

        # Find empty territories (including dead stone positions)
        for row in range(rows):
            for col in range(cols):
                pos = (row, col)
                if pos in assigned:
                    continue

                # Create a temporary board with dead stones removed
                from ..core import Board as CoreBoard
                temp_board = CoreBoard(rows, cols)
                for r in range(rows):
                    for c in range(cols):
                        p = (r, c)
                        if p not in dead_stones:
                            temp_board.set(p, self.board.get(p))

                # Find territory region on the modified board
                territory, owner = find_territory(temp_board, pos)

                # Mark all positions in this territory
                for t_row, t_col in territory:
                    territory_matrix[t_row][t_col] = owner
                    assigned.add((t_row, t_col))

        return territory_matrix

    def draw_territory(self, dead_stones: Set[Tuple[int, int]] = None):
        """
        Draw territory markers on empty intersections.

        Args:
            dead_stones: Set of (row, col) coordinates marked as dead
        """
        if not self.position:
            return

        dead_stones = dead_stones or set()
        territory_matrix = self.compute_territory_matrix(dead_stones)
        marker_size = self.stone_radius // 3

        for row in range(self.board.rows):
            for col in range(self.board.cols):
                pos = (row, col)
                # Show territory markers on empty intersections and dead stone positions
                if self.board.get(pos) != Stone.EMPTY and pos not in dead_stones:
                    continue  # Skip live stones

                owner = territory_matrix[row][col]
                x, y = self.board_to_canvas(row, col)

                if owner == Stone.BLACK:
                    # Small filled square for black territory
                    self.canvas.create_rectangle(
                        x - marker_size, y - marker_size,
                        x + marker_size, y + marker_size,
                        fill=self.BLACK_TERRITORY_COLOR, outline="",
                        tags="territory"
                    )
                elif owner == Stone.WHITE:
                    # Small hollow square for white territory
                    self.canvas.create_rectangle(
                        x - marker_size, y - marker_size,
                        x + marker_size, y + marker_size,
                        fill="", outline=self.WHITE_TERRITORY_COLOR, width=2,
                        tags="territory"
                    )
                else:
                    # Small circle for contested territory (Stone.EMPTY)
                    self.canvas.create_oval(
                        x - marker_size, y - marker_size,
                        x + marker_size, y + marker_size,
                        fill=self.CONTESTED_TERRITORY_COLOR, outline="",
                        tags="territory"
                    )

    def draw_heatmap(self, weights):
        """
        Draw weight heatmap.

        Args:
            weights: Weight matrix or weight function
        """
        if not self.board:
            return

        # Convert weights to matrix if it's a function
        if callable(weights):
            weight_matrix = [[weights(r, c) for c in range(self.board.cols)]
                           for r in range(self.board.rows)]
        else:
            weight_matrix = weights

        # Find min/max for color mapping
        all_weights = [w for row in weight_matrix for w in row]
        min_weight = min(all_weights)
        max_weight = max(all_weights)

        # Draw colored rectangles for each cell
        for row in range(self.board.rows):
            for col in range(self.board.cols):
                weight = weight_matrix[row][col]

                # Color mapping supporting negative values
                color = self.value_to_color(weight, min_weight, max_weight)

                x, y = self.board_to_canvas(row, col)
                half_cell = self.cell_size // 2

                self.canvas.create_rectangle(
                    x - half_cell, y - half_cell,
                    x + half_cell, y + half_cell,
                    fill=color, outline="", tags="heatmap"
                )

                # Draw weight value
                if self.cell_size >= 25:
                    font_size = max(6, min(10, self.cell_size // 4))
                    # Determine text color based on background brightness
                    import colorsys
                    rgb = tuple(int(color[i:i+2], 16) / 255 for i in (1, 3, 5))
                    brightness = colorsys.rgb_to_hsv(*rgb)[2]
                    text_color = "white" if brightness < 0.5 else "black"

                    self.canvas.create_text(
                        x, y,
                        text=f"{weight:.1f}",
                        fill=text_color,
                        font=("Helvetica", font_size),
                        tags="heatmap"
                    )

    def value_to_color(self, value: float, min_val: float, max_val: float) -> str:
        """
        Convert a value to a heatmap color supporting negative values.

        Args:
            value: The actual value
            min_val: Minimum value in the dataset
            max_val: Maximum value in the dataset

        Returns:
            Hex color string

        Color scheme:
            Very negative -> Deep Blue
            Zero -> Green
            Positive -> Yellow -> Red
        """
        # Normalize relative to zero
        if max_val <= 0:
            # All values are non-positive
            if min_val == max_val:
                normalized = 0.5
            else:
                normalized = (value - min_val) / (max_val - min_val) * 0.5
            # Map to blue -> green
            hue = 240 - normalized * 120  # 240° (blue) to 120° (green)
            saturation = 0.7
            brightness = 0.8
        elif min_val >= 0:
            # All values are non-negative
            if min_val == max_val:
                normalized = 0.5
            else:
                normalized = (value - min_val) / (max_val - min_val)
            # Map to green -> yellow -> red
            hue = 120 - normalized * 120  # 120° (green) to 0° (red)
            saturation = 0.8
            brightness = 0.9
        else:
            # Values span negative to positive
            if value < 0:
                # Negative: blue -> green
                normalized = value / min_val  # 0 at value=0, 1 at min_val
                hue = 240 - normalized * 120  # 120° (green) to 240° (blue)
                saturation = 0.7 + normalized * 0.1
                brightness = 0.8 + normalized * 0.1
            else:
                # Positive: green -> yellow -> red
                normalized = value / max_val  # 0 at value=0, 1 at max_val
                hue = 120 - normalized * 120  # 120° (green) to 0° (red)
                saturation = 0.8
                brightness = 0.9

        r, g, b = colorsys.hsv_to_rgb(hue / 360, saturation, brightness)
        return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
