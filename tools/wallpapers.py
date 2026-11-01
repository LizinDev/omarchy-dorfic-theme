#!/usr/bin/env python3
"""Generate the theme's backgrounds from colors.toml. Every image is drawn
from code (no source art), so all of them are publishable.

    python3 -I tools/wallpapers.py [name ...] [--scale 0.5]

Writes backgrounds/<n>-<name>.jpg at 3840x2160 (scale 1).
"""
import math
import random
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import cairo  # noqa: E402
from gloss import (AMBER, DEEP, EMBER, INK, ORANGE, PAPER, RED, SHADE, STEEL, WHITE,  # noqa: E402
                   canvas, daylight, finish, glass_panel, glass_sphere, gloss_capsule, gloss_sphere,
                   label, mix, round_rect, soft_shadow, white_panel)

OUT = Path(__file__).resolve().parent.parent / 'backgrounds'
W, H = 3840, 2160


def bubbles(cr, w, h):
    """Glossy orange balls and clear glass bubbles resting on, and floating
    above, an overexposed white studio floor."""
    daylight(cr, w, h, sun=(0.72, 0.05), floor=0.80)
    rnd = random.Random(23)
    # (x, y, r, kind) — resting balls sit on the floor line, others float
    items = [
        (0.64, None, 0.165, 'gloss'),
        (0.895, None, 0.075, 'gloss'),
        (0.415, None, 0.05, 'gloss'),
        (0.40, 0.30, 0.075, 'glass'),
        (0.92, 0.28, 0.05, 'glass'),
        (0.56, 0.17, 0.035, 'gloss'),
        (0.30, 0.55, 0.03, 'glass'),
    ]
    while len(items) < 22:
        x, y = rnd.uniform(0.25, 0.98), rnd.uniform(0.08, 0.62)
        if abs(x - 0.64) * w / h < 0.32 and y > 0.2:
            continue  # keep the small ones out from behind the big ball
        items.append((x, y, rnd.uniform(0.006, 0.016), rnd.choice(['glass', 'glass', 'gloss'])))
    floor_y = h * 0.80
    for x, y, r, kind in sorted(items, key=lambda i: i[2]):
        R = r * h * 1.6
        cx = x * w
        if y is None:
            cy = floor_y - R
            soft_shadow(cr, cx + R * 0.15, floor_y, R * 1.05, R * 0.16, alpha=0.38)
        else:
            cy = y * h
            soft_shadow(cr, cx + R * 0.3, floor_y + R * 0.2, R * 0.8, R * 0.1, alpha=0.08)
        (gloss_sphere if kind == 'gloss' else glass_sphere)(cr, cx, cy, R)
    # reflection of the big ball on the glossy floor
    cr.save()
    cr.rectangle(0, floor_y, w, h - floor_y)
    cr.clip()
    R = 0.165 * h * 1.6
    cr.translate(0, 2 * floor_y)
    cr.scale(1, -1)
    cr.push_group()
    gloss_sphere(cr, 0.64 * w, floor_y - R, R)
    cr.pop_group_to_source()
    cr.paint_with_alpha(0.12)
    cr.restore()
    caption(cr, w, h, '01', 'DAYLIGHT')


def caption(cr, w, h, num, word, color=INK, top=False):
    """Small corporate tag in a left corner: a number chip and a spaced word."""
    s = h / 2160
    x, y = 150 * s, (250 if top else 2160 - 170) * s
    gloss_capsule(cr, x, y - 70 * s, 150 * s, 92 * s, base=PAPER, light=WHITE, dark=SHADE)
    label(cr, x + 75 * s, y + 2 * s, num, 56 * s, EMBER, align=0.5)
    label(cr, x + 190 * s, y, word, 44 * s, color, spacing=0.32, alpha=0.85)
    cr.set_source_rgba(*color, 0.25)
    cr.rectangle(x + 190 * s, y + 24 * s, 520 * s, 3 * s)
    cr.fill()


def blades(cr, w, h):
    """A fan of rounded glossy blades swinging out from the right edge, all
    white plastic except one orange blade — the 2000s console-dashboard move."""
    daylight(cr, w, h, sun=(0.2, 0.15))
    s = h / 2160
    pivot = (w * 1.08, h * 1.25)
    bw, bh = 3300 * s, 400 * s
    for i, ang in enumerate([0.10, 0.27, 0.44, 0.61, 0.78]):
        orange = i == 2
        cr.save()
        cr.translate(*pivot)
        cr.rotate(ang)
        cr.translate(-bw - 300 * s, -bh / 2)
        # drop shadow toward the lower right
        cr.save()
        cr.translate(24 * s, 36 * s)
        round_rect(cr, 0, 0, bw, bh, 90 * s)
        cr.set_source_rgba(*mix(DEEP, (0, 0, 0), 0.3), 0.28)
        cr.fill()
        cr.restore()
        if orange:
            gloss_capsule(cr, 0, 0, bw, bh, r=90 * s, shine=0.75)
            label(cr, 160 * s, bh * 0.68, 'ORANGE', 120 * s, WHITE, spacing=0.18, alpha=0.95)
        else:
            white_panel(cr, 0, 0, bw, bh, 90 * s, depth=10 * s)
            round_rect(cr, 40 * s, 22 * s, bw - 80 * s, bh * 0.42, 70 * s)
            g = cairo.LinearGradient(0, 22 * s, 0, 22 * s + bh * 0.42)
            g.add_color_stop_rgba(0, 1, 1, 1, 0.9)
            g.add_color_stop_rgba(1, 1, 1, 1, 0)
            cr.set_source(g)
            cr.fill()
            label(cr, 160 * s, bh * 0.68, f'0{i + 1}', 120 * s, STEEL, alpha=0.55)
        cr.restore()
    caption(cr, w, h, '02', 'GRAPHIC')


def hexcells(cr, w, h):
    """Rounded honeycomb of white tiles with a few glossy orange domes."""
    daylight(cr, w, h, sun=(0.5, 0.0))
    s = h / 2160
    R = 210 * s
    dx, dy = R * math.sqrt(3), R * 1.5
    rnd = random.Random(5)
    lit = {(5, 2), (6, 3), (5, 3), (9, 1), (3, 5), (10, 4)}
    for row in range(-1, int(h / dy) + 2):
        for col in range(-1, int(w / dx) + 2):
            cx = col * dx + (dx / 2 if row % 2 else 0)
            cy = row * dy
            fade = max(0.0, min(1.0, 1.25 - abs(cx / w - 0.55) * 1.6))
            if fade <= 0.02:
                continue
            hexagon(cr, cx, cy + 16 * s, R * 0.9, 34 * s)
            cr.set_source_rgba(*mix(DEEP, (0, 0, 0), 0.3), 0.28 * fade)
            cr.fill()
            hexagon(cr, cx, cy, R * 0.9, 34 * s)
            if (col, row) in lit:
                g = cairo.RadialGradient(cx - R * 0.3, cy - R * 0.4, R * 0.05, cx, cy, R)
                g.add_color_stop_rgb(0, *mix(AMBER, WHITE, 0.3))
                g.add_color_stop_rgb(0.5, *ORANGE)
                g.add_color_stop_rgb(1, *EMBER)
                cr.set_source(g)
                cr.fill()
                hexagon(cr, cx, cy - R * 0.3, R * 0.6, 40 * s)
                g = cairo.LinearGradient(0, cy - R * 0.85, 0, cy + R * 0.1)
                g.add_color_stop_rgba(0, 1, 1, 1, 0.85)
                g.add_color_stop_rgba(1, 1, 1, 1, 0)
                cr.set_source(g)
                cr.fill()
            else:
                g = cairo.LinearGradient(0, cy - R, 0, cy + R)
                g.add_color_stop_rgba(0, 1, 1, 1, fade)
                g.add_color_stop_rgba(1, *mix(PAPER, SHADE, 0.6), fade)
                cr.set_source(g)
                cr.fill_preserve()
                cr.set_source_rgba(*SHADE, fade)
                cr.set_line_width(3 * s)
                cr.stroke()
                if rnd.random() < 0.08 and R < cy < h - 2 * R and R < cx < w - R:
                    label(cr, cx, cy + 22 * s, f'{rnd.randint(1, 99):02d}', 64 * s, STEEL, align=0.5, alpha=0.5 * fade)
    caption(cr, w, h, '03', 'FUTURISM')


def hexagon(cr, cx, cy, r, corner):
    """Pointy-top hexagon with rounded corners."""
    pts = [(cx + r * math.cos(math.pi / 6 + i * math.pi / 3), cy + r * math.sin(math.pi / 6 + i * math.pi / 3)) for i in range(6)]
    cr.new_sub_path()
    for i in range(6):
        p0, p1, p2 = pts[i - 1], pts[i], pts[(i + 1) % 6]
        a = _toward(p1, p0, corner)
        b = _toward(p1, p2, corner)
        if i == 0:
            cr.move_to(*a)
        else:
            cr.line_to(*a)
        cr.curve_to(*_toward(a, p1, corner * 0.55), *_toward(b, p1, corner * 0.55), *b)
    cr.close_path()


def _toward(p, q, d):
    vx, vy = q[0] - p[0], q[1] - p[1]
    n = math.hypot(vx, vy) or 1
    return p[0] + vx / n * d, p[1] + vy / n * d


def panels(cr, w, h):
    """Sterile wall of white rounded panels, numbered, with glowing orange
    capsule light strips and a single hazard band."""
    daylight(cr, w, h, sun=(0.3, 0.1))
    s = h / 2160
    cols, rows, gap = 6, 4, 34 * s
    pw = (w - gap * (cols + 1)) / cols
    ph = (h - gap * (rows + 1)) / rows
    n = 0
    for r in range(rows):
        for c in range(cols):
            x = gap + c * (pw + gap)
            y = gap + r * (ph + gap)
            n += 1
            solid = (r, c) in {(0, 1), (1, 3), (2, 4), (3, 0), (0, 5), (2, 1)}
            if solid:
                white_panel(cr, x, y, pw, ph, 46 * s, depth=14 * s)
            else:
                glass_panel(cr, x, y, pw, ph, 46 * s)
            if (r, c) in {(1, 3), (2, 4)}:
                continue
            label(cr, x + 44 * s, y + 92 * s, f'{n:02d}', 54 * s, STEEL if solid else WHITE, alpha=0.6 if solid else 0.8)
    # recessed light strips between the panels
    for (c, r, length) in [(3, 1, 2), (4, 1, 1)]:
        x = gap + c * (pw + gap)
        y = gap + r * (ph + gap)
        glow(cr, x + pw / 2, y + (ph * length + gap * (length - 1)) / 2, pw * 0.7, (ph * length) * 0.7)
    x = gap + 3 * (pw + gap)
    y = gap + 1 * (ph + gap)
    gloss_capsule(cr, x + pw * 0.38, y + 40 * s, pw * 0.24, ph * 2 + gap - 80 * s, shine=0.8)
    x = gap + 4 * (pw + gap)
    y = gap + 2 * (ph + gap)
    gloss_capsule(cr, x + 40 * s, y + ph * 0.36, pw - 80 * s, ph * 0.28, shine=0.8)
    # hazard band along the bottom row
    y = gap + 3 * (ph + gap) + ph * 0.72
    cr.save()
    cr.rectangle(gap, y, w - 2 * gap, 80 * s)
    cr.clip()
    cr.set_source_rgb(*ORANGE)
    cr.paint()
    cr.set_source_rgb(*WHITE)
    step = 160 * s
    for i in range(-2, int(w / step) + 4):
        x0 = i * step
        cr.move_to(x0, y)
        cr.line_to(x0 + step / 2, y)
        cr.line_to(x0 + step / 2 - 80 * s, y + 80 * s)
        cr.line_to(x0 - 80 * s, y + 80 * s)
        cr.close_path()
    cr.fill()
    cr.restore()


def glow(cr, cx, cy, rx, ry):
    cr.save()
    cr.translate(cx, cy)
    cr.scale(rx, ry)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0, *mix(AMBER, WHITE, 0.4), 0.30)
    g.add_color_stop_rgba(1, *AMBER, 0)
    cr.set_source(g)
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.fill()
    cr.restore()


def ribbons(cr, w, h):
    """Parallel glossy bands sweeping up out of the lower left: motion drawn
    as clean geometry."""
    daylight(cr, w, h, sun=(0.85, 0.1))
    s = h / 2160
    bands = [(ORANGE, 150), (WHITE, 90), (AMBER, 60), (WHITE, 40), (RED, 70), (WHITE, 120), (ORANGE, 46), (SHADE, 30)]
    off = 0
    for color, thick in bands:
        t = thick * s
        sweep(cr, w, h, off * s, t, color)
        off += thick + 26
    caption(cr, w, h, '05', 'RED', top=True)


def sweep(cr, w, h, off, t, color):
    def path(o):
        cr.move_to(-200, h * 0.95 - o)
        cr.curve_to(w * 0.35, h * 0.95 - o, w * 0.55, h * 0.25 - o, w + 200, h * 0.18 - o)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    # shadow
    cr.save()
    cr.translate(0, t * 0.35 + 10)
    path(off)
    cr.set_source_rgba(*mix(DEEP, (0, 0, 0), 0.3), 0.28)
    cr.set_line_width(t)
    cr.stroke()
    cr.restore()
    path(off)
    cr.set_source_rgb(*color)
    cr.set_line_width(t)
    cr.stroke()
    if color != SHADE:
        # specular stripe along the upper third of the band
        path(off + t * 0.22)
        cr.set_source_rgba(1, 1, 1, 0.55 if color != WHITE else 0.0)
        cr.set_line_width(t * 0.22)
        cr.stroke()
        if color == WHITE:
            path(off - t * 0.4)
            cr.set_source_rgba(*SHADE, 0.9)
            cr.set_line_width(max(2, t * 0.08))
            cr.stroke()


def capsule(cr, w, h):
    """One big glossy orange pill on white, the acronym set beside it."""
    daylight(cr, w, h, sun=(0.6, 0.0), floor=0.78)
    s = h / 2160
    x, y, cw, ch = 1880 * s, 1090 * s, 1560 * s, 600 * s
    soft_shadow(cr, x + cw / 2, h * 0.78 + 8 * s, cw * 0.55, 60 * s, alpha=0.32)
    gloss_capsule(cr, x, y, cw, ch, shine=0.92)
    ty = 560 * s
    for i, (head, tail) in enumerate([('D', 'AYLIGHT'), ('O', 'RANGE'), ('R', 'ED'), ('F', 'UTURISM'), ('GRAPH', 'IC')]):
        yy = ty + i * 150 * s
        if head == 'GRAPH':
            wd = label(cr, 300 * s, yy, 'GRAPH', 118 * s, WHITE, alpha=0.45)
            label(cr, 300 * s + wd, yy, 'IC', 118 * s, WHITE)
        else:
            wd = label(cr, 300 * s, yy, head, 118 * s, WHITE)
            label(cr, 300 * s + wd, yy, tail, 118 * s, WHITE, alpha=0.45)
    label(cr, x + cw / 2, y + ch * 0.64, 'DORFIC', 190 * s, WHITE, align=0.5, spacing=0.12)


SCENES = {
    'bubbles': (1, bubbles),
    'blades': (2, blades),
    'hexcells': (3, hexcells),
    'panels': (4, panels),
    'ribbons': (5, ribbons),
    'capsule': (6, capsule),
}


def main(args):
    scale = 1.0
    if '--scale' in args:
        i = args.index('--scale')
        scale = float(args[i + 1])
        del args[i:i + 2]
    names = args or list(SCENES)
    w, h = int(W * scale), int(H * scale)
    OUT.mkdir(exist_ok=True)
    for name in names:
        n, fn = SCENES[name]
        surf, cr = canvas(w, h)
        fn(cr, w, h)
        path = OUT / f'{n}-{name}.jpg'
        finish(surf, path)
        print(path)


if __name__ == '__main__':
    main(sys.argv[1:])
