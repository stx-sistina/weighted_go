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
from typing import Optional, Set, Tuple, List
from pathlib import Path

from ..core import (
    GamePosition, Stone, BoardSize,
    score, find_group, is_valid_position,
    read_sgf_file, parse_sgf_properties
)
from ..commons.weights import UniformWeight, CenterSquareWeight, CenterDiamondWeight
from ..commons.gui_colors import FILE_LABEL_NORMAL_COLOR, FILE_LABEL_EMPTY_COLOR
from .board_renderer import BoardRenderer


class WeightedGoApp:
    """Main application window for Weighted Go."""

    # Weight schemes available
    WEIGHT_SCHEMES = {
        "Uniform (Standard)": UniformWeight(),
        "Center: Square": CenterSquareWeight(),
        "Center: Diamond": CenterDiamondWeight(),
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

        # Editing state
        self.app_mode = "scoring"  # "scoring" or "editing"
        self.edit_mode_var = tk.StringVar(value="alternating")
        self.next_stone_color = Stone.BLACK
        self.ghost_stone_pos: Optional[Tuple[int, int]] = None
        self.invalid_groups: List[Set[Tuple[int, int]]] = []
        self.position_modified = False  # Track if SGF-loaded position was edited
        self.original_file_name = ""  # Store original SGF file name
        self.is_custom_game = False  # Track if this is a user-created position (not from SGF)
        self.edit_session_backup: Optional[GamePosition] = None  # Backup for revert
        self.last_drag_pos: Optional[Tuple[int, int]] = None  # Track last position for drag editing

        # Board renderer
        self.renderer: Optional[BoardRenderer] = None

        # UI components
        self.setup_ui()

        # Default: load uniform weights for 19x19 and create empty board
        self.current_weights = UniformWeight()
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
        """Set up the left control panel with scrolling support."""
        # Outer container for the control panel
        control_container = ttk.Frame(parent, relief=tk.RIDGE, borderwidth=2, width=250)
        control_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        control_container.grid_propagate(False)  # Fixed width
        control_container.rowconfigure(0, weight=1)
        control_container.columnconfigure(0, weight=1)

        # Canvas for scrolling
        canvas = tk.Canvas(control_container, highlightthickness=0)
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Scrollbar
        scrollbar = ttk.Scrollbar(control_container, orient=tk.VERTICAL, command=canvas.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        canvas.configure(yscrollcommand=scrollbar.set)

        # Inner frame that holds all controls
        control_frame = ttk.Frame(canvas, padding="5")
        canvas_window = canvas.create_window((0, 0), window=control_frame, anchor=tk.NW)

        # Configure column to expand
        control_frame.columnconfigure(0, weight=1)

        # Update scroll region when frame size changes
        def on_frame_configure(_event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            # Update the width of the frame to match canvas width
            canvas.itemconfig(canvas_window, width=event.width)

        control_frame.bind("<Configure>", on_frame_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        # Enable mouse wheel scrolling
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)  # Windows/MacOS

        # Store references for later use
        self.control_canvas = canvas
        self.control_scrollbar = scrollbar

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

        self.file_label = ttk.Label(control_frame, text="No file loaded", foreground=FILE_LABEL_EMPTY_COLOR,
                                   wraplength=220)
        self.file_label.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        ttk.Button(control_frame, text="Load SGF File", command=self.load_sgf).grid(
            row=row, column=0, sticky=(tk.W, tk.E), pady=5
        )
        row += 1

        # Edit Position button (shown in scoring mode)
        self.edit_button = ttk.Button(control_frame, text="Edit Position",
                                      command=self.enter_edit_mode)
        self.edit_button.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        self.edit_button_row = row
        row += 1

        # Editing Mode section (shown in editing mode, positioned right after game file)
        self.edit_separator = ttk.Separator(control_frame, orient=tk.HORIZONTAL)
        self.edit_separator_row = row

        self.edit_title_label = ttk.Label(control_frame, text="Editing Mode", font=("Helvetica", 12, "bold"))
        self.edit_title_row = row + 1

        self.edit_help_label = ttk.Label(control_frame, text="Click to place/remove stones", foreground=FILE_LABEL_EMPTY_COLOR)
        self.edit_help_row = row + 2

        # Radio buttons for editing modes - Alternating with clickable color toggle
        self.alternating_frame = ttk.Frame(control_frame)
        self.alternating_frame_row = row + 3

        self.edit_alternating_radio = ttk.Radiobutton(
            self.alternating_frame,
            text="Alternating",
            variable=self.edit_mode_var,
            value="alternating",
            command=self.on_edit_mode_changed
        )
        self.edit_alternating_radio.pack(side=tk.LEFT)

        # Clickable label for color toggle
        self.alternating_color_label = ttk.Label(
            self.alternating_frame,
            text="(Next: ●)",
            foreground="blue",
            cursor="hand2"
        )
        self.alternating_color_label.pack(side=tk.LEFT)
        self.alternating_color_label.bind("<Button-1>", lambda _: self.toggle_alternating_color())

        self.edit_black_radio = ttk.Radiobutton(
            control_frame,
            text="Black",
            variable=self.edit_mode_var,
            value="black",
            command=self.on_edit_mode_changed
        )
        self.edit_black_row = row + 4

        self.edit_white_radio = ttk.Radiobutton(
            control_frame,
            text="White",
            variable=self.edit_mode_var,
            value="white",
            command=self.on_edit_mode_changed
        )
        self.edit_white_row = row + 5

        self.edit_erase_radio = ttk.Radiobutton(
            control_frame,
            text="Erase",
            variable=self.edit_mode_var,
            value="erase",
            command=self.on_edit_mode_changed
        )
        self.edit_erase_row = row + 6

        # Done/Clear/Revert buttons (shown in editing mode)
        self.done_button = ttk.Button(control_frame, text="Done Editing",
                                      command=self.exit_edit_mode)
        self.done_button_row = row + 7

        self.clear_button = ttk.Button(control_frame, text="Clear Board",
                                       command=self.clear_board)
        self.clear_button_row = row + 8

        self.revert_button = ttk.Button(control_frame, text="Revert Changes",
                                        command=self.revert_changes)
        self.revert_button_row = row + 9

        self.set_size_button = ttk.Button(control_frame, text="Set Board Size",
                                          command=self.set_board_size)
        self.set_size_button_row = row + 10

        # Don't grid editing mode widgets yet - they'll be shown when entering edit mode
        # Keep track of all editing mode widgets for easy show/hide
        self.edit_mode_widgets = [
            (self.edit_separator, self.edit_separator_row),
            (self.edit_title_label, self.edit_title_row),
            (self.edit_help_label, self.edit_help_row),
            (self.alternating_frame, self.alternating_frame_row),
            (self.edit_black_radio, self.edit_black_row),
            (self.edit_white_radio, self.edit_white_row),
            (self.edit_erase_radio, self.edit_erase_row),
            (self.done_button, self.done_button_row),
            (self.clear_button, self.clear_button_row),
            (self.revert_button, self.revert_button_row),
            (self.set_size_button, self.set_size_button_row),
        ]

        # Game info section starts after editing section
        row += 11  # Skip past editing section (now includes Set Board Size button)

        # Game info section separator and title
        self.game_info_separator = ttk.Separator(control_frame, orient=tk.HORIZONTAL)
        self.game_info_separator.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10)
        self.game_info_separator_row = row
        row += 1

        self.game_info_title = ttk.Label(control_frame, text="Game Info", font=("Helvetica", 12, "bold"))
        self.game_info_title.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        self.game_info_title_row = row
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

        # Score display (scoring mode only)
        self.score_separator = ttk.Separator(control_frame, orient=tk.HORIZONTAL)
        self.score_separator.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10)
        row += 1

        self.score_title_label = ttk.Label(control_frame, text="Score", font=("Helvetica", 12, "bold"))
        self.score_title_label.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1

        score_frame = ttk.Frame(control_frame)
        score_frame.grid(row=row, column=0, sticky=(tk.W, tk.E))
        score_frame.columnconfigure(0, weight=1)
        self.score_frame = score_frame
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

        # Dead group removal (scoring mode only)
        self.dead_separator = ttk.Separator(control_frame, orient=tk.HORIZONTAL)
        self.dead_separator.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10)
        row += 1

        self.dead_title_label = ttk.Label(control_frame, text="Dead Stones", font=("Helvetica", 12, "bold"))
        self.dead_title_label.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1

        self.dead_help_label = ttk.Label(control_frame, text="Click stones to mark as dead", foreground=FILE_LABEL_EMPTY_COLOR)
        self.dead_help_label.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        self.dead_black_label = ttk.Label(control_frame, text="Dead black: 0")
        self.dead_black_label.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        self.dead_white_label = ttk.Label(control_frame, text="Dead white: 0")
        self.dead_white_label.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        self.dead_clear_button = ttk.Button(control_frame, text="Clear Dead Stones", command=self.clear_dead_stones)
        self.dead_clear_button.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=5)
        row += 1


        # Display mode (scoring mode only)
        self.display_separator = ttk.Separator(control_frame, orient=tk.HORIZONTAL)
        self.display_separator.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=10)
        row += 1

        self.display_title_label = ttk.Label(control_frame, text="Display Mode", font=("Helvetica", 12, "bold"))
        self.display_title_label.grid(row=row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        row += 1

        self.display_var = tk.StringVar(value="stones")
        self.display_stones_radio = ttk.Radiobutton(
            control_frame,
            text="Stones Only",
            variable=self.display_var,
            value="stones",
            command=self.redraw_board
        )
        self.display_stones_radio.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        self.display_territory_radio = ttk.Radiobutton(
            control_frame,
            text="Territory Markers",
            variable=self.display_var,
            value="territory",
            command=self.redraw_board
        )
        self.display_territory_radio.grid(row=row, column=0, sticky=(tk.W, tk.E))
        row += 1

        self.display_heatmap_radio = ttk.Radiobutton(
            control_frame,
            text="Weight Heatmap",
            variable=self.display_var,
            value="heatmap",
            command=self.redraw_board
        )
        self.display_heatmap_radio.grid(row=row, column=0, sticky=(tk.W, tk.E))
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

        # Bind drag events for editing mode
        self.canvas.bind("<B1-Motion>", self.on_canvas_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_canvas_release)

        # Bind mouse motion for ghost stones
        self.canvas.bind("<Motion>", self.on_canvas_motion)
        self.canvas.bind("<Leave>", self.on_canvas_leave)

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
        self.current_weights = self.WEIGHT_SCHEMES[self.current_weight_name]

        # Update UI
        self.file_label.config(text="Empty board", foreground=FILE_LABEL_EMPTY_COLOR)
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
            self.position, last_move_color = read_sgf_file(file_path)
            self.dead_stones.clear()

            # Track original filename for modification detection
            self.original_file_name = Path(file_path).name
            self.position_modified = False
            self.is_custom_game = False  # Clear custom game flag when loading SGF

            # Infer next stone color from last move (opponent of last move)
            if last_move_color is not None:
                self.next_stone_color = last_move_color.opponent()
            else:
                self.next_stone_color = Stone.BLACK  # Default if no moves

            # Update weights to match board size
            rows, cols = self.position.board.rows, self.position.board.cols
            self.current_weights = self.WEIGHT_SCHEMES[self.current_weight_name]

            # Update UI
            self.file_label.config(text=self.original_file_name, foreground=FILE_LABEL_NORMAL_COLOR)
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
            self.current_weights = self.WEIGHT_SCHEMES[self.current_weight_name]
            self.update_scores()
            self.redraw_board()

    def on_canvas_click(self, event):
        """Handle click on board canvas."""
        if not self.position or not self.renderer:
            return

        # Convert canvas coordinates to board coordinates
        coord = self.renderer.canvas_to_board(event.x, event.y)
        if coord is None:
            return

        # Clear invalid group highlighting if any
        if self.invalid_groups:
            self.invalid_groups.clear()
            self.redraw_board()

        # Dispatch based on app mode
        if self.app_mode == "editing":
            # Set drag tracking for the clicked position (fixes first intersection not updating during drag)
            mode = self.edit_mode_var.get()
            if mode != "alternating":  # Drag modes
                self.last_drag_pos = coord
            self.handle_edit_click(coord)
        else:  # scoring mode
            self.handle_dead_stone_click(coord)

    def handle_dead_stone_click(self, coord: Tuple[int, int]):
        """Handle click for dead stone marking (scoring mode)."""
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

        has_content = False

        # Event
        event = self.sgf_properties.get('event', '')
        if event:
            self.event_label.config(text=f"Event: {event}", foreground=FILE_LABEL_NORMAL_COLOR)
            self.event_label.pack(anchor=tk.W)
            has_content = True

        # Date
        date = self.sgf_properties.get('date', '')
        if date:
            self.date_label.config(text=f"Date: {date}", foreground=FILE_LABEL_NORMAL_COLOR)
            self.date_label.pack(anchor=tk.W)
            has_content = True

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
            self.black_player_label.config(text=black_text, foreground=FILE_LABEL_NORMAL_COLOR)
            self.black_player_label.pack(anchor=tk.W)
            has_content = True

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
            self.white_player_label.config(text=white_text, foreground=FILE_LABEL_NORMAL_COLOR)
            self.white_player_label.pack(anchor=tk.W)
            has_content = True

        # Komi
        komi = self.sgf_properties.get('komi', '')
        if komi:
            self.komi_label.config(text=f"Komi: {komi}", foreground=FILE_LABEL_NORMAL_COLOR)
            self.komi_label.pack(anchor=tk.W)
            has_content = True

        # Result
        result = self.sgf_properties.get('result', '')
        if result:
            self.result_label.config(text=f"Result: {result}", foreground=FILE_LABEL_NORMAL_COLOR)
            self.result_label.pack(anchor=tk.W)
            has_content = True

        # Show or hide the game info section based on content
        if has_content:
            self.game_info_separator.grid()
            self.game_info_title.grid()
            self.game_info_frame.grid()
        else:
            self.game_info_separator.grid_remove()
            self.game_info_title.grid_remove()
            self.game_info_frame.grid_remove()

    def clear_game_info(self):
        """Clear game info display and hide section."""
        for label in [self.event_label, self.date_label, self.black_player_label,
                     self.white_player_label, self.komi_label, self.result_label]:
            label.pack_forget()
        # Hide section title, separator, and frame
        self.game_info_separator.grid_remove()
        self.game_info_title.grid_remove()
        self.game_info_frame.grid_remove()

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

    def enter_edit_mode(self):
        """Switch to editing mode."""
        self.app_mode = "editing"
        self.dead_stones.clear()
        self.invalid_groups.clear()
        self.ghost_stone_pos = None

        # Save backup for revert (position + metadata)
        self.edit_session_backup = GamePosition(self.position.board.rows, self.position.board.cols)
        for i in range(self.position.board.rows):
            for j in range(self.position.board.cols):
                stone = self.position.board.get((i, j))
                self.edit_session_backup.board.set((i, j), stone)

        # Also backup SGF metadata for proper revert after clear
        self.backup_original_file_name = self.original_file_name
        self.backup_next_stone_color = self.next_stone_color

        # Hide scoring controls
        self.edit_button.grid_remove()
        self.score_separator.grid_remove()
        self.score_title_label.grid_remove()
        self.score_frame.grid_remove()
        self.dead_separator.grid_remove()
        self.dead_title_label.grid_remove()
        self.dead_help_label.grid_remove()
        self.dead_black_label.grid_remove()
        self.dead_white_label.grid_remove()
        self.dead_clear_button.grid_remove()

        # Hide territory markers option (invalid positions can't show territory)
        # Keep Display Mode section visible (stones/heatmap still work)
        self.display_territory_radio.grid_remove()

        # Switch to stones view if currently showing territory
        if self.display_var.get() == "territory":
            self.display_var.set("stones")

        # Show editing mode section (positioned right after game file)
        for widget, widget_row in self.edit_mode_widgets:
            if widget == self.edit_separator:
                widget.grid(row=widget_row, column=0, sticky=(tk.W, tk.E), pady=10)
            elif widget == self.edit_title_label:
                widget.grid(row=widget_row, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
            elif widget in (self.edit_help_label, self.alternating_frame,
                           self.edit_black_radio, self.edit_white_radio, self.edit_erase_radio):
                widget.grid(row=widget_row, column=0, sticky=(tk.W, tk.E))
            elif widget in (self.done_button, self.clear_button, self.revert_button, self.set_size_button):
                widget.grid(row=widget_row, column=0, sticky=(tk.W, tk.E), pady=5)

        self.update_edit_mode_label()
        self.redraw_board()

    def exit_edit_mode(self):
        """Validate and exit editing mode."""
        # Validate position
        if not is_valid_position(self.position):
            # Find invalid groups
            self.invalid_groups = self.find_invalid_groups()
            messagebox.showerror("Invalid Position",
                f"Position has {len(self.invalid_groups)} group(s) with no liberties.\n"
                "Invalid groups are highlighted in red.")
            self.redraw_board()
            return

        # Valid - enter scoring mode
        self.app_mode = "scoring"
        self.ghost_stone_pos = None
        self.invalid_groups.clear()

        # Check if this is a custom game (has stones but no SGF origin)
        if not self.original_file_name:
            # Count stones to see if position is non-empty
            black_count, white_count = self.position.board.count_stones()
            if black_count > 0 or white_count > 0:
                self.is_custom_game = True
                self.update_file_label()

        # Show scoring controls
        self.edit_button.grid(row=self.edit_button_row, column=0, sticky=(tk.W, tk.E), pady=5)
        self.score_separator.grid()
        self.score_title_label.grid()
        self.score_frame.grid()
        self.dead_separator.grid()
        self.dead_title_label.grid()
        self.dead_help_label.grid()
        self.dead_black_label.grid()
        self.dead_white_label.grid()
        self.dead_clear_button.grid()

        # Show territory markers option again
        self.display_territory_radio.grid()

        # Hide editing mode section
        for widget, _ in self.edit_mode_widgets:
            widget.grid_remove()

        # Clear backup
        self.edit_session_backup = None

        self.update_scores()
        self.redraw_board()

    def handle_edit_click(self, coord: Tuple[int, int]):
        """Handle click in editing mode."""
        mode = self.edit_mode_var.get()
        row, col = coord
        current_stone = self.position.board.get(coord)

        # Track if we actually made a change
        changed = False

        if mode == "alternating":
            # Use validated placement
            if current_stone != Stone.EMPTY:
                return  # Can't place on occupied position

            success = self.position.place_stone(coord, self.next_stone_color)
            if success:
                changed = True
                # Alternate color
                self.next_stone_color = self.next_stone_color.opponent()
                self.update_edit_mode_label()
            # If failed (suicide), ghost stone will show red X

        elif mode == "black":
            # Direct manipulation
            if current_stone == Stone.BLACK:
                self.position.board.set(coord, Stone.EMPTY)  # Remove
                changed = True
            elif current_stone != Stone.BLACK:
                self.position.board.set(coord, Stone.BLACK)  # Place
                changed = True

        elif mode == "white":
            if current_stone == Stone.WHITE:
                self.position.board.set(coord, Stone.EMPTY)
                changed = True
            elif current_stone != Stone.WHITE:
                self.position.board.set(coord, Stone.WHITE)
                changed = True

        elif mode == "erase":
            if current_stone != Stone.EMPTY:
                self.position.board.set(coord, Stone.EMPTY)
                changed = True

        # Mark position as modified if we changed something and it's an SGF-loaded position
        if changed and self.original_file_name:
            if not self.position_modified:
                self.position_modified = True
                self.update_file_label()

        self.redraw_board()

    def on_canvas_drag(self, event):
        """Handle drag for continuous stone placement."""
        if self.app_mode != "editing":
            return

        mode = self.edit_mode_var.get()
        if mode == "alternating":  # No drag in alternating
            return

        coord = self.renderer.canvas_to_board(event.x, event.y)
        if coord is None:
            return

        # Only edit if we moved to a different position (avoid redundant edits)
        if coord == self.last_drag_pos:
            return

        self.last_drag_pos = coord
        self.handle_edit_click(coord)

    def on_canvas_motion(self, event):
        """Handle mouse motion for ghost stone preview."""
        if self.app_mode != "editing" or not self.position or not self.renderer:
            if self.ghost_stone_pos is not None:
                self.ghost_stone_pos = None
                self.redraw_board()
            return

        coord = self.renderer.canvas_to_board(event.x, event.y)

        # Update ghost stone position if changed
        if coord != self.ghost_stone_pos:
            self.ghost_stone_pos = coord
            self.redraw_board()

    def on_canvas_release(self, _event):
        """Handle mouse button release - reset drag tracking."""
        self.last_drag_pos = None

    def on_canvas_leave(self, event):
        """Clear ghost stone when mouse leaves canvas."""
        if self.ghost_stone_pos is not None:
            self.ghost_stone_pos = None
            if self.app_mode == "editing":
                self.redraw_board()
        # Also reset drag tracking when leaving canvas
        self.last_drag_pos = None

    def clear_board(self):
        """Clear all stones from the board."""
        if messagebox.askyesno("Clear Board", "Remove all stones from the board?"):
            for i in range(self.position.board.rows):
                for j in range(self.position.board.cols):
                    self.position.board.set((i, j), Stone.EMPTY)
            self.invalid_groups.clear()

            # Clear all game metadata
            self.original_file_name = ""
            self.position_modified = False
            self.is_custom_game = False
            self.file_label.config(text="Empty board", foreground=FILE_LABEL_EMPTY_COLOR)

            # Clear SGF properties and game info
            self.sgf_properties = {}
            self.clear_game_info()

            self.redraw_board()

    def revert_changes(self):
        """Revert position to the state when entering edit mode."""
        if not self.edit_session_backup:
            return

        if messagebox.askyesno("Revert Changes", "Revert all changes made in this editing session?"):
            # Restore from backup
            for i in range(self.position.board.rows):
                for j in range(self.position.board.cols):
                    stone = self.edit_session_backup.board.get((i, j))
                    self.position.board.set((i, j), stone)

            # Restore SGF metadata (fixes issue when reverting after clear board)
            self.original_file_name = self.backup_original_file_name
            self.next_stone_color = self.backup_next_stone_color

            self.invalid_groups.clear()
            self.position_modified = False
            self.update_file_label()
            self.update_edit_mode_label()  # Update color indicator
            self.redraw_board()

    def set_board_size(self):
        """Set a new board size (clears board and metadata)."""
        # Create dialog for board size input
        dialog = tk.Toplevel(self.root)
        dialog.title("Set Board Size")
        dialog.geometry("300x150")
        dialog.transient(self.root)
        dialog.grab_set()

        # Center the dialog
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Instructions
        ttk.Label(dialog, text="Enter board size (1-25)", font=("Helvetica", 12)).pack(pady=10)
        ttk.Label(dialog, text="Format: '19' for square or '13x9' for non-square",
                 wraplength=280).pack(pady=5)

        # Entry field
        entry_frame = ttk.Frame(dialog)
        entry_frame.pack(pady=10)
        size_entry = ttk.Entry(entry_frame, width=15)
        size_entry.pack()
        size_entry.insert(0, "19")
        size_entry.focus()

        def apply_size():
            size_str = size_entry.get().strip()
            try:
                # Parse board size
                if 'x' in size_str.lower():
                    parts = size_str.lower().split('x')
                    if len(parts) != 2:
                        raise ValueError("Invalid format")
                    rows, cols = int(parts[0]), int(parts[1])
                else:
                    rows = cols = int(size_str)

                # Validate range
                if not (1 <= rows <= 25 and 1 <= cols <= 25):
                    raise ValueError("Size must be between 1 and 25")

                # Confirm if board has stones
                if self.position:
                    black_count, white_count = self.position.board.count_stones()
                    if black_count > 0 or white_count > 0:
                        if not messagebox.askyesno("Clear Board",
                            f"Changing board size will clear all stones and metadata.\nContinue?",
                            parent=dialog):
                            return

                # Create new board
                self.load_empty_board(rows, cols)

                # Clear all metadata
                self.original_file_name = ""
                self.position_modified = False
                self.is_custom_game = False
                self.sgf_properties = {}
                self.clear_game_info()
                self.file_label.config(text="Empty board", foreground=FILE_LABEL_EMPTY_COLOR)

                # Clear invalid groups
                self.invalid_groups.clear()

                # Reset backup since board size changed
                self.edit_session_backup = None

                self.redraw_board()
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Invalid Size",
                    f"Please enter a valid board size (1-25).\nFormat: '19' or '13x9'",
                    parent=dialog)

        # Buttons
        button_frame = ttk.Frame(dialog)
        button_frame.pack(pady=10)
        ttk.Button(button_frame, text="OK", command=apply_size).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side=tk.LEFT, padx=5)

        # Bind Enter key
        size_entry.bind("<Return>", lambda _: apply_size())

    def on_edit_mode_changed(self):
        """Handle editing mode change."""
        self.update_edit_mode_label()
        self.redraw_board()

    def update_edit_mode_label(self):
        """Update the alternating mode label with current color."""
        color_symbol = "●" if self.next_stone_color == Stone.BLACK else "○"
        self.alternating_color_label.config(text=f"(Next: {color_symbol})")

    def toggle_alternating_color(self):
        """Reverse the next stone color in alternating mode."""
        self.next_stone_color = self.next_stone_color.opponent()
        self.update_edit_mode_label()
        self.redraw_board()  # Update ghost stone color

    def update_file_label(self):
        """Update file label to show modification status."""
        if self.position_modified and self.original_file_name:
            self.file_label.config(text=f"<Modified> {self.original_file_name}", foreground=FILE_LABEL_NORMAL_COLOR)
        elif self.original_file_name:
            self.file_label.config(text=self.original_file_name, foreground=FILE_LABEL_NORMAL_COLOR)
        elif self.is_custom_game:
            self.file_label.config(text="Custom game", foreground=FILE_LABEL_NORMAL_COLOR)
        else:
            self.file_label.config(text="Empty board", foreground=FILE_LABEL_EMPTY_COLOR)

    def find_invalid_groups(self) -> List[Set[Tuple[int, int]]]:
        """Find all groups with no liberties."""
        invalid = []
        checked = set()

        for i in range(self.position.board.rows):
            for j in range(self.position.board.cols):
                pos = (i, j)
                stone = self.position.board.get(pos)

                if stone != Stone.EMPTY and pos not in checked:
                    group = find_group(self.position.board, pos)
                    if group and len(group.liberties) == 0:
                        invalid.append(group.stones)
                    if group:
                        checked.update(group.stones)

        return invalid

    def get_ghost_color(self) -> Stone:
        """Get the color for ghost stone based on editing mode."""
        mode = self.edit_mode_var.get()
        if mode == "alternating":
            return self.next_stone_color
        elif mode == "black":
            return Stone.BLACK
        elif mode == "white":
            return Stone.WHITE
        else:  # erase
            return Stone.EMPTY

    def is_ghost_illegal(self) -> bool:
        """Check if ghost stone position would be suicide (alternating mode only)."""
        if self.edit_mode_var.get() != "alternating":
            return False

        if not self.ghost_stone_pos:
            return False

        # Only show red X for suicide moves, not for occupied positions
        current = self.position.board.get(self.ghost_stone_pos)
        if current != Stone.EMPTY:
            return False  # Don't show red X for occupied - just don't show ghost

        # Test if move would be suicide
        test_pos = GamePosition(self.position.board.rows, self.position.board.cols)
        test_pos.board = self.position.board.copy()
        return not test_pos.place_stone(self.ghost_stone_pos, self.next_stone_color)

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

        # Draw board grid
        self.renderer.draw_board(show_coordinates=True)

        # In editing mode, draw invalid group highlights
        if self.app_mode == "editing" and self.invalid_groups:
            self.renderer.draw_invalid_groups(self.invalid_groups)

        # Draw stones
        if self.app_mode == "editing":
            self.renderer.draw_stones()
        else:
            self.renderer.draw_stones(dead_stones=self.dead_stones)

        # Draw territory only in scoring mode
        if self.app_mode == "scoring" and display_mode == "territory":
            self.renderer.draw_territory(dead_stones=self.dead_stones)

        # Draw ghost stone in editing mode
        if self.app_mode == "editing" and self.ghost_stone_pos:
            # In alternating mode, don't show ghost on occupied positions
            if self.edit_mode_var.get() == "alternating":
                current = self.position.board.get(self.ghost_stone_pos)
                if current != Stone.EMPTY:
                    return  # Skip ghost stone on occupied positions

            is_illegal = self.is_ghost_illegal()
            self.renderer.draw_ghost_stone(
                self.ghost_stone_pos,
                self.get_ghost_color(),
                show_illegal=is_illegal
            )


def main():
    """Run the GUI application."""
    root = tk.Tk()
    app = WeightedGoApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
