"""Entry point for the classic-style Tetris game.

Run with:  python main.py
"""

import sys

import pygame

from tetris.game import Game, MENU, PLAYING, PAUSED, GAME_OVER
from tetris.constants import FPS, MAX_STARTING_LEVEL
from tetris import renderer


def handle_menu_keys(game, event):
    if event.key in (pygame.K_UP, pygame.K_RIGHT):
        game.starting_level = min(MAX_STARTING_LEVEL, game.starting_level + 1)
    elif event.key in (pygame.K_DOWN, pygame.K_LEFT):
        game.starting_level = max(0, game.starting_level - 1)
    elif event.key in (pygame.K_1, pygame.K_KP1):
        game.player_mode = 1
    elif event.key in (pygame.K_2, pygame.K_KP2):
        game.player_mode = 2
    elif event.key == pygame.K_RETURN:
        return "start"
    elif event.key == pygame.K_ESCAPE:
        pygame.quit()
        sys.exit(0)
    return None


def handle_playing_keys(game, event):
    if event.key in (pygame.K_UP, pygame.K_x, pygame.K_w):
        game.rotate(1)
    elif event.key in (pygame.K_z, pygame.K_q):
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


def handle_two_player_keys(game_p1, game_p2, event, two_paused):
    if event.key in (pygame.K_UP,):
        game_p1.rotate(1)
    elif event.key == pygame.K_RCTRL:
        game_p1.rotate(-1)
    elif event.key == pygame.K_w:
        game_p2.rotate(1)
    elif event.key == pygame.K_LSHIFT:
        game_p2.rotate(-1)
    elif event.key == pygame.K_p:
        return not two_paused
    return two_paused


def main():
    pygame.init()
    pygame.display.set_caption("Tetris")
    surface = pygame.display.set_mode((renderer.WIDTH, renderer.HEIGHT))
    pygame.key.set_repeat(300, 60)  # lets you hold Up/Down to scroll the 0-29 level picker
    clock = pygame.time.Clock()
    fonts = renderer.Fonts()

    menu_game = Game()
    app_mode = "menu"  # menu | single | two

    game = None
    game_p1 = None
    game_p2 = None
    two_paused = False

    repeat_on = True

    running = True
    while running:
        want_repeat = app_mode == "menu"
        if want_repeat != repeat_on:
            pygame.key.set_repeat(300, 60) if want_repeat else pygame.key.set_repeat()
            repeat_on = want_repeat

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if app_mode == "menu":
                    if handle_menu_keys(menu_game, event) == "start":
                        level = menu_game.starting_level
                        if menu_game.player_mode == 1:
                            game = Game()
                            game.start(level)
                            surface = pygame.display.set_mode((renderer.WIDTH, renderer.HEIGHT))
                            app_mode = "single"
                        else:
                            game_p1 = Game()
                            game_p1.start(level)
                            game_p2 = Game()
                            game_p2.start(level)
                            two_paused = False
                            surface = pygame.display.set_mode((renderer.TWO_WIDTH, renderer.TWO_HEIGHT))
                            app_mode = "two"
                elif app_mode == "single":
                    if game.state == PLAYING:
                        handle_playing_keys(game, event)
                    elif game.state == PAUSED:
                        handle_paused_keys(game, event)
                    elif game.state == GAME_OVER:
                        handle_game_over_keys(game, event)
                    if game.state == MENU:
                        app_mode = "menu"
                        surface = pygame.display.set_mode((renderer.WIDTH, renderer.HEIGHT))
                elif app_mode == "two":
                    if event.key == pygame.K_ESCAPE:
                        app_mode = "menu"
                        surface = pygame.display.set_mode((renderer.WIDTH, renderer.HEIGHT))
                    elif event.key == pygame.K_RETURN:
                        p1_done = game_p1.state == GAME_OVER and game_p1.game_over_fill_row >= game_p1.board.total_rows
                        p2_done = game_p2.state == GAME_OVER and game_p2.game_over_fill_row >= game_p2.board.total_rows
                        if p1_done and p2_done:
                            app_mode = "menu"
                            surface = pygame.display.set_mode((renderer.WIDTH, renderer.HEIGHT))
                    else:
                        two_paused = handle_two_player_keys(game_p1, game_p2, event, two_paused)

        if app_mode == "single":
            keys = pygame.key.get_pressed()
            if game.state == PLAYING:
                game.process_input(
                    left=keys[pygame.K_LEFT] or keys[pygame.K_a],
                    right=keys[pygame.K_RIGHT] or keys[pygame.K_d],
                    soft_drop=keys[pygame.K_DOWN] or keys[pygame.K_s],
                )
            game.update()
            renderer.render(surface, game, fonts)
        elif app_mode == "two":
            if not two_paused:
                keys = pygame.key.get_pressed()
                if game_p1.state == PLAYING:
                    game_p1.process_input(
                        left=keys[pygame.K_LEFT], right=keys[pygame.K_RIGHT], soft_drop=keys[pygame.K_DOWN],
                    )
                if game_p2.state == PLAYING:
                    game_p2.process_input(
                        left=keys[pygame.K_a], right=keys[pygame.K_d], soft_drop=keys[pygame.K_s],
                    )
                game_p1.update()
                game_p2.update()
            renderer.render_two_player(surface, game_p1, game_p2, fonts, paused=two_paused)
        else:
            renderer.render(surface, menu_game, fonts)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
