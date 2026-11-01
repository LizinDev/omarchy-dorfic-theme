#!/usr/bin/env python3
"""preview.png: the theme-switcher tile, drawn from code only (the 1-bubbles
background, a mock Gloss Bar and a glass terminal showing the palette), so it
is safe to publish.

    python3 -I tools/preview.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cairo  # noqa: E402
from gloss import WHITE, canvas, finish, gloss_capsule, label, mix, rgb, round_rect  # noqa: E402
from wallpapers import bubbles  # noqa: E402

THEME = Path(__file__).resolve().parent.parent
W, H = 1800, 1012
BG, FG, ACCENT = rgb('background'), rgb('foreground'), rgb('accent')
CAPSULE = dict(base=rgb('#e2600a'), light=rgb('#ffb066'), dark=rgb('#ff8a2a'), shine=0.8)


def main():
    surf, cr = canvas(W, H)
    bubbles(cr, W, H)

    # bar: three translucent orange capsules
    for x, w, text in [(18, 300, '01   02   03   04   05'), (720, 360, 'Saturday 23:03'), (1450, 332, 'NET   ·   VOL 60   ·   82%')]:
        cr.push_group()
        gloss_capsule(cr, x, 10, w, 40, **CAPSULE)
        cr.pop_group_to_source()
        cr.paint_with_alpha(0.85)
        label(cr, x + w / 2, 37, text, 19, WHITE, family='Nimbus Sans', align=0.5)

    # terminal: ember glass with the gold-white-orange frame
    x, y, w, h = 120, 150, 980, 640
    round_rect(cr, x - 3, y - 3, w + 6, h + 6, 21)
    g = cairo.LinearGradient(0, y, 0, y + h)
    for stop, hex_ in [(0, '#ffffff'), (0.5, '#ffd23f'), (1, '#ff8a1f')]:
        g.add_color_stop_rgb(stop, *rgb(hex_))
    cr.set_source(g)
    cr.fill()
    round_rect(cr, x, y, w, h, 18)
    cr.set_source_rgba(*BG, 0.86)
    cr.fill()
    mono = 'JetBrainsMono Nerd Font'
    lines = [
        [('~/Projects ', ACCENT), ('$ ', FG), ('omarchy theme set dorfic', FG)],
        [('daylight · orange · red · futurism · graphic', rgb('dark_foreground'))],
        [],
        [('def ', rgb('magenta')), ('gloss', rgb('blue')), ('(capsule):', FG)],
        [('    shine ', FG), ('= ', rgb('cyan')), ('0.8', rgb('yellow')), ('  # highlight band', rgb('muted'))],
        [('    return ', rgb('magenta')), ('"orange glass"', rgb('green'))],
        [],
        [('[ok] ', rgb('green')), ('rendered 6 backgrounds', FG)],
        [('[!!] ', rgb('red')), ('no grey allowed', FG)],
    ]
    for i, parts in enumerate(lines):
        cx = x + 44
        for text, color in parts:
            cx += label(cr, cx, y + 70 + i * 44, text, 24, color, weight=cairo.FONT_WEIGHT_NORMAL, family=mono)
    # ANSI swatches as glossy chips
    keys = ['red', 'yellow', 'orange', 'green', 'cyan', 'blue', 'magenta', 'accent']
    for i, key in enumerate(keys):
        c = rgb(key)
        gloss_capsule(cr, x + 44 + i * 112, y + h - 96, 96, 48, base=c, light=mix(c, WHITE, 0.4), dark=mix(c, BG, 0.25), shine=0.7)

    finish(surf, THEME / 'preview.png', grain=0.8)
    print(THEME / 'preview.png')


if __name__ == '__main__':
    main()
