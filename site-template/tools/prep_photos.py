#!/usr/bin/env python3
"""Готовит фото компании для сайта: уменьшает и сохраняет пару .jpg + .webp.

    python3 tools/prep_photos.py ~/Downloads/фото-компании  assets/<slug>

Исходники любого размера и формата. На выходе файлы photo-01.jpg/.webp, photo-02… шириной до 1280 px.
Скрипт печатает ширину и высоту каждого файла: их нужно вписать в JSON компании (поля w и h)."""
import sys
from pathlib import Path
from PIL import Image, ImageOps

if len(sys.argv) != 3:
    sys.exit(__doc__)
src, dst = Path(sys.argv[1]).expanduser(), Path(sys.argv[2])
dst.mkdir(parents=True, exist_ok=True)
files = sorted(p for p in src.iterdir() if p.suffix.lower() in ('.jpg', '.jpeg', '.png', '.webp', '.heic'))
for i, f in enumerate(files, 1):
    im = ImageOps.exif_transpose(Image.open(f)).convert('RGB')
    im.thumbnail((1280, 1280), Image.LANCZOS)
    name = f'photo-{i:02d}'
    im.save(dst / f'{name}.jpg', quality=82, optimize=True, progressive=True)
    im.save(dst / f'{name}.webp', quality=80, method=6)
    print(f'{dst}/{name}  {im.size[0]}x{im.size[1]}  ← {f.name}')
