#!/usr/bin/env python3
"""Write kitty.conf, alacritty.toml and ghostty.conf with a see-through
background, so Hyprland's blur turns every terminal into orange glass.

    python3 -I tools/terminals.py

A theme file beats its template, so each is the stock template rendered with
this palette (via omarchy-theme-color) plus the opacity lines. Re-run after any
change to colors.toml.
"""
import re
import subprocess
from pathlib import Path

THEME = Path(__file__).resolve().parent.parent
TEMPLATES = Path('/usr/share/omarchy/default/themed')
OPACITY = 0.8

EXTRA = {
    'kitty.conf': f'\n# DORFic glass\nbackground_opacity {OPACITY}\n',
    'alacritty.toml': f'\n# DORFic glass\n[window]\nopacity = {OPACITY}\n',
    'ghostty.conf': f'\n# DORFic glass\nbackground-opacity = {OPACITY}\n',
}


def resolved():
    out = subprocess.run(['omarchy-theme-color', '--file', str(THEME / 'colors.toml'), '--all'],
                         capture_output=True, text=True, check=True).stdout
    return dict(line.split('\t', 1) for line in out.splitlines() if '\t' in line)


def main():
    colors = resolved()
    for name, extra in EXTRA.items():
        text = (TEMPLATES / f'{name}.tpl').read_text()

        def fill(m):
            key = m.group(1)
            if key not in colors:
                raise SystemExit(f'{name}: no value for {key}')
            return colors[key]

        text = re.sub(r'\{\{\s*([a-z_]+)\s*\}\}', fill, text)
        (THEME / name).write_text(text.rstrip('\n') + '\n' + extra)
        print(name)


main()
