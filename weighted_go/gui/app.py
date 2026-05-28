"""
Main GUI application for Weighted Go.

Provides:
- Visual board display with stone graphics
- SGF file loading
- Weight scheme selection
- Score calculation and display
- Manual dead group removal
- Weight heatmap visualization
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional, Set, Tuple
from pathlib import Path

from ..core import (
    GamePosition, Stone,
    uniform_weights, center_weights, aggressive_center_weights,
    score, find_group,
    read_sgf_file, parse_sgf_properties
)
from .board_renderer import BoardRenderer


class WeightedGoApp:
    """Main application window for Weighted Go."""

    # Weight schemes available
    WEIGHT_SCHEMES = {
        "Uniform (Standard)": uniform_weights,
        "Center: Square": center_weights,
        "Center: Diamond": aggressive_center_weights,
    }

    def __init__(self, root: tk.Tk):
        """
        Initialize the GUI application.

        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("Weighted Go - Scoring and Analysis")
        self.root.geometry("1050x800")  # Narrower to make board canvas more square

        # Application state
        self.position: Optional[GamePosition] = None
        self.current_weights = None
        self.current_weight_name = "Uniform (Standard)"
        self.dead_stones: Set[Tuple[int, int]] = set()  # Coordinates of dead stones
        self.sgf_properties: dict = {}  # SGF metadata

        # Board renderer
        self.renderer: Optional[BoardRenderer] = None

        # UI components
        self.setup_ui()

        # Default: load uniform weights for 19x19 and create empty board
        self.current_weights = uniform_weights(19, 19)
        self.load_empty_board(19, 19)

    def setup_ui(self):
        """Set up the user interface layout."""
        # Main container with two columns
        main_container = ttk.Frame(self.root, padding="10")
        main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Configure grid weights for resizing
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_container.columnconfigure(1, weight=1)
        main_container.rowconfigure(0, weight=1)

        # Left panel: Controls
        self.setup_control_panel(main_container)

        # Right panel: Board display
        self.setup_board_panel(main_container)

    def setup_control_panel(self, parent):
        """Set up the left control panel."""
        control_frame = ttk.Frame(parent, padding="5", relief=tk.RIDGE, borderwidth=2, width=250)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        control_frame.grid_propagate(False)  # Prevent resizing based on content

        # Configure column to expand
        control_frame.columnconfigure(0, weight=1)

        row = 0

        # Title
        title = ttk.Label(control_frame, text="Weighted Go", font=("Helvetica", 16, "bold"))
        title.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        row += 1

        # File loading section
        ttk.Label(control_frame, text="Game File", font=("Helvetica", 12, "bold")).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=(10, 5)
        )
        row += 1

        self.file_label = ttk.Label(control_frame, text="No file loaded", foreground="gray",
                                   wraplength=220)
        self.file_label.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        ttk.Button(control_frame, text="Load SGF File", command=self.load_sgf).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=5
        )
        row += 1

        # Game info section
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=10
        )
        row += 1

        ttk.Label(control_frame, text="Game Info", font=("Helvetica", 12, "bold")).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5)
        )
        row += 1

        # Game info labels - only pack them when they have content
        self.game_info_frame = ttk.Frame(control_frame)
        self.game_info_frame.grid(row=row, column=0, sticky=(tk.W, tk.E))

        self.event_label = ttk.Label(self.game_info_frame, wraplength=220)
        self.date_label = ttk.Label(self.game_info_frame, wraplength=220)
        self.black_player_label = ttk.Label(self.game_info_frame, wraplength=220)
        self.white_player_label = ttk.Label(self.game_info_frame, wraplength=220)
        self.komi_label = ttk.Label(self.game_info_frame, wraplength=220)
        self.result_label = ttk.Label(self.game_info_frame, wraplength=220)

        row += 1

        # Weight scheme selection
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=10
        )
        row += 1

        ttk.Label(control_frame, text="Weight Scheme", font=("Helvetica", 12, "bold")).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5)
        )
        row += 1

        self.weight_var = tk.StringVar(value=self.current_weight_name)
        for scheme_name in self.WEIGHT_SCHEMES.keys():
            ttk.Radiobutton(
                control_frame,
                text=scheme_name,
                variable=self.weight_var,
                value=scheme_name,
                command=self.on_weight_changed
            ).grid(row=row, column=0, sticky=(tk.W, tk.E))
            row += 1

        # Score display
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=10
        )
        row += 1

        ttk.Label(control_frame, text="Score", font=("Helvetica", 12, "bold")).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5)
        )
        row += 1

        score_frame = ttk.Frame(control_frame)
        score_frame.grid(row=row, column=0, sticky=(tk.W, tk.E))
        score_frame.columnconfigure(0, weight=1)
        row += 1

        self.score_black_label = ttk.Label(score_frame, text="Black: -")
        self.score_black_label.grid(row=0, column=0, sticky=(tk.W, tk.E))

        self.score_white_label = ttk.Label(score_frame, text="White: -")
        self.score_white_label.grid(row=1, column=0, sticky=(tk.W, tk.E))

        # Use default font with bold weight
        import tkinter.font as tkfont
        default_font = tkfont.nametofont("TkDefaultFont")
        bold_font = tkfont.Font(family=default_font.actual()["family"],
                               size=default_font.actual()["size"],
                               weight="bold")

        self.score_result_label = ttk.Label(score_frame, text="Result: -", font=bold_font)
        self.score_result_label.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Dead group removal
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=10
        )
        row += 1

        ttk.Label(control_frame, text="Dead Stones", font=("Helvetica", 12, "bold")).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5)
        )
        row += 1

        ttk.Label(control_frame, text="Click stones to mark as dead", foreground="gray").grid(
            row=row, column=0, sticky=(tk.W, tk.E)
        )
        row += 1

        self.dead_black_label = ttk.Label(control_frame, text="Dead black: 0")
        self.dead_black_label.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        self.dead_white_label = ttk.Label(control_frame, text="Dead white: 0")
        self.dead_white_label.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        ttk.Button(control_frame, text="Clear Dead Stones", command=self.clear_dead_stones).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=5
        )
        row += 1

        # Display mode
        ttk.Separator(control_frame, orient=tk.HORIZONTAL).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=10
        )
        row += 1

        ttk.Label(control_frame, text="Display Mode", font=("Helvetica", 12, "bold")).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5)
        )
        row += 1

        self.display_var = tk.StringVar(value="stones")
        ttk.Radiobutton(
            control_frame,
            text="Stones Only",
            variable=self.display_var,
            value="stones",
            command=self.redraw_board
        ).grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        ttk.Radiobutton(
            control_frame,
            text="Territory Markers",
            variable=self.display_var,
            value="territory",
            command=self.redraw_board
        ).grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        ttk.Radiobutton(
            control_frame,
            text="Weight Heatmap",
            variable=self.display_var,
            value="heatmap",
            command=self.redraw_board
        ).grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

    def setup_board_panel(self, parent):
        """Set up the right board display panel."""
        board_frame = ttk.Frame(parent, padding="5", relief=tk.RIDGE, borderwidth=2)
        board_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Board canvas
        self.canvas = tk.Canvas(board_frame, bg="burlywood", width=700, height=700)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Initialize renderer
        self.renderer = BoardRenderer(self.canvas)

        # Bind click events for dead stone marking
        self.canvas.bind("<Button-1>", self.on_canvas_click)

        # Bind resize event to fix board positioning
        self.canvas.bind("<Configure>", self.on_canvas_resize)

        # Info label
        self.info_label = ttk.Label(board_frame, text="Load an SGF file to begin",
                                    font=("Helvetica", 10))
        self.info_label.pack(pady=5)

    def load_empty_board(self, rows: int = 19, cols: int = 19):
        """
        Load an empty board for manual setup.

        Args:
            rows: Number of rows
            cols: Number of columns
        """
        self.position = GamePosition(rows, cols)
        self.dead_stones.clear()
        self.sgf_properties = {}

        # Update weights to match board size
        weight_func = self.WEIGHT_SCHEMES[self.current_weight_name]
        self.current_weights = weight_func(rows, cols)

        # Update UI
        self.file_label.config(text="Empty board", foreground="gray")
        self.info_label.config(text=f"Board: {rows}×{cols}")
        self.clear_game_info()

        # Calculate and display scores
        self.update_scores()

        # Force canvas update before drawing
        self.canvas.update_idletasks()

        # Draw the board
        self.redraw_board()

    def load_sgf(self):
        """Load an SGF file."""
        file_path = filedialog.askopenfilename(
            title="Select SGF File",
            filetypes=[("SGF Files", "*.sgf"), ("All Files", "*.*")],
            initialdir=Path.cwd() / "data" if (Path.cwd() / "data").exists() else Path.cwd()
        )

        if not file_path:
            return

        try:
            # Read SGF file content to extract metadata
            with open(file_path, 'r', encoding='utf-8') as f:
                sgf_content = f.read()

            self.sgf_properties = parse_sgf_properties(sgf_content)
            self.position = read_sgf_file(file_path)
            self.dead_stones.clear()

            # Update weights to match board size
            rows, cols = self.position.board.rows, self.position.board.cols
            weight_func = self.WEIGHT_SCHEMES[self.current_weight_name]
            self.current_weights = weight_func(rows, cols)

            # Update UI
            self.file_label.config(text=Path(file_path).name, foreground="black")
            self.info_label.config(text=f"Board: {rows}×{cols}")
            self.update_game_info()

            # Calculate and display scores
            self.update_scores()

            # Force canvas update before drawing
            self.canvas.update_idletasks()

            # Draw the board
            self.redraw_board()

        except Exception as e:
            messagebox.showerror("Error Loading File", f"Failed to load SGF file:\n{str(e)}")

    def on_weight_changed(self):
        """Handle weight scheme selection change."""
        self.current_weight_name = self.weight_var.get()

        if self.position:
            rows, cols = self.position.board.rows, self.position.board.cols
            weight_func = self.WEIGHT_SCHEMES[self.current_weight_name]
            self.current_weights = weight_func(rows, cols)
            self.update_scores()
            self.redraw_board()

    def on_canvas_click(self, event):
        """Handle click on board canvas for dead stone marking."""
        if not self.position or not self.renderer:
            return

        # Convert canvas coordinates to board coordinates
        coord = self.renderer.canvas_to_board(event.x, event.y)
        if coord is None:
            return

        row, col = coord
        stone = self.position.board.get((row, col))

        if stone == Stone.EMPTY:
            return  # Empty intersection

        # Find the entire group
        group = find_group(self.position.board, (row, col))
        if group is None:
            return

        group_stones = group.stones

        # Toggle dead stone marking for the entire group
        if coord in self.dead_stones:
            # Remove entire group from dead stones
            self.dead_stones -= group_stones
        else:
            # Add entire group to dead stones
            self.dead_stones.update(group_stones)

        self.update_dead_stone_counts()
        self.update_scores()
        self.redraw_board()

    def on_canvas_resize(self, event):
        """Handle canvas resize event."""
        if self.position and self.renderer:
            # Force recalculation of layout on resize
            self.canvas.update_idletasks()
            self.redraw_board()

    def update_game_info(self):
        """Update game info display from SGF properties."""
        if not self.sgf_properties:
            self.clear_game_info()
            return

        # Clear all labels first
        for label in [self.event_label, self.date_label, self.black_player_label,
                     self.white_player_label, self.komi_label, self.result_label]:
            label.pack_forget()

        # Event
        event = self.sgf_properties.get('event', '')
        if event:
            self.event_label.config(text=f"Event: {event}", foreground="black")
            self.event_label.pack(anchor=tk.W)

        # Date
        date = self.sgf_properties.get('date', '')
        if date:
            self.date_label.config(text=f"Date: {date}", foreground="black")
            self.date_label.pack(anchor=tk.W)

        # Black player
        black_player = self.sgf_properties.get('black_player', '')
        black_rank = self.sgf_properties.get('black_rank', '')
        if black_player and black_rank:
            black_text = f"Black: {black_player} [{black_rank}]"
        elif black_player:
            black_text = f"Black: {black_player}"
        else:
            black_text = ""
        if black_text:
            self.black_player_label.config(text=black_text, foreground="black")
            self.black_player_label.pack(anchor=tk.W)

        # White player
        white_player = self.sgf_properties.get('white_player', '')
        white_rank = self.sgf_properties.get('white_rank', '')
        if white_player and white_rank:
            white_text = f"White: {white_player} [{white_rank}]"
        elif white_player:
            white_text = f"White: {white_player}"
        else:
            white_text = ""
        if white_text:
            self.white_player_label.config(text=white_text, foreground="black")
            self.white_player_label.pack(anchor=tk.W)

        # Komi
        komi = self.sgf_properties.get('komi', '')
        if komi:
            self.komi_label.config(text=f"Komi: {komi}", foreground="black")
            self.komi_label.pack(anchor=tk.W)

        # Result
        result = self.sgf_properties.get('result', '')
        if result:
            self.result_label.config(text=f"Result: {result}", foreground="black")
            self.result_label.pack(anchor=tk.W)

    def clear_game_info(self):
        """Clear game info display."""
        for label in [self.event_label, self.date_label, self.black_player_label,
                     self.white_player_label, self.komi_label, self.result_label]:
            label.pack_forget()

    def clear_dead_stones(self):
        """Clear all marked dead stones."""
        self.dead_stones.clear()
        self.update_dead_stone_counts()
        self.update_scores()
        self.redraw_board()

    def update_dead_stone_counts(self):
        """Update dead stone count labels by color."""
        if not self.position:
            return

        dead_black = 0
        dead_white = 0

        for row, col in self.dead_stones:
            stone = self.position.board.get((row, col))
            if stone == Stone.BLACK:
                dead_black += 1
            elif stone == Stone.WHITE:
                dead_white += 1

        self.dead_black_label.config(text=f"Dead black: {dead_black}")
        self.dead_white_label.config(text=f"Dead white: {dead_white}")

    def update_scores(self):
        """Calculate and update score display."""
        if not self.position or not self.current_weights:
            return

        # Create a modified position with dead stones removed
        if self.dead_stones:
            # Clone the position
            rows, cols = self.position.board.rows, self.position.board.cols
            modified_position = GamePosition(rows, cols)
            for row in range(rows):
                for col in range(cols):
                    if (row, col) not in self.dead_stones:
                        stone = self.position.board.get((row, col))
                        if stone != Stone.EMPTY:
                            modified_position.board.set((row, col), stone)
                    # Dead stones are left as EMPTY

            black_score, white_score = score(modified_position, self.current_weights)
        else:
            # No dead stones, use original position
            black_score, white_score = score(self.position, self.current_weights)

        # Update labels
        self.score_black_label.config(text=f"Black: {black_score:.1f}")
        self.score_white_label.config(text=f"White: {white_score:.1f}")

        if black_score > white_score:
            result = f"B+{black_score - white_score:.1f}"
        elif white_score > black_score:
            result = f"W+{white_score - black_score:.1f}"
        else:
            result = "Tie"

        self.score_result_label.config(text=f"Result: {result}")

    def redraw_board(self):
        """Redraw the board display."""
        if not self.position or not self.renderer:
            return

        self.canvas.delete("all")
        self.renderer.set_position(self.position)

        display_mode = self.display_var.get()

        if display_mode == "heatmap":
            # Draw heatmap first (as background)
            self.renderer.draw_heatmap(self.current_weights)
            # Then grid lines
            self.renderer.draw_board(show_coordinates=True)
            # Then stones on top
            self.renderer.draw_stones(dead_stones=self.dead_stones)
        else:
            # Draw board grid
            self.renderer.draw_board(show_coordinates=True)

            # Draw stones
            self.renderer.draw_stones(dead_stones=self.dead_stones)

            # Draw territory markers if requested (with dead stones consideration)
            if display_mode == "territory":
                self.renderer.draw_territory(dead_stones=self.dead_stones)


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = WeightedGoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
