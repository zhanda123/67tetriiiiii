"""The playfield grid: collision checks, locking, and line clearing."""

from .constants import COLS, ROWS, BUFFER_ROWS, PIECE_COLOR_GROUP


class Board:
    def __init__(self):
        self.total_rows = ROWS + BUFFER_ROWS
        self.grid = [[0] * COLS for _ in range(self.total_rows)]

    def is_inside(self, col: int, row: int) -> bool:
        return 0 <= col < COLS and 0 <= row < self.total_rows

    def is_free(self, col: int, row: int) -> bool:
        if not self.is_inside(col, row):
            return False
        return self.grid[row][col] == 0

    def piece_fits(self, piece, rotation=None, col=None, row=None) -> bool:
        for c, r in piece.cells(rotation, col, row):
            if not self.is_free(c, r):
                return False
        return True

    def lock_piece(self, piece):
        group = PIECE_COLOR_GROUP[piece.kind] + 1  # store as 1 or 2
        for c, r in piece.cells():
            if self.is_inside(c, r):
                self.grid[r][c] = group

    def full_rows(self):
        return [r for r in range(self.total_rows) if all(self.grid[r])]

    def clear_rows(self, rows):
        for r in rows:
            del self.grid[r]
            self.grid.insert(0, [0] * COLS)

    def is_row_visible(self, row: int) -> bool:
        return row >= BUFFER_ROWS
