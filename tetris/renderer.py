"""Drawing code: recreates the classic look of blocky brick borders,
a bordered playfield, and NEXT / SCORE / LEVEL / STATISTICS panels."""

import pygame

from .constants import (
    COLS, ROWS, BUFFER_ROWS, CELL, WHITE, BLACK, GRAY, DARK_GRAY,
    BRICK, BRICK_DARK, CYAN_BORDER, PANEL_BG, TEXT_ORANGE, PALETTES,
    PIECE_COLOR_GROUP,
)
from .pieces import SHAPES, PIECE_TYPES
from . import game as game_module

MARGIN = 16
BORDER = 10
LEFT_PANEL_W = 190
RIGHT_PANEL_W = 190
TOP_BAR_H = 50

PLAYFIELD_W = COLS * CELL
PLAYFIELD_H = ROWS * CELL

PLAYFIELD_X = MARGIN + LEFT_PANEL_W + MARGIN + BORDER
PLAYFIELD_Y = MARGIN + TOP_BAR_H + MARGIN + BORDER

WIDTH = PLAYFIELD_X + PLAYFIELD_W + BORDER + MARGIN + RIGHT_PANEL_W + MARGIN
HEIGHT = PLAYFIELD_Y + PLAYFIELD_H + BORDER + MARGIN

LEFT_PANEL_RECT = pygame.Rect(MARGIN, PLAYFIELD_Y - BORDER, LEFT_PANEL_W, PLAYFIELD_H + 2 * BORDER)
RIGHT_PANEL_X = PLAYFIELD_X + PLAYFIELD_W + BORDER + MARGIN


class PixelFont:
    """Renders text tiny with anti-aliasing off, then scales it up with
    nearest-neighbor so every glyph edge stays hard-pixelated -- the
    blocky low-res look of the original game's on-screen text, rather
    than a smooth modern monospace font."""

    def __init__(self, base_size, scale=3, bold=True):
        name = pygame.font.match_font("couriernew,consolas,dejavusansmono,monospace")
        self.font = pygame.font.Font(name, base_size)
        self.font.set_bold(bold)
        self.scale = scale

    def render(self, text, antialias=False, color=WHITE):
        surf = self.font.render(text, False, color)
        w, h = surf.get_size()
        return pygame.transform.scale(surf, (max(1, w * self.scale), max(1, h * self.scale)))

    def get_height(self):
        return self.font.get_height() * self.scale


class Fonts:
    def __init__(self):
        self.huge = PixelFont(22, scale=2)
        self.big = PixelFont(15, scale=2)
        self.med = PixelFont(11, scale=2)
        self.small = PixelFont(9, scale=2)


def draw_brick_background(surface):
    surface.fill(DARK_GRAY)
    brick_w, brick_h = 20, 12
    for row, y in enumerate(range(0, HEIGHT, brick_h)):
        offset = (brick_w // 2) if row % 2 else 0
        for x in range(-brick_w, WIDTH + brick_w, brick_w):
            rect = pygame.Rect(x + offset, y, brick_w - 2, brick_h - 2)
            pygame.draw.rect(surface, BRICK, rect)
            pygame.draw.rect(surface, BRICK_DARK, rect, 1)


def draw_bordered_box(surface, rect, title=None, fonts=None, title_color=CYAN_BORDER):
    outer = rect.inflate(BORDER * 2, BORDER * 2)
    pygame.draw.rect(surface, CYAN_BORDER, outer, border_radius=4)
    pygame.draw.rect(surface, BLACK, outer.inflate(-6, -6), border_radius=3)
    pygame.draw.rect(surface, PANEL_BG, rect)
    if title and fonts:
        label = fonts.small.render(title, True, title_color)
        surface.blit(label, (rect.x + 6, rect.y + 4))


def draw_block(surface, px, py, size, colors):
    light, dark = colors
    pygame.draw.rect(surface, dark, (px, py, size, size))
    inner = size - 4
    if inner > 0:
        pygame.draw.rect(surface, light, (px + 2, py + 2, inner, inner))
    hl = max(3, size // 3)
    pygame.draw.rect(surface, WHITE, (px + 3, py + 3, hl, hl))
    pygame.draw.rect(surface, BLACK, (px, py, size, size), 1)


def _shade(color, factor=0.55):
    return tuple(max(0, int(c * factor)) for c in color)


def _palette_for(level, kind):
    pal = PALETTES[level % len(PALETTES)]
    group = PIECE_COLOR_GROUP[kind]
    color = pal[group]
    return (color, _shade(color))


def _colors_for_cell(level, value):
    pal = PALETTES[level % len(PALETTES)]
    color = pal[value - 1]
    return (color, _shade(color))


def draw_playfield(surface, game, fonts, x=PLAYFIELD_X, y=PLAYFIELD_Y):
    rect = pygame.Rect(x, y, PLAYFIELD_W, PLAYFIELD_H)
    draw_bordered_box(surface, rect)

    board = game.board
    flashing = game.state == game_module.LINE_CLEAR and (game.clear_timer // 3) % 2 == 0

    for r in range(BUFFER_ROWS, board.total_rows):
        for c in range(COLS):
            value = board.grid[r][c]
            if value == 0:
                continue
            px = x + c * CELL
            py = y + (r - BUFFER_ROWS) * CELL
            if flashing and r in game.clearing_rows:
                draw_block(surface, px, py, CELL, (WHITE, GRAY))
            else:
                draw_block(surface, px, py, CELL, _colors_for_cell(game.level, value))

    if game.state == game_module.PLAYING and game.piece:
        colors = _palette_for(game.level, game.piece.kind)
        for c, r in game.piece.cells():
            if r < BUFFER_ROWS:
                continue
            px = x + c * CELL
            py = y + (r - BUFFER_ROWS) * CELL
            draw_block(surface, px, py, CELL, colors)

    # subtle grid lines
    for c in range(COLS + 1):
        gx = x + c * CELL
        pygame.draw.line(surface, (20, 20, 28), (gx, y), (gx, y + PLAYFIELD_H))
    for r in range(ROWS + 1):
        gy = y + r * CELL
        pygame.draw.line(surface, (20, 20, 28), (x, gy), (x + PLAYFIELD_W, gy))


def draw_mini_piece(surface, kind, level, cx, cy, cell=14):
    shape = SHAPES[kind][0]
    xs = [p[0] for p in shape]
    ys = [p[1] for p in shape]
    w = (max(xs) - min(xs) + 1) * cell
    h = (max(ys) - min(ys) + 1) * cell
    ox = cx - w // 2
    oy = cy - h // 2
    colors = _palette_for(level, kind)
    for x, y in shape:
        px = ox + (x - min(xs)) * cell
        py = oy + (y - min(ys)) * cell
        draw_block(surface, px, py, cell, colors)


def draw_top_bar(surface, game, fonts):
    left_rect = pygame.Rect(MARGIN + BORDER, MARGIN + BORDER, LEFT_PANEL_W - 2 * BORDER, TOP_BAR_H - 2 * BORDER)
    draw_bordered_box(surface, left_rect)
    label = fonts.med.render("A-TYPE", True, TEXT_ORANGE)
    surface.blit(label, label.get_rect(center=left_rect.center))

    lines_rect = pygame.Rect(PLAYFIELD_X, MARGIN + BORDER, PLAYFIELD_W, TOP_BAR_H - 2 * BORDER)
    draw_bordered_box(surface, lines_rect)
    text = fonts.med.render(f"LINES-{game.lines:03d}", True, WHITE)
    surface.blit(text, text.get_rect(center=lines_rect.center))


def draw_stats_panel(surface, game, fonts):
    rect = LEFT_PANEL_RECT
    inner = pygame.Rect(rect.x + BORDER, rect.y + BORDER, rect.w - 2 * BORDER, rect.h - 2 * BORDER)
    draw_bordered_box(surface, inner, "STATISTICS", fonts)

    y = inner.y + 26
    row_h = (inner.h - 30) // len(PIECE_TYPES)
    for kind in PIECE_TYPES:
        draw_mini_piece(surface, kind, game.level, inner.x + 40, y + row_h // 2, cell=12)
        count = fonts.small.render(f"{game.stats[kind]:03d}", True, TEXT_ORANGE)
        surface.blit(count, (inner.x + 90, y + row_h // 2 - count.get_height() // 2))
        y += row_h


def draw_side_panel(surface, game, fonts):
    x = RIGHT_PANEL_X + BORDER
    w = RIGHT_PANEL_W - 2 * BORDER
    y = PLAYFIELD_Y

    score_rect = pygame.Rect(x, y, w, 90)
    draw_bordered_box(surface, score_rect)
    top_label = fonts.small.render("TOP", True, GRAY)
    top_val = fonts.med.render(f"{game.top_score:06d}", True, WHITE)
    score_label = fonts.small.render("SCORE", True, GRAY)
    score_val = fonts.med.render(f"{game.score:06d}", True, WHITE)
    surface.blit(top_label, (score_rect.x + 10, score_rect.y + 8))
    surface.blit(top_val, (score_rect.x + 10, score_rect.y + 24))
    surface.blit(score_label, (score_rect.x + 10, score_rect.y + 50))
    surface.blit(score_val, (score_rect.x + 10, score_rect.y + 66))

    y += 90 + MARGIN
    next_rect = pygame.Rect(x, y, w, 110)
    draw_bordered_box(surface, next_rect, "NEXT", fonts)
    draw_mini_piece(surface, game.next_kind, game.level, next_rect.centerx, next_rect.centery + 10, cell=20)

    y += 110 + MARGIN
    level_rect = pygame.Rect(x, y, w, 70)
    draw_bordered_box(surface, level_rect)
    level_label = fonts.small.render("LEVEL", True, GRAY)
    level_val = fonts.big.render(f"{game.level:02d}", True, WHITE)
    surface.blit(level_label, level_label.get_rect(centerx=level_rect.centerx, top=level_rect.y + 8))
    surface.blit(level_val, level_val.get_rect(centerx=level_rect.centerx, top=level_rect.y + 26))


def draw_overlay_text(surface, fonts, lines, y_start=None, center_x=None, height=HEIGHT):
    center_x = WIDTH // 2 if center_x is None else center_x
    total_h = sum(f.get_height() for f, _, _ in lines) + 10 * (len(lines) - 1)
    y = y_start if y_start is not None else (height - total_h) // 2
    for font, text, color in lines:
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(centerx=center_x, top=y))
        y += font.get_height() + 10


def render(surface, game, fonts):
    draw_brick_background(surface)
    draw_top_bar(surface, game, fonts)
    draw_stats_panel(surface, game, fonts)
    draw_playfield(surface, game, fonts)
    draw_side_panel(surface, game, fonts)

    if game.state == game_module.MENU:
        panel = pygame.Rect(0, 0, 560, 400)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(surface, PANEL_BG, panel)
        pygame.draw.rect(surface, CYAN_BORDER, panel, 4)
        level_hint = "KILL SCREEN" if game.starting_level >= 29 else ("near kill screen" if game.starting_level >= 19 else "")
        mode_text = "1 PLAYER" if game.player_mode == 1 else "2 PLAYER"
        draw_overlay_text(
            surface, fonts,
            [
                (fonts.huge, "TETRIS", TEXT_ORANGE),
                (fonts.med, f"Mode: {mode_text}", WHITE),
                (fonts.small, "1 / 2 to choose mode", GRAY),
                (fonts.med, f"Starting Level: {game.starting_level:02d}  {level_hint}", WHITE),
                (fonts.small, "UP / DOWN change level (0-29)", GRAY),
                (fonts.small, "ENTER to start", GRAY),
                (fonts.small, "1P: arrows or WASD, Z/X or Q/W rotate", GRAY),
                (fonts.small, "2P: P1 arrows + Up/RCtrl", GRAY),
                (fonts.small, "2P: P2 WASD + LShift", GRAY),
            ],
            y_start=panel.y + 20,
        )
    elif game.state == game_module.PAUSED:
        draw_overlay_text(surface, fonts, [
            (fonts.huge, "PAUSED", WHITE),
            (fonts.small, "Press P to resume", GRAY),
        ])
    elif game.state == game_module.GAME_OVER and game.game_over_fill_row >= game.board.total_rows:
        draw_overlay_text(surface, fonts, [
            (fonts.huge, "GAME OVER", TEXT_ORANGE),
            (fonts.med, f"Score {game.score}", WHITE),
            (fonts.small, "Press ENTER for menu", GRAY),
        ])


# --- Two-player layout: two playfields side by side, each with its own
# compact NEXT / SCORE / LEVEL / LINES panel. ---

TWO_PANEL_W = 160
TWO_TOP_H = 50
TWO_BOARD_GAP = 32

TWO_FIELD_Y = MARGIN + TWO_TOP_H + MARGIN + BORDER

_tx = MARGIN
P1_PANEL_X = _tx
_tx += TWO_PANEL_W + MARGIN
P1_FIELD_X = _tx + BORDER
_tx += BORDER + PLAYFIELD_W + BORDER + TWO_BOARD_GAP
P2_FIELD_X = _tx + BORDER
_tx += BORDER + PLAYFIELD_W + BORDER + MARGIN
P2_PANEL_X = _tx
_tx += TWO_PANEL_W + MARGIN

TWO_WIDTH = _tx
TWO_HEIGHT = TWO_FIELD_Y + PLAYFIELD_H + BORDER + MARGIN


def draw_player_panel(surface, x, game, fonts, label, label_color):
    w = TWO_PANEL_W
    y = TWO_FIELD_Y

    label_rect = pygame.Rect(x, y, w, 36)
    draw_bordered_box(surface, label_rect)
    text = fonts.med.render(label, True, label_color)
    surface.blit(text, text.get_rect(center=label_rect.center))

    y += 36 + MARGIN
    next_rect = pygame.Rect(x, y, w, 96)
    draw_bordered_box(surface, next_rect, "NEXT", fonts)
    draw_mini_piece(surface, game.next_kind, game.level, next_rect.centerx, next_rect.centery + 8, cell=16)

    y += 96 + MARGIN
    score_rect = pygame.Rect(x, y, w, 64)
    draw_bordered_box(surface, score_rect)
    score_label = fonts.small.render("SCORE", True, GRAY)
    score_val = fonts.med.render(f"{game.score:06d}", True, WHITE)
    surface.blit(score_label, (score_rect.x + 8, score_rect.y + 6))
    surface.blit(score_val, (score_rect.x + 8, score_rect.y + 24))

    y += 64 + MARGIN
    level_rect = pygame.Rect(x, y, w, 84)
    draw_bordered_box(surface, level_rect)
    level_label = fonts.small.render("LEVEL", True, GRAY)
    level_val = fonts.med.render(f"{game.level:02d}", True, WHITE)
    lines_label = fonts.small.render("LINES", True, GRAY)
    lines_val = fonts.med.render(f"{game.lines:03d}", True, WHITE)
    surface.blit(level_label, (level_rect.x + 8, level_rect.y + 6))
    surface.blit(level_val, (level_rect.x + 8, level_rect.y + 22))
    surface.blit(lines_label, (level_rect.x + 8, level_rect.y + 44))
    surface.blit(lines_val, (level_rect.x + 8, level_rect.y + 60))


def _player_over(game):
    return game.state == game_module.GAME_OVER and game.game_over_fill_row >= game.board.total_rows


def render_two_player(surface, game_p1, game_p2, fonts, paused=False):
    draw_brick_background(surface)

    title_rect = pygame.Rect(0, MARGIN + BORDER, 0, TWO_TOP_H - 2 * BORDER)
    title_rect.w = TWO_WIDTH - 2 * MARGIN
    title_rect.centerx = TWO_WIDTH // 2
    draw_bordered_box(surface, title_rect)
    title = fonts.med.render("2 PLAYER", True, TEXT_ORANGE)
    surface.blit(title, title.get_rect(center=title_rect.center))

    draw_player_panel(surface, P1_PANEL_X, game_p1, fonts, "PLAYER 1", (120, 200, 255))
    draw_player_panel(surface, P2_PANEL_X, game_p2, fonts, "PLAYER 2", (255, 150, 120))

    draw_playfield(surface, game_p1, fonts, x=P1_FIELD_X, y=TWO_FIELD_Y)
    draw_playfield(surface, game_p2, fonts, x=P2_FIELD_X, y=TWO_FIELD_Y)

    round_over = _player_over(game_p1) and _player_over(game_p2)
    for game, field_x in ((game_p1, P1_FIELD_X), (game_p2, P2_FIELD_X)):
        if _player_over(game) and not round_over:
            overlay_rect = pygame.Rect(field_x, TWO_FIELD_Y, PLAYFIELD_W, PLAYFIELD_H)
            shade = pygame.Surface(overlay_rect.size, pygame.SRCALPHA)
            shade.fill((0, 0, 0, 160))
            surface.blit(shade, overlay_rect.topleft)
            draw_overlay_text(
                surface, fonts,
                [(fonts.big, "TOPPED OUT", TEXT_ORANGE)],
                y_start=overlay_rect.centery - 20,
                center_x=overlay_rect.centerx,
            )

    if paused:
        draw_overlay_text(surface, fonts, [
            (fonts.huge, "PAUSED", WHITE),
            (fonts.small, "Press P to resume", GRAY),
        ], center_x=TWO_WIDTH // 2, height=TWO_HEIGHT)
    elif _player_over(game_p1) and _player_over(game_p2):
        if game_p1.score > game_p2.score:
            result = "PLAYER 1 WINS"
        elif game_p2.score > game_p1.score:
            result = "PLAYER 2 WINS"
        else:
            result = "TIE GAME"
        draw_overlay_text(surface, fonts, [
            (fonts.huge, "GAME OVER", TEXT_ORANGE),
            (fonts.med, result, WHITE),
            (fonts.small, "Press ENTER for menu", GRAY),
        ], center_x=TWO_WIDTH // 2, height=TWO_HEIGHT)
