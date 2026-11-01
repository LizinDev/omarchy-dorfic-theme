#!/usr/bin/env python3
"""fastfetch.txt: the theme's fastfetch logo, a glossy orb cluster drawn with
the wallpaper primitives and encoded as truecolor half-blocks (two pixels per
character cell), so it keeps its gloss in the terminal.

    python3 -I tools/fastfetch.py

The theme-set hook in tools/fastfetch-hook installs it; see the README.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
from gloss import canvas, glass_sphere, gloss_sphere  # noqa: E402
from palette import BG  # noqa: E402

THEME = Path(__file__).resolve().parent.parent
COLS, ROWS = 54, 26          # the stock Omarchy logo's footprint
SS = 8                       # supersampling factor
W, H = COLS, ROWS * 2        # pixels: two per cell vertically


def draw():
    surf, cr = canvas(W * SS, H * SS)
    s = SS
    glass_sphere(cr, 41 * s, 12 * s, 9 * s)
    gloss_sphere(cr, 22 * s, 30 * s, 21 * s)
    gloss_sphere(cr, 46 * s, 40 * s, 8 * s)
    gloss_sphere(cr, 6 * s, 9 * s, 3.5 * s)
    surf.flush()
    stride = surf.get_stride() // 4
    px = np.ndarray((H * SS, stride, 4), np.uint8, surf.get_data())[:, :W * SS].astype(np.float64)
    # cairo stores premultiplied BGRA; average blocks while still premultiplied
    px = px.reshape(H, SS, W, SS, 4).mean(axis=(1, 3))
    alpha = px[..., 3] / 255
    # Composite over the terminal background, so soft edges and the faint
    # glass come out antialiased instead of cut at a hard threshold.
    rgb = px[..., [2, 1, 0]] + np.array(BG, float) * (1 - alpha)[..., None]
    return np.clip(np.rint(rgb), 0, 255).astype(int), alpha


def encode(rgb, alpha, cutoff=0.12):
    lines = []
    for row in range(ROWS):
        top, bottom = 2 * row, 2 * row + 1
        cells = []
        for x in range(COLS):
            t = alpha[top, x] >= cutoff
            b = alpha[bottom, x] >= cutoff
            if t and b:
                cells.append(('38;2;%d;%d;%d;48;2;%d;%d;%d' % (*rgb[top, x], *rgb[bottom, x]), '▀'))
            elif t:
                cells.append(('49;38;2;%d;%d;%d' % tuple(rgb[top, x]), '▀'))
            elif b:
                cells.append(('49;38;2;%d;%d;%d' % tuple(rgb[bottom, x]), '▄'))
            else:
                cells.append((None, ' '))
        while cells and cells[-1][0] is None:
            cells.pop()
        out, state = [], None
        for code, char in cells:
            if code is None and state is not None:
                out.append('\x1b[0m')
            elif code is not None and code != state:
                out.append('\x1b[%sm' % code)
            state = code
            out.append(char)
        lines.append(''.join(out) + ('\x1b[0m' if state is not None else ''))
    while lines and not lines[0]:
        lines.pop(0)
    while lines and not lines[-1]:
        lines.pop()
    return '\n'.join(lines) + '\n'


def main():
    rgb, alpha = draw()
    out = THEME / 'fastfetch.txt'
    out.write_text(encode(rgb, alpha))
    print(out)


if __name__ == '__main__':
    main()
