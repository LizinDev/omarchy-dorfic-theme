#!/usr/bin/env python3
"""Write this theme's shell.<section>.toml overrides.

    python3 tools/shell-overrides.py

A section override REPLACES the whole generated section, so each file restates
every key Omarchy generated and changes only the ones listed in OVERRIDES. The
generated values are read from the live shell.toml, so apply the theme first
(`omarchy theme set <slug>`), run this, then `omarchy theme refresh`. Re-run it
after any change to colors.toml: the restated values are frozen hex copies.

[gloss-bar] is not an Omarchy section: Omarchy appends it to shell.toml and
the Gloss Bar plugin reads it to draw glossy capsules behind the bar sections.
"""
import re
import sys
from pathlib import Path

THEME = Path(__file__).resolve().parent.parent
STATE = Path.home() / '.local/state/omarchy/current'

# Tinted orange glass everywhere (Hyprland blurs what is behind it), a
# white-gold gradient frame, and the chosen row as a white pill with ember text.
GLASS_CARD = {
    'background': '{background}',
    'background-alpha': 0.72,
    'scrim': '{darker_background}',
    'scrim-alpha': 0.25,
    'border': 'hyprland.active-border',
    'selected-background': '#ffffff',
    'selected-background-alpha': 0.92,
    'selected-text': '{background}',
    'selected-border': '#ffffff',
    'selected-border-alpha': 1.0,
}
OVERRIDES = {
    # The Gloss Bar capsules carry the bar, so the strip itself is clear.
    'bar': {'size-horizontal': 34, 'background-alpha': 0.0, 'text': '#ffffff'},
    'controls': {
        'selected-color': '{accent}', 'selected-fill-alpha': 0.28,
        'selected-border': '{accent}', 'selected-border-width': 1, 'selected-border-alpha': 0.9,
    },
    'popups': {'background-alpha': 0.78, 'border-width': 2},
    'tooltip': {'background-alpha': 0.82, 'border': 'hyprland.active-border'},
    'notifications': {'background-alpha': 0.78, 'border-width': 2},
    'menu': GLASS_CARD,
    'launcher': GLASS_CARD,
    'polkit': {'background-alpha': 0.82},
    'lock': {'background-alpha': 0.6, 'border': '#ffffff'},
}

# Clear glass capsules: almost no tint, so the blur does the work; the shape
# comes from a crisp white rim, a specular hairline on top and a gold one below.
# No drop shadow and only a whisper of glare: both read as plastic.
GLOSS_BAR = {
    'enabled': 'true',
    'fill-top': '#ffffff',
    'fill': '#c24a05',
    'fill-bottom': '#8f3000',
    'fill-alpha': 0.08,
    'rim': '#ffffff',
    'rim-alpha': 0.55,
    'shadow-alpha': 0,
    'shine-style': 'glare',
    'shine-alpha': 0.1,
    'glow-alpha': 0,
    'edge-light-alpha': 0.95,
    'edge-glow': '{accent}',
    'edge-glow-alpha': 0.6,
    'inset': 4,
    'padding': 8,
}


HEADER = [
    '# A section override REPLACES the whole section, so every generated key is',
    '# restated; hex values are frozen copies of colors.toml - re-run the tool',
    '# after any palette change.',
]


def palette():
    keys = {}
    for line in (THEME / 'colors.toml').read_text().splitlines():
        m = re.match(r'\s*([A-Za-z0-9_-]+)\s*=\s*"([^"]*)"', line)
        if m:
            keys[m.group(1)] = m.group(2)
    return keys


def sections(text):
    found, name = {}, None
    for line in text.splitlines():
        m = re.match(r'^\s*\[([^\]]+)\]', line)
        if m:
            name = m.group(1)
            found[name] = []
        elif name:
            found[name].append(line)
    return found
def literal(value):
    if isinstance(value, str):
        return '"%s"' % value
    return repr(value)


def main():
    slug = THEME.name.removeprefix('omarchy-').removesuffix('-theme')
    current = (STATE / 'theme.name').read_text().strip()
    if current != slug:
        sys.exit(f'apply the theme first: current is {current!r}, this is {slug!r}')
    colors = palette()
    generated = sections((STATE / 'theme/shell.toml').read_text())
    header_lines = set(HEADER)
    for section, changes in OVERRIDES.items():
        lines, done = [], set()
        for line in generated[section]:
            # Once the theme ships its overrides, the live section already
            # carries this tool's header; drop it so reruns do not stack it.
            if line in header_lines or line.startswith(f'# {slug} override for ['):
                continue
            m = re.match(r'^(\s*)([a-z-]+)(\s*=\s*)(.*)$', line)
            if m and m.group(2) in changes:
                value = changes[m.group(2)]
                if isinstance(value, str):
                    value = value.format(**colors)
                lines.append(m.group(1) + m.group(2) + m.group(3) + literal(value))
                done.add(m.group(2))
            else:
                lines.append(line)
        while lines and not lines[-1].strip():
            lines.pop()
        width = max((len(m.group(1)) for m in (re.match(r'^\s*([a-z-]+)\s*=', l) for l in lines) if m), default=0)
        for key in changes:
            if key not in done:
                value = changes[key]
                if isinstance(value, str):
                    value = value.format(**colors)
                lines.append(f'{key:<{width}} = {literal(value)}')
        header = [f'# {slug} override for [{section}], written by tools/shell-overrides.py.'] + HEADER
        (THEME / f'shell.{section}.toml').write_text('\n'.join(header + lines) + '\n')
        print(f'shell.{section}.toml')

    lines = [
        f'# {slug} [gloss-bar], written by tools/shell-overrides.py. Read by the',
        '# Gloss Bar plugin; Omarchy itself ignores this section.',
    ]
    pad = max(len(k) for k in GLOSS_BAR)
    for key, value in GLOSS_BAR.items():
        if isinstance(value, str):
            value = value.format(**colors)
        lines.append(f'{key:<{pad}} = {literal(value)}')
    (THEME / 'shell.gloss-bar.toml').write_text('\n'.join(lines) + '\n')
    print('shell.gloss-bar.toml')


main()
