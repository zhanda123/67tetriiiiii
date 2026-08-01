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

## Controls

| Key            | Action                        |
|----------------|--------------------------------|
| Left / Right   | Move piece                     |
| Down           | Soft drop                      |
| Up / X         | Rotate clockwise                |
| Z              | Rotate counter-clockwise        |
| Up / Down (menu) | Choose starting level (0-9)  |
| Enter          | Start game / return to menu     |
| P              | Pause / resume                  |
| Esc            | Back to menu / quit              |

## Gameplay notes

- 10x20 playfield, 7 tetrominoes (I, O, T, S, Z, J, L), classic NES-style
  falling speed table (level 0 = 48 frames/row down to level 29+ = 1 frame/row).
- Scoring: single 40, double 100, triple 300, tetris 1200, each multiplied
  by `(level + 1)`, matching the original scoring table.
- Level advances every 10 lines cleared.
- No hold piece, no hard drop, no ghost piece — just like the original.
- STATISTICS panel tracks how many of each piece type has dropped.

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
