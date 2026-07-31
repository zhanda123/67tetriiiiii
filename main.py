"""Entry point for the classic-style Tetris game.

Run with:  python main.py
"""

import sys

import pygame

from tetris.game import Game, MENU, PLAYING, PAUSED, GAME_OVER
from tetris.constants import FPS
from tetris import renderer


def handle_menu_keys(game, event):
    if event.key in (pygame.K_UP, pygame.K_RIGHT):
        game.starting_level = min(9, game.starting_level + 1)
    elif event.key in (pygame.K_DOWN, pygame.K_LEFT):
        game.starting_level = max(0, game.starting_level - 1)
    elif event.key == pygame.K_RETURN:
        game.start(game.starting_level)
    elif event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit(0)


def handle_playing_keys(game, event):
    if event.key in (pygame.K_UP, pygame.K_x):
        game.rotate(1)
    elif event.key == pygame.K_z:
        game.rotate(-1)
    elif event.key == pygame.K_p:
        game.state = PAUSED
    elif event.key == pygame.K_ESCAPE:
        game.state = MENU


def handle_paused_keys(game, event):
    if event.key == pygame.K_p:
        game.state = PLAYING
    elif event.key == pygame.K_ESCAPE:
        game.state = MENU


def handle_game_over_keys(game, event):
    if event.key == pygame.K_RETURN and game.game_over_fill_row >= game.board.total_rows:
        game.state = MENU


def main():
    pygame.init()
    pygame.display.set_caption("Tetris")
    surface = pygame.display.set_mode((renderer.WIDTH, renderer.HEIGHT))
    clock = pygame.time.Clock()
    fonts = renderer.Fonts()

    game = Game()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if game.state == MENU:
                    handle_menu_keys(game, event)
                elif game.state == PLAYING:
                    handle_playing_keys(game, event)
                elif game.state == PAUSED:
                    handle_paused_keys(game, event)
                elif game.state == GAME_OVER:
                    handle_game_over_keys(game, event)

        keys = pygame.key.get_pressed()
        if game.state == PLAYING:
            game.process_input(
                left=keys[pygame.K_LEFT],
                right=keys[pygame.K_RIGHT],
                soft_drop=keys[pygame.K_DOWN],
            )

        game.update()

        renderer.render(surface, game, fonts)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
