"""Shared constants for the Tetris game: sizing, timing, colors."""

FPS = 60

COLS = 10
ROWS = 20
BUFFER_ROWS = 4  # hidden rows above the visible field, used for spawning

CELL = 24  # pixel size of one grid cell

# --- Timing (in frames, at FPS=60, matching the original NES feel) ---
DAS_DELAY = 16          # frames held before auto-shift kicks in
DAS_REPEAT = 6           # frames between repeated shifts while held
SOFT_DROP_FRAMES = 2     # frames per row while soft-dropping
LOCK_DELAY = 30          # frames a piece can rest before it locks
LINE_CLEAR_FRAMES = 20   # frames spent flashing a completed line

# Gravity table: frames it takes to fall one row, indexed by level.
# This mirrors the well-known NES Tetris speed curve.
def frames_per_row(level: int) -> int:
    table = {
        0: 48, 1: 43, 2: 38, 3: 33, 4: 28,
        5: 23, 6: 18, 7: 13, 8: 8, 9: 6,
        10: 5, 11: 5, 12: 5, 13: 4, 14: 4, 15: 4,
        16: 3, 17: 3, 18: 3,
    }
    if level in table:
        return table[level]
    if 19 <= level <= 28:
        return 2
    return 1


# --- Scoring ---
LINE_SCORES = {1: 40, 2: 100, 3: 300, 4: 1200}


def score_for_lines(lines: int, level: int) -> int:
    return LINE_SCORES.get(lines, 0) * (level + 1)


def lines_to_level(starting_level: int, total_lines: int) -> int:
    return starting_level + total_lines // 10


# --- Colors ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (120, 120, 128)
DARK_GRAY = (60, 60, 68)
BRICK = (96, 96, 104)
BRICK_DARK = (72, 72, 80)
CYAN_BORDER = (96, 220, 220)
PANEL_BG = (8, 8, 16)
TEXT_ORANGE = (216, 96, 40)

# Two-color palette per level, cycling every 10 levels, echoing the
# alternating look of the original game where each level re-colors
# the same falling shapes.
PALETTES = [
    ((92, 186, 255), (36, 96, 220)),    # 0 blue
    ((255, 110, 110), (200, 40, 40)),   # 1 red
    ((120, 226, 120), (40, 156, 40)),   # 2 green
    ((255, 210, 80), (206, 146, 24)),   # 3 gold
    ((214, 120, 255), (140, 40, 210)),  # 4 purple
    ((90, 226, 226), (30, 156, 156)),   # 5 teal
    ((255, 156, 80), (206, 100, 24)),   # 6 orange
    ((236, 236, 236), (160, 160, 160)), # 7 white/gray
    ((255, 110, 190), (206, 40, 130)),  # 8 pink
    ((140, 140, 255), (70, 70, 210)),   # 9 indigo
]

# Which palette slot (0 or 1) each piece type uses.
PIECE_COLOR_GROUP = {
    "I": 0, "O": 1, "T": 0, "S": 1, "Z": 0, "J": 1, "L": 0,
}
