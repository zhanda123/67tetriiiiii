"""Core game state machine: input handling, gravity, scoring, levels."""

from .board import Board
from .pieces import Piece, Randomizer, PIECE_TYPES
from .constants import (
    COLS, BUFFER_ROWS, DAS_DELAY, DAS_REPEAT, SOFT_DROP_FRAMES,
    LOCK_DELAY, LINE_CLEAR_FRAMES, MAX_STARTING_LEVEL, frames_per_row,
    score_for_lines, lines_to_level,
)

MENU = "menu"
PLAYING = "playing"
PAUSED = "paused"
LINE_CLEAR = "line_clear"
GAME_OVER = "game_over"


class Game:
    def __init__(self, piece_source=None):
        # piece_source: optional zero-arg callable returning the next piece
        # kind, e.g. a SharedSequence cursor so two Game instances in
        # 2-player mode draw from the exact same piece order. Defaults to
        # this instance's own independent Randomizer.
        self.state = MENU
        self.starting_level = 1
        self.player_mode = 1  # UI-only selection (1 or 2 players) used by the menu screen
        self._piece_source = piece_source
        self.randomizer = Randomizer()
        self.reset()

    def _draw_piece(self) -> str:
        if self._piece_source is not None:
            return self._piece_source()
        return self.randomizer.next()

    def reset(self):
        self.board = Board()
        self.level = self.starting_level
        self.score = 0
        self.top_score = getattr(self, "top_score", 0)
        self.lines = 0
        self.stats = {k: 0 for k in PIECE_TYPES}
        if self._piece_source is None:
            self.randomizer = Randomizer()
        self.next_kind = self._draw_piece()
        self.piece = None
        self.gravity_timer = 0
        self.lock_timer = 0
        self.landed = False
        self.das_dir = 0
        self.das_timer = 0
        self.clearing_rows = []
        self.clear_timer = 0
        self.game_over_fill_row = 0
        self.game_over_timer = 0
        self._spawn_piece()

    # -- setup -----------------------------------------------------
    def start(self, level: int):
        self.starting_level = max(0, min(MAX_STARTING_LEVEL, level))
        self.reset()
        self.state = PLAYING

    def _spawn_piece(self):
        kind = self.next_kind
        self.next_kind = self._draw_piece()
        self.stats[kind] += 1
        piece = Piece(kind, col=3, row=0)
        if not self.board.piece_fits(piece):
            self.state = GAME_OVER
            self.game_over_fill_row = 0
            self.game_over_timer = 0
            self.top_score = max(self.top_score, self.score)
            return
        self.piece = piece
        self.gravity_timer = 0
        self.lock_timer = 0
        self.landed = False

    # -- movement ----------------------------------------------------
    def _can_move(self, dx, dy, drot=0):
        p = self.piece
        rotation = (p.rotation + drot) % 4
        return self.board.piece_fits(p, rotation=rotation, col=p.col + dx, row=p.row + dy)

    def move(self, dx):
        if self._can_move(dx, 0):
            self.piece.col += dx
            self._refresh_landed()
            return True
        return False

    def rotate(self, direction):
        if self._can_move(0, 0, direction):
            self.piece.rotation = (self.piece.rotation + direction) % 4
            self._refresh_landed()
            return True
        return False

    def _refresh_landed(self):
        self.landed = not self._can_move(0, 1)
        if self.landed:
            self.lock_timer = 0

    def soft_drop_step(self):
        if self._can_move(0, 1):
            self.piece.row += 1
            return True
        return False

    # -- per-frame update ---------------------------------------------
    def process_input(self, left, right, soft_drop):
        if self.state != PLAYING:
            return
        direction = 0
        if left and not right:
            direction = -1
        elif right and not left:
            direction = 1

        if direction != 0:
            if direction != self.das_dir:
                self.das_dir = direction
                self.das_timer = 0
                self.move(direction)
            else:
                self.das_timer += 1
                if self.das_timer >= DAS_DELAY:
                    if (self.das_timer - DAS_DELAY) % DAS_REPEAT == 0:
                        self.move(direction)
        else:
            self.das_dir = 0
            self.das_timer = 0

        self._soft_drop_held = soft_drop

    def update(self):
        if self.state == LINE_CLEAR:
            self._update_line_clear()
            return
        if self.state == GAME_OVER:
            self._update_game_over_animation()
            return
        if self.state != PLAYING:
            return

        drop_interval = SOFT_DROP_FRAMES if getattr(self, "_soft_drop_held", False) else frames_per_row(self.level)
        self.gravity_timer += 1
        if self.gravity_timer >= drop_interval:
            self.gravity_timer = 0
            if not self.soft_drop_step():
                # Piece can't fall any further: it locks on this tick,
                # matching the original game's lack of an infinite-slide
                # lock-reset grace period.
                self._lock_and_advance()
            else:
                self._refresh_landed()

    def _lock_and_advance(self):
        self.board.lock_piece(self.piece)
        full = self.board.full_rows()
        if full:
            self.clearing_rows = full
            self.clear_timer = 0
            self.state = LINE_CLEAR
        else:
            self._spawn_piece()

    def _update_line_clear(self):
        self.clear_timer += 1
        if self.clear_timer >= LINE_CLEAR_FRAMES:
            n = len(self.clearing_rows)
            self.board.clear_rows(self.clearing_rows)
            self.lines += n
            self.score += score_for_lines(n, self.level)
            self.level = lines_to_level(self.starting_level, self.lines)
            self.clearing_rows = []
            self.top_score = max(self.top_score, self.score)
            self.state = PLAYING
            self._spawn_piece()

    def _update_game_over_animation(self):
        self.game_over_timer += 1
        if self.game_over_timer % 2 == 0 and self.game_over_fill_row < self.board.total_rows:
            row = self.game_over_fill_row
            for c in range(COLS):
                self.board.grid[row][c] = 2 if c % 2 == 0 else 1
            self.game_over_fill_row += 1

    def ghost_col_row(self):
        """Not used for rendering by default (classic NES has no ghost
        piece) but kept available for potential UI toggles."""
        p = self.piece
        row = p.row
        while self.board.piece_fits(p, col=p.col, row=row + 1):
            row += 1
        return row
