"""
ui/frontend/theme.py
Shared colors, fonts and image helpers for the front-end screens.
"""

import os
from functools import lru_cache

import customtkinter as ctk
from PIL import Image, ImageDraw, ImageFilter, ImageFont


PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
IMAGE_DIR = os.path.join(PROJECT_ROOT, "assets", "images")

BG_DARK = "#07090c"
PANEL = "#0b0f14"
PANEL_LIGHT = "#121922"
PANEL_HOVER = "#1a2430"
BORDER = "#24303d"
GOLD = "#c9a24d"
GOLD_BRIGHT = "#f0c867"
TEXT = "#d8dee6"
TEXT_DIM = "#8a96a3"
TEXT_MUTED = "#5b6672"
BLUE_SIDE = "#4a9eff"
RED_SIDE = "#e05252"
SUCCESS = "#5fbf6f"
DANGER = "#c94a4a"

HEADING_FAMILY = "Bahnschrift SemiBold"
BODY_FAMILY = "Bahnschrift"
CONDENSED_FAMILY = "Bahnschrift SemiBold Condensed"

_PIL_FONT_CANDIDATES = [
    r"C:\Windows\Fonts\bahnschrift.ttf",
    r"C:\Windows\Fonts\impact.ttf",
    r"C:\Windows\Fonts\arialbd.ttf",
]


def font(size, weight="normal", family=None):
    if family is None:
        family = HEADING_FAMILY if weight == "bold" else BODY_FAMILY
    return ctk.CTkFont(family=family, size=size)


def side_color(side):
    return BLUE_SIDE if side == "Blue" else RED_SIDE


@lru_cache(maxsize=None)
def load_art(name):
    path = os.path.join(IMAGE_DIR, name)
    if os.path.exists(path):
        return Image.open(path).convert("RGB")
    fallback = Image.new("RGB", (1024, 576), (12, 18, 26))
    draw = ImageDraw.Draw(fallback)
    for x in range(0, 1024, 32):
        draw.line([(x, 0), (x, 576)], fill=(20, 30, 42))
    for y in range(0, 576, 32):
        draw.line([(0, y), (1024, y)], fill=(20, 30, 42))
    return fallback


def pil_font(size, bold=True):
    for path in _PIL_FONT_CANDIDATES:
        if os.path.exists(path):
            f = ImageFont.truetype(path, size)
            if path.endswith("bahnschrift.ttf"):
                try:
                    f.set_variation_by_name("Bold" if bold else "Regular")
                except (OSError, ValueError):
                    pass
            return f
    return ImageFont.load_default(size=size)


def cover_crop(image, width, height, focus_x=0.5, focus_y=0.5):
    """Scale and crop an image so it fully covers width x height."""
    width, height = max(1, int(width)), max(1, int(height))
    src_w, src_h = image.size
    scale = max(width / src_w, height / src_h)
    new_w, new_h = int(src_w * scale + 0.5), int(src_h * scale + 0.5)
    resized = image.resize((new_w, new_h), Image.LANCZOS)
    left = int((new_w - width) * focus_x)
    top = int((new_h - height) * focus_y)
    return resized.crop((left, top, left + width, top + height))


def hex_to_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))


def horizontal_fade(size, color, start_alpha, end_alpha, reverse=False):
    width, height = size
    rgb = hex_to_rgb(color)
    gradient = Image.new("L", (width, 1))
    for x in range(width):
        t = x / max(1, width - 1)
        if reverse:
            t = 1 - t
        gradient.putpixel((x, 0), int(start_alpha + (end_alpha - start_alpha) * t))
    alpha = gradient.resize((width, height))
    layer = Image.new("RGBA", (width, height), rgb + (0,))
    layer.putalpha(alpha)
    return layer


def vertical_fade(size, color, start_alpha, end_alpha):
    width, height = size
    rgb = hex_to_rgb(color)
    gradient = Image.new("L", (1, height))
    for y in range(height):
        t = y / max(1, height - 1)
        gradient.putpixel((0, y), int(start_alpha + (end_alpha - start_alpha) * t))
    alpha = gradient.resize((width, height))
    layer = Image.new("RGBA", (width, height), rgb + (0,))
    layer.putalpha(alpha)
    return layer


def glow_text(text, size, color=GOLD_BRIGHT, glow=GOLD, glow_radius=10, tracking=0, bold=True):
    """Render text with a soft outer glow onto a transparent image."""
    fnt = pil_font(size, bold=bold)
    chars = list(text)
    widths = [fnt.getbbox(c)[2] - fnt.getbbox(c)[0] if c != " " else size // 3 for c in chars]
    total_w = sum(widths) + tracking * (len(chars) - 1)
    ascent, descent = fnt.getmetrics()
    pad = glow_radius * 3
    img = Image.new("RGBA", (total_w + pad * 2, ascent + descent + pad * 2), (0, 0, 0, 0))

    def draw_chars(target, fill):
        d = ImageDraw.Draw(target)
        x = pad
        for c, w in zip(chars, widths):
            if c != " ":
                d.text((x - fnt.getbbox(c)[0], pad), c, font=fnt, fill=fill)
            x += w + tracking

    glow_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_chars(glow_layer, hex_to_rgb(glow) + (200,))
    glow_layer = glow_layer.filter(ImageFilter.GaussianBlur(glow_radius))
    img = Image.alpha_composite(img, glow_layer)
    text_layer = Image.new("RGBA", img.size, (0, 0, 0, 0))
    draw_chars(text_layer, hex_to_rgb(color) + (255,))
    return Image.alpha_composite(img, text_layer)


def banner_image(art_name, width, height, title, subtitle, focus_y=0.5):
    """Wide screen-header banner: art with a dark left fade and title text."""
    base = cover_crop(load_art(art_name), width, height, focus_y=focus_y).convert("RGBA")
    base = Image.alpha_composite(base, horizontal_fade(base.size, BG_DARK, 250, 40))
    base = Image.alpha_composite(base, vertical_fade(base.size, BG_DARK, 0, 160))
    title_img = glow_text(title.upper(), int(height * 0.30), tracking=int(height * 0.02), glow_radius=8)
    base.alpha_composite(title_img, (int(height * 0.25) - 24, int(height * 0.14) - 24))
    d = ImageDraw.Draw(base)
    d.text((int(height * 0.25), int(height * 0.62)), subtitle.upper(),
           font=pil_font(int(height * 0.12), bold=False), fill=hex_to_rgb(TEXT_DIM))
    d.line([(0, height - 2), (width, height - 2)], fill=hex_to_rgb(GOLD), width=2)
    return base
