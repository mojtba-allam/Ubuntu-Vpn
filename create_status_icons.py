#!/usr/bin/env python3
"""Create PNG versions of status icons."""

import cairosvg
import os

status_dir = 'ui/icons/status'
icons = ['connected', 'disconnected', 'connecting']

for icon in icons:
    svg_file = os.path.join(status_dir, f'{icon}.svg')
    png_file = os.path.join(status_dir, f'{icon}.png')
    if os.path.exists(svg_file):
        cairosvg.svg2png(url=svg_file, write_to=png_file, output_width=64, output_height=64)
        print(f'Created {png_file}')
