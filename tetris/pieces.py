"""Tetromino shape definitions and the piece bag/randomizer."""

import random

# Each shape is a list of 4 rotation states. Every state is a tuple of
# (x, y) cell offsets within a 4x4 bounding box.
SHAPES = {
    "I": [
        [(0, 1), (1, 1), (2, 1), (3, 1)],
        [(2, 0), (2, 1), (2, 2), (2, 3)],
        [(0, 2), (1, 2), (2, 2), (3, 2)],
        [(1, 0), (1, 1), (1, 2), (1, 3)],
    ],
    "O": [
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (2, 1)],
    ],
    "T": [
        [(1, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (1, 2)],
        [(1, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "S": [
        [(1, 0), (2, 0), (0, 1), (1, 1)],
        [(1, 0), (1, 1), (2, 1), (2, 2)],
        [(1, 1), (2, 1), (0, 2), (1, 2)],
        [(0, 0), (0, 1), (1, 1), (1, 2)],
    ],
    "Z": [
        [(0, 0), (1, 0), (1, 1), (2, 1)],
        [(2, 0), (1, 1), (2, 1), (1, 2)],
        [(0, 1), (1, 1), (1, 2), (2, 2)],
        [(1, 0), (0, 1), (1, 1), (0, 2)],
    ],
    "J": [
        [(0, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (2, 0), (1, 1), (1, 2)],
        [(0, 1), (1, 1), (2, 1), (2, 2)],
        [(1, 0), (1, 1), (0, 2), (1, 2)],
    ],
    "L": [
        [(2, 0), (0, 1), (1, 1), (2, 1)],
        [(1, 0), (1, 1), (1, 2), (2, 2)],
        [(0, 1), (1, 1), (2, 1), (0, 2)],
        [(0, 0), (1, 0), (1, 1), (1, 2)],
    ],
}

PIECE_TYPES = list(SHAPES.keys())


class Piece:
    def __init__(self, kind: str, col: int = 3, row: int = 0):
        self.kind = kind
        self.rotation = 0
        self.col = col
        self.row = row

    def cells(self, rotation=None, col=None, row=None):
        rotation = self.rotation if rotation is None else rotation
        col = self.col if col is None else col
        row = self.row if row is None else row
        return [(col + dx, row + dy) for dx, dy in SHAPES[self.kind][rotation % 4]]

    def clone(self):
        p = Piece(self.kind, self.col, self.row)
        p.rotation = self.rotation
        return p


class Randomizer:
    """Approximates the classic NES randomizer: uniform random choice,
    with a re-roll if the same piece as the previous one is drawn twice
    in a row, which keeps long repeats rare without using a strict bag."""

    def __init__(self, rng: random.Random = None):
        self.rng = rng or random.Random()
        self.previous = None

    def next(self) -> str:
        choice = self.rng.choice(PIECE_TYPES)
        if choice == self.previous:
            choice = self.rng.choice(PIECE_TYPES)
        self.previous = choice
        return choice


class SharedSequence:
    """One piece order shared by both players in 2-player mode, so a
    fast player and a slow player still see the exact same Nth piece --
    each side pulls by its own piece count rather than by call order,
    so speed differences can't desync them."""

    def __init__(self):
        self._randomizer = Randomizer()
        self._cache = []

    def _at(self, index: int) -> str:
        while len(self._cache) <= index:
            self._cache.append(self._randomizer.next())
        return self._cache[index]

    def cursor(self):
        """Returns a fresh zero-arg callable with its own position in
        this shared sequence, starting at index 0."""
        state = {"index": 0}

        def _next():
            kind = self._at(state["index"])
            state["index"] += 1
            return kind

        return _next
