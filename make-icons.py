#!/usr/bin/env python3
"""
生成 PWA 图标。改了主色后重跑一次：

    python3 make-icons.py

输出到 icons/：
    icon-192.png            192x192，普通图标
    icon-512.png            512x512，普通图标
    icon-maskable-512.png   512x512，Android 自适应图标（四周留足安全区）
    apple-touch-icon.png    180x180，iOS 主屏图标（不透明，iOS 自己切圆角）
"""

import os
from PIL import Image, ImageDraw

ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, 'icons')

BG = (11, 13, 16)          # #0b0d10 深色背景
COLORS = [
    (76, 141, 255),        # #4c8dff
    (110, 168, 255),       # #6ea8ff
    (110, 168, 255),
    (76, 141, 255),
]


def draw_icon(size, maskable=False):
    img = Image.new('RGB', (size, size), BG)
    d = ImageDraw.Draw(img)

    # maskable 图标要保证内容落在中心 80% 的圆形安全区内
    pad = size * (0.30 if maskable else 0.20)
    area = size - 2 * pad
    gap = area * 0.12
    cell = (area - gap) / 2
    radius = cell * 0.24

    i = 0
    for row in range(2):
        for col in range(2):
            x = pad + col * (cell + gap)
            y = pad + row * (cell + gap)
            d.rounded_rectangle([x, y, x + cell, y + cell], radius=radius, fill=COLORS[i])
            i += 1
    return img


def main():
    os.makedirs(OUT, exist_ok=True)
    tasks = [
        ('icon-192.png', 192, False),
        ('icon-512.png', 512, False),
        ('icon-maskable-512.png', 512, True),
        ('apple-touch-icon.png', 180, False),
    ]
    for name, size, maskable in tasks:
        img = draw_icon(size, maskable)
        img.save(os.path.join(OUT, name), 'PNG', optimize=True)
        print('生成 icons/%s  %dx%d%s' % (name, size, size, '  (maskable)' if maskable else ''))


if __name__ == '__main__':
    main()
