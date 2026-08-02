# 67tetriiiiii — Tetris

A from-scratch Python/pygame recreation of classic NES-style Tetris (A-Type):
brick-patterned border, cyan-framed STATISTICS / NEXT / SCORE / LEVEL panels,
beveled blocks, level-based color palettes, the original scoring table, and
the classic falling-speed curve.

## Requirements

- Python 3.9+
- pygame

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## Menu

- **1** / **2** — choose 1-player or 2-player mode
- **Up** / **Down** — choose starting level (0-29; hold to scroll fast). 29 is
  the real NES "kill screen" (1 frame per row).
- **Enter** — start

## Controls — 1 player

Arrow keys and WASD both work at the same time, so use whichever you like:

| Action              | Keys              |
|---------------------|-------------------|
| Move left / right   | Left/Right or A/D |
| Soft drop            | Down or S         |
| Rotate clockwise      | Up, X, W, F, or K |
| Rotate counter-clockwise | Z or Q        |
| Pause / resume        | P                 |
| Back to menu           | Esc               |

## Controls — 2 player

Player 1 (arrow cluster, **left** side of the screen) and Player 2 (WASD,
**right** side of the screen) play on one keyboard at once. Both players get
the exact same sequence of pieces, so a run is fair regardless of who's
faster:

| Action                | Player 1 (left board)  | Player 2 (right board) |
|------------------------|------------------------|-------------------------|
| Move left / right       | Left / Right           | A / D                    |
| Soft drop                | Down                   | S                        |
| Rotate clockwise           | Up or K              | W or F                   |
| Rotate counter-clockwise     | Right Ctrl          | Left Shift                |

Pause (**P**) and back-to-menu (**Esc**) are shared. Each board tops out
independently — the other player keeps going. When both are out, the higher
score wins.

## Gameplay notes

- 10x20 playfield, 7 tetrominoes (I, O, T, S, Z, J, L), classic NES-style
  falling speed table (level 0 = 48 frames/row down to level 29+ = 1 frame/row).
- Scoring: single 40, double 100, triple 300, tetris 1200, each multiplied
  by `(level + 1)`, matching the original scoring table.
- Level advances every 10 lines cleared.
- No hold piece, no hard drop, no ghost piece — just like the original.
- STATISTICS panel (1-player only) tracks how many of each piece type has
  dropped.
- 2-player mode gives both boards the same piece sequence (indexed by each
  player's own piece count, not by turn order), so playing faster or slower
  never changes what piece either player gets next.
- On-screen text is rendered as a tiny pixel font scaled up with hard edges,
  for the same blocky low-res look as the original game's text.

## Project layout

```
main.py            # pygame entry point / input handling
tetris/
  constants.py      # sizing, timing, scoring, color palettes
  pieces.py         # tetromino shapes + randomizer
  board.py          # grid state, collision, line clearing
  game.py            # game state machine (menu/playing/paused/game over)
  renderer.py         # all drawing code
```
