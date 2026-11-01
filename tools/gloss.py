"""Drawing primitives for the DORFic backgrounds: glossy orange plastic, clear
glass, white plastic and frosted panels on a sunlit orange ground.

Everything is pycairo plus numpy (no PIL). Colors are 0..1 RGB tuples.
"""
import io
import math
import subprocess

import cairo
import numpy as np

from palette import KEYS


def rgb(key_or_hex):
    if key_or_hex.startswith('#'):
        h = key_or_hex
        return tuple(int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return tuple(c / 255 for c in KEYS[key_or_hex])


def mix(a, b, t):
    return tuple(x + (y - x) * t for x, y in zip(a, b))


WHITE = (1, 1, 1)
PAPER = rgb('#f7f4ee')             # white plastic
SHADE = rgb('#ddd5c8')
INK = rgb('foreground')
ORANGE = rgb('#f25c05')            # DORFic orange (the palette accent is gold)
AMBER = rgb('#ff9a2e')
EMBER = rgb('#b33d00')
RED = rgb('#d4231a')
STEEL = rgb('#b9a796')
FIELD = rgb('#ee7a12')               # the sunlit orange ground
SUN = rgb('#ffb648')
DEEP = rgb('background')             # the terminal ember


def canvas(w, h):
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, w, h)
    return surf, cairo.Context(surf)


def daylight(cr, w, h, sun=(0.78, 0.12), floor=None):
    """Sunlit orange field: a hot amber-white bloom where the sun is, falling
    off to deep ember in the far corner. `floor` (0..1) adds a studio horizon."""
    cr.set_source_rgb(*FIELD)
    cr.paint()
    g = cairo.RadialGradient(w * sun[0], h * sun[1], 0, w * sun[0], h * sun[1], max(w, h) * 1.15)
    g.add_color_stop_rgba(0.0, *mix(SUN, WHITE, 0.55), 1)
    g.add_color_stop_rgba(0.18, *SUN, 0.95)
    g.add_color_stop_rgba(0.55, *FIELD, 0.6)
    g.add_color_stop_rgba(1.0, *EMBER, 1)
    cr.set_source(g)
    cr.paint()
    if floor is not None:
        y = h * floor
        f = cairo.LinearGradient(0, y - h * 0.02, 0, h)
        f.add_color_stop_rgba(0, *SUN, 0)
        f.add_color_stop_rgba(0.04, *mix(SUN, WHITE, 0.35), 0.45)
        f.add_color_stop_rgba(0.35, *FIELD, 0.2)
        f.add_color_stop_rgba(1, *EMBER, 0.55)
        cr.set_source(f)
        cr.rectangle(0, y - h * 0.02, w, h)
        cr.fill()


def soft_shadow(cr, cx, cy, rx, ry, alpha=0.28, color=None):
    """Contact shadow: a blurred ellipse faked with a radial gradient."""
    color = color or mix(DEEP, (0, 0, 0), 0.35)
    cr.save()
    cr.translate(cx, cy)
    cr.scale(rx, ry)
    g = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    g.add_color_stop_rgba(0, *color, alpha)
    g.add_color_stop_rgba(0.45, *color, alpha * 0.55)
    g.add_color_stop_rgba(1, *color, 0)
    cr.set_source(g)
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.fill()
    cr.restore()


def gloss_sphere(cr, cx, cy, r, base=ORANGE, light=AMBER, dark=EMBER):
    """Glossy plastic ball: body gradient, bounce light, specular cap."""
    g = cairo.RadialGradient(cx - r * 0.35, cy - r * 0.45, r * 0.05, cx, cy, r)
    g.add_color_stop_rgb(0, *mix(light, WHITE, 0.25))
    g.add_color_stop_rgb(0.45, *base)
    g.add_color_stop_rgb(0.88, *dark)
    g.add_color_stop_rgb(1, *mix(dark, DEEP, 0.5))
    cr.set_source(g)
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.fill()
    # warm bounce from the white floor along the lower rim
    cr.save()
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.clip()
    b = cairo.RadialGradient(cx, cy + r * 1.05, r * 0.1, cx, cy + r * 1.05, r * 0.75)
    b.add_color_stop_rgba(0, *mix(light, WHITE, 0.5), 0.75)
    b.add_color_stop_rgba(1, *light, 0)
    cr.set_source(b)
    cr.paint()
    cr.restore()
    # specular cap: a flattened ellipse fading downward
    cr.save()
    cr.translate(cx - r * 0.08, cy - r * 0.5)
    cr.scale(r * 0.66, r * 0.4)
    s = cairo.LinearGradient(0, -1, 0, 1)
    s.add_color_stop_rgba(0, 1, 1, 1, 0.95)
    s.add_color_stop_rgba(0.55, 1, 1, 1, 0.28)
    s.add_color_stop_rgba(1, 1, 1, 1, 0)
    cr.set_source(s)
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.fill()
    cr.restore()
    # pin-point hotspot
    hs = cairo.RadialGradient(cx - r * 0.38, cy - r * 0.55, 0, cx - r * 0.38, cy - r * 0.55, r * 0.16)
    hs.add_color_stop_rgba(0, 1, 1, 1, 1)
    hs.add_color_stop_rgba(1, 1, 1, 1, 0)
    cr.set_source(hs)
    cr.arc(cx - r * 0.38, cy - r * 0.55, r * 0.16, 0, 2 * math.pi)
    cr.fill()


def glass_sphere(cr, cx, cy, r, tint=ORANGE):
    """Clear soap-glass bubble: bright rim, faint body, orange caustic below."""
    g = cairo.RadialGradient(cx, cy, r * 0.55, cx, cy, r)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.06)
    g.add_color_stop_rgba(0.82, 1, 1, 1, 0.18)
    g.add_color_stop_rgba(0.96, *mix(WHITE, tint, 0.25), 0.55)
    g.add_color_stop_rgba(1, *mix(INK, tint, 0.5), 0.35)
    cr.set_source(g)
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.fill()
    cr.save()
    cr.arc(cx, cy, r, 0, 2 * math.pi)
    cr.clip()
    c = cairo.RadialGradient(cx + r * 0.1, cy + r * 0.75, 0, cx + r * 0.1, cy + r * 0.75, r * 0.7)
    c.add_color_stop_rgba(0, *mix(tint, AMBER, 0.4), 0.55)
    c.add_color_stop_rgba(1, *tint, 0)
    cr.set_source(c)
    cr.paint()
    cr.restore()
    cr.save()
    cr.translate(cx - r * 0.3, cy - r * 0.48)
    cr.rotate(-0.5)
    cr.scale(r * 0.38, r * 0.17)
    s = cairo.RadialGradient(0, 0, 0, 0, 0, 1)
    s.add_color_stop_rgba(0, 1, 1, 1, 0.95)
    s.add_color_stop_rgba(1, 1, 1, 1, 0)
    cr.set_source(s)
    cr.arc(0, 0, 1, 0, 2 * math.pi)
    cr.fill()
    cr.restore()


def round_rect(cr, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    cr.new_sub_path()
    cr.arc(x + w - r, y + r, r, -math.pi / 2, 0)
    cr.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    cr.arc(x + r, y + h - r, r, math.pi / 2, math.pi)
    cr.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    cr.close_path()


def gloss_capsule(cr, x, y, w, h, r=None, base=ORANGE, light=AMBER, dark=EMBER, shine=0.9):
    """Aqua-era glossy pill: vertical body gradient, a top highlight band set
    inside the edge, and a soft glow pooled at the bottom."""
    r = h / 2 if r is None else r
    round_rect(cr, x, y, w, h, r)
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, *mix(base, dark, 0.25))
    g.add_color_stop_rgb(0.5, *base)
    g.add_color_stop_rgb(1, *mix(light, WHITE, 0.2))
    cr.set_source(g)
    cr.fill_preserve()
    cr.set_source_rgba(*mix(dark, DEEP, 0.5), 0.6)
    cr.set_line_width(max(1, h * 0.02))
    cr.stroke()
    inset = h * 0.07
    round_rect(cr, x + inset * 1.6, y + inset, w - inset * 3.2, h * 0.46, max(1, r - inset))
    s = cairo.LinearGradient(0, y + inset, 0, y + inset + h * 0.46)
    s.add_color_stop_rgba(0, 1, 1, 1, shine)
    s.add_color_stop_rgba(1, 1, 1, 1, shine * 0.08)
    cr.set_source(s)
    cr.fill()


def white_panel(cr, x, y, w, h, r, depth=None):
    """White plastic panel with a soft top light and a darker lower lip."""
    depth = depth or h * 0.04
    round_rect(cr, x, y + depth * 0.6, w, h, r)
    cr.set_source_rgba(*mix(DEEP, (0, 0, 0), 0.3), 0.3)
    cr.fill()
    round_rect(cr, x, y, w, h, r)
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgb(0, 1, 1, 1)
    g.add_color_stop_rgb(0.7, *mix(WHITE, PAPER, 0.8))
    g.add_color_stop_rgb(1, *mix(PAPER, SHADE, 0.7))
    cr.set_source(g)
    cr.fill_preserve()
    cr.set_source_rgba(*SHADE, 0.9)
    cr.set_line_width(max(1, r * 0.06))
    cr.stroke()


def glass_panel(cr, x, y, w, h, r):
    """Frosted glass tile: a faint white body, brighter toward the top, a
    highlight band and a crisp white rim."""
    round_rect(cr, x, y + h * 0.02, w, h, r)
    cr.set_source_rgba(*mix(DEEP, (0, 0, 0), 0.3), 0.18)
    cr.fill()
    round_rect(cr, x, y, w, h, r)
    g = cairo.LinearGradient(0, y, 0, y + h)
    g.add_color_stop_rgba(0, 1, 1, 1, 0.34)
    g.add_color_stop_rgba(0.5, 1, 1, 1, 0.12)
    g.add_color_stop_rgba(1, 1, 1, 1, 0.22)
    cr.set_source(g)
    cr.fill_preserve()
    cr.set_source_rgba(1, 1, 1, 0.75)
    cr.set_line_width(max(1, r * 0.06))
    cr.stroke()
    inset = r * 0.35
    round_rect(cr, x + inset, y + inset * 0.6, w - 2 * inset, h * 0.42, r * 0.7)
    s = cairo.LinearGradient(0, y, 0, y + h * 0.45)
    s.add_color_stop_rgba(0, 1, 1, 1, 0.45)
    s.add_color_stop_rgba(1, 1, 1, 1, 0)
    cr.set_source(s)
    cr.fill()


def label(cr, x, y, text, size, color=INK, weight=cairo.FONT_WEIGHT_BOLD, family='Nimbus Sans', align=0.0, alpha=1.0, spacing=0.0):
    cr.select_font_face(family, cairo.FONT_SLANT_NORMAL, weight)
    cr.set_font_size(size)
    widths = [cr.text_extents(ch).x_advance for ch in text]
    total = sum(widths) + spacing * size * max(0, len(text) - 1)
    cx = x - total * align
    cr.set_source_rgba(*color, alpha)
    for ch, adv in zip(text, widths):
        cr.move_to(cx, y)
        cr.show_text(ch)
        cx += adv + spacing * size
    return total


def finish(surf, path, grain=1.4, seed=7):
    """Add a touch of luminance grain (kills gradient banding) and save."""
    surf.flush()
    h, w = surf.get_height(), surf.get_width()
    buf = np.ndarray((h, surf.get_stride() // 4, 4), np.uint8, surf.get_data())[:, :w]
    rng = np.random.default_rng(seed)
    noise = rng.normal(0, grain, (h, w, 1))
    px = buf[..., :3].astype(np.float32) + noise
    buf[..., :3] = np.clip(px, 0, 255).astype(np.uint8)
    surf.mark_dirty()
    if str(path).endswith('.png'):
        surf.write_to_png(str(path))
        return
    # JPEG keeps the repo small; the grain hides any blocking in the gradients.
    tmp = io.BytesIO()
    surf.write_to_png(tmp)
    subprocess.run(['magick', 'png:-', '-quality', '92', '-sampling-factor', '4:4:4', str(path)],
                   input=tmp.getvalue(), check=True)
