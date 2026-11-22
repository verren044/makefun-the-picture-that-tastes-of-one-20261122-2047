#!/usr/bin/env python3
# The picture that tastes of one — make.fun entry.
# Judging: one hero ingredient, a single ripe strawberry, drawn entirely in code.
# Output: entry.png, 1024x1024 PNG, under 1 MiB.
# Deterministic: fixed seed, no clock, no network, no paid APIs.
"""The picture that tastes of one ingredient.

Draws one hero ingredient - a single ripe strawberry, dew-fresh, in macro -
entirely in code with Pillow. Deterministic: fixed seed, no clock, no network.
Writes entry.png (1024x1024) to MAKEFUN_OUTPUT_DIR (default /output).

Run:  mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
"""
import math
import os
import random
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

W = H = 1024
BASE = os.path.dirname(os.path.abspath(__file__))


def font(name, size):
    p = os.path.join(BASE, "fonts", name)
    try:
        return ImageFont.truetype(p, size)
    except Exception:
        for cand in ("/usr/share/fonts/truetype/dejavu/" + name,):
            try:
                return ImageFont.truetype(cand, size)
            except Exception:
                pass
    return ImageFont.load_default()


def vgrad(w, h, top, bottom):
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return g.resize((w, h))


def soft_layer(size, blur):
    layer = Image.new("RGBA", size, (0, 0, 0, 0))
    return layer, ImageDraw.Draw(layer)


def paste_soft(base, layer, blur):
    if blur:
        layer = layer.filter(ImageFilter.GaussianBlur(blur))
    base.alpha_composite(layer)


# ---------------------------------------------------------------- background
img = vgrad(W, H, (58, 26, 18), (24, 12, 9)).convert("RGBA")
rnd = random.Random(20261122)

# warm key-light glow, upper left
glow, gd = soft_layer((W, H), 0)
gd.ellipse([40, -260, 760, 420], fill=(255, 190, 110, 46))
paste_soft(img, glow, 90)

# bokeh
bok, bd = soft_layer((W, H), 0)
for _ in range(16):
    x = rnd.randint(-60, W)
    y = rnd.randint(-40, H)
    r = rnd.randint(18, 90)
    c = rnd.choice([(255, 170, 90), (255, 120, 70), (200, 60, 50), (255, 210, 140)])
    bd.ellipse([x - r, y - r, x + r, y + r], fill=c + (rnd.randint(18, 52),))
paste_soft(img, bok, 26)

# soft shadow / plate under the berry
sh, sd = soft_layer((W, H), 0)
sd.ellipse([250, 830, 790, 940], fill=(0, 0, 0, 130))
paste_soft(img, sh, 34)

# ---------------------------------------------------------------- berry shape
CX = 512
TOP, BOT = 175, 895
MAXW = 305


def half_width(t):
    """t: 0 top -> 1 bottom point."""
    return MAXW * (math.sin(math.pi * (0.18 + 0.82 * t)) ** 0.9)


def outline_points():
    pts = []
    for i in range(0, 61):
        t = i / 60
        y = TOP + (BOT - TOP) * t
        pts.append((CX - half_width(t), y))
    for i in range(60, -1, -1):
        t = i / 60
        y = TOP + (BOT - TOP) * t
        pts.append((CX + half_width(t), y))
    return pts


mask = Image.new("L", (W, H), 0)
md = ImageDraw.Draw(mask)
md.polygon(outline_points(), fill=255)
mask = mask.filter(ImageFilter.GaussianBlur(2))

# berry body: vertical gradient + warm radial light
body = vgrad(W, H, (238, 58, 52), (150, 12, 22)).convert("RGBA")
light, ld = soft_layer((W, H), 0)
ld.ellipse([300, 60, 640, 520], fill=(255, 120, 95, 95))
ld.ellipse([640, 420, 900, 900], fill=(90, 4, 12, 110))
paste_soft(body, light, 70)
body.putalpha(mask)
img.alpha_composite(body)

# fine flesh texture: speckles inside the berry only
tex = Image.new("RGBA", (W, H), (0, 0, 0, 0))
td = ImageDraw.Draw(tex)
for _ in range(2600):
    t = rnd.random()
    y = TOP + (BOT - TOP) * t
    hw = half_width(t) * 0.96
    x = CX + rnd.uniform(-hw, hw)
    c = rnd.choice([(255, 90, 80), (190, 20, 30), (255, 130, 110), (120, 8, 16)])
    td.point((x, y), fill=c + (rnd.randint(28, 70),))
tex.putalpha(Image.composite(tex.split()[3], Image.new("L", (W, H), 0), mask))
img.alpha_composite(tex)

# ---------------------------------------------------------------- seeds
def seed_layer(angle, scale=1.0):
    s = Image.new("RGBA", (34, 48), (0, 0, 0, 0))
    d = ImageDraw.Draw(s)
    d.ellipse([4, 4, 30, 44], fill=(255, 232, 168, 255))
    d.ellipse([9, 9, 25, 39], fill=(255, 244, 205, 255))
    d.ellipse([4, 4, 30, 44], outline=(176, 120, 40, 220), width=2)
    s = s.rotate(angle, expand=True, resample=Image.BICUBIC)
    if scale != 1.0:
        s = s.resize((int(s.width * scale), int(s.height * scale)), Image.LANCZOS)
    return s


for row, t in enumerate([0.16, 0.26, 0.36, 0.46, 0.56, 0.66, 0.76, 0.86]):
    y = TOP + (BOT - TOP) * t
    hw = half_width(t)
    n = max(2, int(hw / 52))
    off = 0.5 if row % 2 else 0.0
    for k in range(n):
        fx = -0.82 + 1.64 * ((k + 0.5 + off) / n if k + off < n else (k + 0.5) / n)
        if abs(fx) > 0.88:
            continue
        x = CX + fx * hw
        ang = -28 * fx + rnd.uniform(-8, 8)
        # shallow pit shadow under the seed
        pit = Image.new("RGBA", (40, 54), (0, 0, 0, 0))
        pd = ImageDraw.Draw(pit)
        pd.ellipse([5, 6, 35, 48], fill=(120, 8, 14, 90))
        pit = pit.rotate(ang, expand=True, resample=Image.BICUBIC)
        img.alpha_composite(pit, (int(x - pit.width / 2), int(y - pit.height / 2) + 3))
        s = seed_layer(ang, scale=0.85 + 0.22 * rnd.random())
        img.alpha_composite(s, (int(x - s.width / 2), int(y - s.height / 2)))

# ---------------------------------------------------------------- dew drops
dew = Image.new("RGBA", (W, H), (0, 0, 0, 0))
dd = ImageDraw.Draw(dew)
for _ in range(14):
    t = 0.15 + 0.7 * rnd.random()
    y = TOP + (BOT - TOP) * t
    hw = half_width(t) * 0.9
    x = CX + rnd.uniform(-hw, hw)
    r = rnd.randint(6, 15)
    dd.ellipse([x - r, y - r, x + r, y + r], fill=(255, 255, 255, 52))
    dd.ellipse([x - r, y - r, x + r, y + r], outline=(255, 255, 255, 110), width=1)
    dd.ellipse([x - r * 0.45, y - r * 0.55, x - r * 0.05, y - r * 0.15],
               fill=(255, 255, 255, 235))
dew.putalpha(Image.composite(dew.split()[3], Image.new("L", (W, H), 0), mask))
img.alpha_composite(dew)

# gloss highlight on the berry shoulder
gl, gld = soft_layer((W, H), 0)
gld.ellipse([330, 190, 520, 330], fill=(255, 255, 255, 88))
gld.ellipse([360, 210, 480, 300], fill=(255, 255, 255, 90))
paste_soft(gl, 0) if False else None
gl = gl.filter(ImageFilter.GaussianBlur(18))
gl.putalpha(Image.composite(gl.split()[3], Image.new("L", (W, H), 0), mask))
img.alpha_composite(gl)

# ---------------------------------------------------------------- calyx + stem
leaves, lvd = soft_layer((W, H), 0)
leaf_defs = [(-150, 210), (-105, 175), (-60, 150), (-15, 135), (30, 145),
             (75, 168), (118, 200)]
for dx, ln in leaf_defs:
    tip_x = CX + dx * 1.9
    tip_y = TOP - 55 - (ln - 135) * 0.9
    bx = CX + dx * 0.55
    by = TOP + 18
    wdt = 26
    px, py = bx - wdt, by + 6
    qx, qy = bx + wdt, by + 6
    lvd.polygon([(tip_x, tip_y), (qx, qy), (bx, by + 34), (px, py)],
                fill=(46, 122, 51, 255))
    lvd.line([(bx, by + 8), (tip_x, tip_y)], fill=(120, 200, 110, 200), width=3)
leaves = leaves.filter(ImageFilter.GaussianBlur(1))
img.alpha_composite(leaves)
# stem
stem, std = soft_layer((W, H), 0)
std.rounded_rectangle([CX - 11, TOP - 108, CX + 11, TOP - 8], radius=10,
                      fill=(74, 110, 58, 255))
std.line([(CX - 4, TOP - 100), (CX - 4, TOP - 16)], fill=(140, 185, 120, 200), width=4)
img.alpha_composite(stem.filter(ImageFilter.GaussianBlur(1)))

# ---------------------------------------------------------------- halved berry, bottom-left (cropped)
hx, hy, hr = 104, 884, 102
half = Image.new("RGBA", (W, H), (0, 0, 0, 0))
hd = ImageDraw.Draw(half)
hd.ellipse([hx - hr, hy - hr, hx + hr, hy + hr], fill=(214, 32, 40, 255))
hd.ellipse([hx - hr + 14, hy - hr + 14, hx + hr - 14, hy + hr - 14],
           fill=(248, 150, 140, 255))
hd.ellipse([hx - hr + 30, hy - hr + 30, hx + hr - 30, hy + hr - 30],
           fill=(252, 196, 186, 255))
# white core star
for a in range(6):
    ang = math.radians(a * 60 + 12)
    x2 = hx + int(52 * math.cos(ang))
    y2 = hy + int(52 * math.sin(ang))
    hd.line([(hx, hy), (x2, y2)], fill=(255, 244, 230, 255), width=9)
hd.ellipse([hx - 16, hy - 16, hx + 16, hy + 16], fill=(255, 246, 235, 255))
# seed ring on the cut face
for a in range(10):
    ang = math.radians(a * 36 + 8)
    sx = hx + int(86 * math.cos(ang))
    sy = hy + int(86 * math.sin(ang))
    hd.ellipse([sx - 7, sy - 11, sx + 7, sy + 11], fill=(255, 232, 168, 255),
               outline=(176, 120, 40, 255))
half = half.filter(ImageFilter.GaussianBlur(1))
img.alpha_composite(half)
# gloss on the cut face
cg, cgd = soft_layer((W, H), 0)
cgd.ellipse([hx - 70, hy - 88, hx + 10, hy - 18], fill=(255, 255, 255, 70))
img.alpha_composite(cg.filter(ImageFilter.GaussianBlur(10)))

# ---------------------------------------------------------------- vignette + caption
vig = Image.new("RGBA", (W, H), (0, 0, 0, 0))
vd = ImageDraw.Draw(vig)
vd.rectangle([0, 0, W, H], outline=(0, 0, 0, 0))
for i in range(60):
    a = int(150 * (i / 60) ** 2)
    vd.rectangle([i, i, W - 1 - i, H - 1 - i], outline=(10, 4, 3, a))
img.alpha_composite(vig.filter(ImageFilter.GaussianBlur(6)))

d = ImageDraw.Draw(img)
cap = font("DejaVuSerif-Bold.ttf", 30)
text = "ONE INGREDIENT  ·  STRAWBERRY"
tw = d.textlength(text, font=cap)
d.text(((W - tw) / 2 + 2, 968 + 2), text, font=cap, fill=(0, 0, 0, 160))
d.text(((W - tw) / 2, 968), text, font=cap, fill=(245, 230, 200, 255))

# ---------------------------------------------------------------- write output
outdir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(outdir, exist_ok=True)
out = os.path.join(outdir, "entry.png")
rgb = img.convert("RGB")
rgb.save(out, "PNG", optimize=True)
if os.path.getsize(out) > 1048576:  # gate cap: fall back to JPEG bytes
    rgb.save(out, "JPEG", quality=92, optimize=True)
print("wrote", out, os.path.getsize(out), "bytes")
