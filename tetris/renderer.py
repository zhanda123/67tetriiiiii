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


def _font(size, bold=True):
    name = pygame.font.match_font("couriernew,consolas,dejavusansmono,monospace")
    f = pygame.font.Font(name, size)
    f.set_bold(bold)
    return f


class Fonts:
    def __init__(self):
        self.huge = _font(40)
        self.big = _font(26)
        self.med = _font(18)
        self.small = _font(14)


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


def draw_playfield(surface, game, fonts):
    rect = pygame.Rect(PLAYFIELD_X, PLAYFIELD_Y, PLAYFIELD_W, PLAYFIELD_H)
    draw_bordered_box(surface, rect)

    board = game.board
    flashing = game.state == game_module.LINE_CLEAR and (game.clear_timer // 3) % 2 == 0

    for r in range(BUFFER_ROWS, board.total_rows):
        for c in range(COLS):
            value = board.grid[r][c]
            if value == 0:
                continue
            px = PLAYFIELD_X + c * CELL
            py = PLAYFIELD_Y + (r - BUFFER_ROWS) * CELL
            if flashing and r in game.clearing_rows:
                draw_block(surface, px, py, CELL, (WHITE, GRAY))
            else:
                draw_block(surface, px, py, CELL, _colors_for_cell(game.level, value))

    if game.state == game_module.PLAYING and game.piece:
        colors = _palette_for(game.level, game.piece.kind)
        for c, r in game.piece.cells():
            if r < BUFFER_ROWS:
                continue
            px = PLAYFIELD_X + c * CELL
            py = PLAYFIELD_Y + (r - BUFFER_ROWS) * CELL
            draw_block(surface, px, py, CELL, colors)

    # subtle grid lines
    for c in range(COLS + 1):
        x = PLAYFIELD_X + c * CELL
        pygame.draw.line(surface, (20, 20, 28), (x, PLAYFIELD_Y), (x, PLAYFIELD_Y + PLAYFIELD_H))
    for r in range(ROWS + 1):
        y = PLAYFIELD_Y + r * CELL
        pygame.draw.line(surface, (20, 20, 28), (PLAYFIELD_X, y), (PLAYFIELD_X + PLAYFIELD_W, y))


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


def draw_overlay_text(surface, fonts, lines, y_start=None):
    total_h = sum(f.get_height() for f, _, _ in lines) + 10 * (len(lines) - 1)
    y = y_start if y_start is not None else (HEIGHT - total_h) // 2
    for font, text, color in lines:
        rendered = font.render(text, True, color)
        surface.blit(rendered, rendered.get_rect(centerx=WIDTH // 2, top=y))
        y += font.get_height() + 10


def render(surface, game, fonts):
    draw_brick_background(surface)
    draw_top_bar(surface, game, fonts)
    draw_stats_panel(surface, game, fonts)
    draw_playfield(surface, game, fonts)
    draw_side_panel(surface, game, fonts)

    if game.state == game_module.MENU:
        panel = pygame.Rect(0, 0, 420, 260)
        panel.center = (WIDTH // 2, HEIGHT // 2)
        pygame.draw.rect(surface, PANEL_BG, panel)
        pygame.draw.rect(surface, CYAN_BORDER, panel, 4)
        level_hint = "KILL SCREEN" if game.starting_level >= 29 else ("near kill screen" if game.starting_level >= 19 else "")
        draw_overlay_text(
            surface, fonts,
            [
                (fonts.huge, "TETRIS", TEXT_ORANGE),
                (fonts.med, f"Starting Level: {game.starting_level:02d}  {level_hint}", WHITE),
                (fonts.small, "UP / DOWN change level (0-29)", GRAY),
                (fonts.small, "ENTER to start", GRAY),
                (fonts.small, "LEFT/RIGHT move  Z/X rotate  DOWN soft drop", GRAY),
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
