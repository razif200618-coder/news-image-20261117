#!/usr/bin/env python3
"""Compose the entry image for make.fun news-image-20261117.

"One Day on Earth" — a one-page newspaper front page summing up Tuesday
17 November 2026: 40 verified stories, 3 leads, 8 illustrated stories, a
world map with pins, and a numbered brief list. Every illustration is drawn
here from scratch with PIL flat shapes; no external assets.
"""
import math
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 26  # side margin

# ---- palette (deep teal + warm sand + amber; nothing copied from the tops) ----
PAPER   = (247, 242, 230)
INK     = (28, 36, 32)
TEAL    = (14, 79, 74)
TEAL_DK = (9, 56, 53)
TEAL_MD = (32, 110, 103)
AMBER   = (198, 124, 18)
AMBER_L = (233, 196, 120)
RED     = (178, 56, 40)
CARD    = (255, 255, 255)
BORDER  = (214, 200, 168)
GREY    = (110, 104, 90)
SEA     = (203, 220, 216)
LAND    = (232, 219, 190)
SKY     = (220, 233, 239)

F = "/usr/share/fonts/truetype/dejavu/"
def font(name, size):
    return ImageFont.truetype(F + name, size)

SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)
SERIF   = lambda s: font("DejaVuSerif.ttf", s)
SANS_B  = lambda s: font("DejaVuSans-Bold.ttf", s)
SANS    = lambda s: font("DejaVuSans.ttf", s)

# ---------------------------------------------------------------- text helpers
def wrap(text, fnt, width):
    words, lines, cur = text.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if fnt.getlength(t) <= width:
            cur = t
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

def text_block(d, x, y, lines, fnt, fill, leading):
    for ln in lines:
        d.text((x, y), ln, font=fnt, fill=fill)
        y += leading
    return y

def star(d, cx, cy, r, fill):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.42
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)

def jet(d, x, y, s, fill, flip=False):
    # simple top-view jet silhouette, pointing right (or left when flipped)
    pts = [(0, 0), (2.6 * s, 0.28 * s), (3.4 * s, 0.62 * s), (2.2 * s, 0.62 * s),
           (1.7 * s, 1.15 * s), (1.25 * s, 0.62 * s), (0.55 * s, 0.62 * s),
           (0.15 * s, 0.95 * s), (-0.05 * s, 0.55 * s), (-0.45 * s, 0.55 * s),
           (-0.45 * s, 0.28 * s), (0, 0)]
    if flip:
        pts = [(-px, py) for px, py in pts]
    d.polygon([(x + px, y + py) for px, py in pts], fill=fill)

def burst(d, cx, cy, r, fill):
    pts = []
    for i in range(16):
        ang = i * math.pi / 8
        rr = r if i % 2 == 0 else r * 0.55
        pts.append((cx + rr * math.cos(ang), cy + rr * math.sin(ang)))
    d.polygon(pts, fill=fill)

# ------------------------------------------------------------------- flags
def flag_us(d, x, y, w, h):
    for i in range(7):
        d.rectangle([x, y + i * h / 7, x + w, y + (i + 1) * h / 7],
                    fill=(178, 34, 52) if i % 2 == 0 else (255, 255, 255))
    d.rectangle([x, y, x + w * 0.42, y + h * 0.57], fill=(30, 58, 95))
    for r in range(3):
        for c in range(4):
            d.ellipse([x + 3 + c * w * 0.09, y + 2 + r * h * 0.17,
                       x + 6 + c * w * 0.09, y + 5 + r * h * 0.17], fill=(255, 255, 255))

def flag_cn(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 41, 16))
    star(d, x + w * 0.22, y + h * 0.30, h * 0.20, (255, 222, 0))
    for sx, sy in [(0.48, 0.16), (0.60, 0.28), (0.60, 0.46), (0.48, 0.56)]:
        star(d, x + w * sx, y + h * sy, h * 0.09, (255, 222, 0))

def flag_ru(d, x, y, w, h):
    for i, c in enumerate([(255, 255, 255), (0, 57, 166), (213, 0, 50)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)

def flag_in(d, x, y, w, h):
    for i, c in enumerate([(255, 153, 51), (255, 255, 255), (19, 136, 8)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
    d.ellipse([x + w / 2 - h * 0.14, y + h / 2 - h * 0.14,
               x + w / 2 + h * 0.14, y + h / 2 + h * 0.14],
              outline=(0, 0, 128), width=1)

def flag_jp(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.ellipse([x + w / 2 - h * 0.30, y + h * 0.20, x + w / 2 + h * 0.30, y + h * 0.80],
              fill=(188, 0, 45))

def flag_au(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(0, 40, 104))
    d.rectangle([x, y, x + w * 0.45, y + h * 0.5], fill=(200, 16, 46))
    d.line([x, y, x + w * 0.45, y + h * 0.5], fill=(255, 255, 255), width=2)
    d.line([x + w * 0.45, y, x, y + h * 0.5], fill=(255, 255, 255), width=2)
    for sx, sy in [(0.72, 0.25), (0.85, 0.45), (0.68, 0.70), (0.88, 0.78)]:
        star(d, x + w * sx, y + h * sy, h * 0.09, (255, 255, 255))

def flag_mx(d, x, y, w, h):
    for i, c in enumerate([(0, 104, 71), (255, 255, 255), (206, 17, 38)]):
        d.rectangle([x + i * w / 3, y, x + (i + 1) * w / 3, y + h], fill=c)
    d.ellipse([x + w / 2 - 2, y + h / 2 - 2, x + w / 2 + 2, y + h / 2 + 2],
              fill=(120, 70, 20))

def flag_bo(d, x, y, w, h):
    for i, c in enumerate([(213, 0, 50), (247, 220, 0), (0, 122, 61)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)

def flag_mn(d, x, y, w, h):
    for i, c in enumerate([(205, 0, 30), (0, 80, 160), (205, 0, 30)]):
        d.rectangle([x + i * w / 3, y, x + (i + 1) * w / 3, y + h], fill=c)
    d.rectangle([x + w * 0.08, y + h * 0.18, x + w * 0.20, y + h * 0.82], fill=(255, 215, 0))

def flag_rs(d, x, y, w, h):
    for i, c in enumerate([(198, 12, 48), (12, 64, 118), (255, 255, 255)]):
        d.rectangle([x, y + i * h / 3, x + w, y + (i + 1) * h / 3], fill=c)
    d.ellipse([x + w * 0.10, y + h * 0.30, x + w * 0.22, y + h * 0.70], fill=(255, 215, 0))

# ------------------------------------------------------- illustration panels
def panel_hormuz(d, x, y, w, h):
    """Strait of Hormuz: sea between Iran (top) and Oman (bottom), tanker ablaze."""
    d.rectangle([x, y, x + w, y + h], fill=(168, 196, 206))
    d.polygon([(x, y), (x + w, y), (x + w, y + h * 0.30), (x + w * 0.62, y + h * 0.22),
               (x + w * 0.30, y + h * 0.30), (x, y + h * 0.24)], fill=(227, 211, 168))
    d.polygon([(x, y + h), (x + w, y + h), (x + w, y + h * 0.82), (x + w * 0.55, y + h * 0.74),
               (x + w * 0.25, y + h * 0.84), (x, y + h * 0.78)], fill=(227, 211, 168))
    d.text((x + 8, y + 6), "IRAN", font=SANS_B(10), fill=(90, 70, 40))
    d.text((x + w - 52, y + h - 18), "OMAN", font=SANS_B(10), fill=(90, 70, 40))
    # tanker: long dark hull, white bridge, red funnel, flame on the deck
    tx, ty = x + w * 0.30, y + h * 0.56
    d.rectangle([tx, ty, tx + w * 0.52, ty + 13], fill=(40, 44, 48))
    d.rectangle([tx, ty + 13, tx + w * 0.52, ty + 16], fill=(20, 22, 24))
    d.rectangle([tx + w * 0.40, ty - 10, tx + w * 0.47, ty], fill=(240, 240, 235))
    d.rectangle([tx + w * 0.06, ty - 7, tx + w * 0.11, ty], fill=(178, 56, 40))
    # flame + smoke rising from the deck
    fx = tx + w * 0.24
    burst(d, fx, ty - 9, 12, (230, 120, 20))
    burst(d, fx, ty - 9, 6, (245, 200, 40))
    for cx, cy, r in [(fx - 4, ty - 28, 7), (fx + 5, ty - 38, 9), (fx - 2, ty - 48, 6)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(120, 120, 118))
    # strike dashes from Qeshm + tag
    d.line([x + w * 0.80, y + h * 0.20, fx + 8, ty - 16], fill=RED, width=2)
    for k in range(4):
        t = k / 3
        px = x + w * 0.80 + (fx + 8 - x - w * 0.80) * t
        py = y + h * 0.20 + (ty - 16 - y - h * 0.20) * t
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=RED)
    d.text((x + w * 0.76, y + 4), "QESHM", font=SANS_B(9), fill=RED)
    jet(d, x + w * 0.08, y + h * 0.34, 9, (40, 44, 48))
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(20, 40, 44))
    d.text((x + 8, y + h - 14), "STRAIT OF HORMUZ", font=SANS_B(9), fill=(255, 255, 255))

def panel_crimea(d, x, y, w, h):
    """Kerch Strait bridge: road arch collapsed into the water, smoke, jets."""
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.rectangle([x, y + h * 0.58, x + w, y + h], fill=(143, 180, 196))
    for i in range(4):
        d.line([x, y + h * 0.62 + i * 7, x + w, y + h * 0.62 + i * 7],
               fill=(120, 160, 178), width=1)
    # bridge deck left (intact) and right (standing), middle span down;
    # arches rise from the deck itself
    d.rectangle([x, y + h * 0.44, x + w * 0.42, y + h * 0.52], fill=(70, 74, 78))
    d.rectangle([x + w * 0.68, y + h * 0.44, x + w, y + h * 0.52], fill=(70, 74, 78))
    d.arc([x + w * 0.04, y + h * 0.06, x + w * 0.42, y + h * 0.46], 180, 360, fill=(70, 74, 78), width=5)
    d.arc([x + w * 0.68, y + h * 0.06, x + w, y + h * 0.46], 180, 360, fill=(70, 74, 78), width=5)
    # collapsed span tilted into the water
    d.polygon([(x + w * 0.44, y + h * 0.54), (x + w * 0.60, y + h * 0.46),
               (x + w * 0.66, y + h * 0.54), (x + w * 0.52, y + h * 0.68)], fill=(52, 56, 60))
    burst(d, x + w * 0.55, y + h * 0.48, 13, (230, 120, 20))
    burst(d, x + w * 0.55, y + h * 0.48, 7, (245, 200, 40))
    for cx, cy, r in [(x + w * 0.50, y + h * 0.28, 9), (x + w * 0.60, y + h * 0.20, 11),
                      (x + w * 0.56, y + h * 0.12, 7)]:
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(110, 110, 108))
    jet(d, x + w * 0.06, y + h * 0.16, 8, (30, 32, 36))
    jet(d, x + w * 0.84, y + h * 0.08, 8, (30, 32, 36), flip=True)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(20, 40, 44))
    d.text((x + 8, y + h - 14), "KERCH STRAIT", font=SANS_B(9), fill=(255, 255, 255))

def panel_shenzhen(d, x, y, w, h):
    """Shenzhen: three flags over a round table, skyline behind."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 224, 200))
    for bx, bw, bh in [(0.02, 0.10, 0.42), (0.14, 0.08, 0.55), (0.24, 0.12, 0.38),
                       (0.78, 0.09, 0.50), (0.89, 0.08, 0.40)]:
        d.rectangle([x + w * bx, y + h - bh * h - 18, x + w * (bx + bw), y + h - 18],
                    fill=(180, 168, 138))
    # round table
    d.ellipse([x + w * 0.30, y + h - 34, x + w * 0.70, y + h - 6], fill=(120, 84, 50))
    d.rectangle([x + w * 0.30, y + h - 22, x + w * 0.70, y + h - 14], fill=(96, 64, 36))
    # three flag poles
    for i, fn in enumerate([flag_us, flag_cn, flag_ru]):
        fx = x + w * (0.34 + i * 0.16)
        d.line([fx + 14, y + 10, fx + 14, y + h - 30], fill=(90, 80, 60), width=2)
        fn(d, fx - 6, y + 10, 40, 24)
    d.rectangle([x, y + h - 16, x + w, y + h], fill=(20, 40, 44))
    d.text((x + 8, y + h - 14), "SHENZHEN · THU 19 NOV", font=SANS_B(9), fill=(255, 255, 255))

def panel_quad(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 232, 226))
    fw, fh, gap = 46, 26, 8
    total = 4 * fw + 3 * gap
    x0 = x + (w - total) / 2
    for i, fn in enumerate([flag_us, flag_in, flag_jp, flag_au]):
        fn(d, x0 + i * (fw + gap), y + 6, fw, fh)
    d.rectangle([x + 14, y + h - 12, x + w - 14, y + h - 6], fill=(120, 84, 50))
    d.text((x + 8, y + h - 16), "", font=SANS_B(9), fill=INK)

def panel_nvidia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(18, 38, 32))
    d.rectangle([x + 10, y + 12, x + 34, y + 36], fill=(30, 70, 55))
    d.rectangle([x + 15, y + 17, x + 29, y + 31], fill=(60, 200, 120))
    d.text((x + 18, y + 20), "AI", font=SANS_B(9), fill=(18, 38, 32))
    for i, bh in enumerate([8, 14, 11, 20, 26]):
        d.rectangle([x + 44 + i * 13, y + 40 - bh, x + 52 + i * 13, y + 40],
                    fill=(60, 200, 120))
    d.line([x + 44, y + 46, x + w - 40, y + 14], fill=(230, 80, 60), width=3)
    d.polygon([(x + w - 40, y + 14), (x + w - 52, y + 16), (x + w - 42, y + 26)],
              fill=(230, 80, 60))
    d.text((x + w - 76, y + h - 15), "DOW −849", font=SANS_B(11), fill=(255, 120, 100))

def panel_measles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(240, 228, 214))
    # spiky virus
    cx, cy = x + 30, y + h / 2
    for k in range(8):
        ang = k * math.pi / 4
        d.line([cx + 10 * math.cos(ang), cy + 10 * math.sin(ang),
                cx + 17 * math.cos(ang), cy + 17 * math.sin(ang)], fill=RED, width=2)
    d.ellipse([cx - 11, cy - 11, cx + 11, cy + 11], fill=RED)
    d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=(240, 228, 214))
    fw, fh = 44, 24
    for i, fn in enumerate([flag_us, flag_mx, flag_bo]):
        fn(d, x + 58 + i * (fw + 8), y + 8, fw, fh)
    d.text((x + 58, y + h - 18), "STATUS LOST", font=SANS_B(10), fill=RED)

def panel_cop31(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(222, 232, 226))
    # globe
    cx, cy, r = x + 34, y + h / 2 + 2, 20
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(90, 150, 190))
    d.ellipse([cx - r + 6, cy - r + 4, cx - 2, cy - 2], fill=(90, 170, 110))
    d.ellipse([cx + 2, cy + 2, cx + r - 4, cy + r - 6], fill=(90, 170, 110))
    # draft document
    d.rectangle([x + 66, y + 6, x + w - 60, y + h - 8], fill=(255, 255, 255),
                outline=(150, 150, 140))
    for i in range(4):
        d.line([x + 74, y + 14 + i * 8, x + w - 68, y + 14 + i * 8], fill=(160, 160, 150), width=2)
    d.text((x + 74, y + 42), "DRAFT", font=SANS_B(8), fill=RED)
    # flame
    burst(d, x + w - 34, y + h / 2, 12, (230, 120, 20))
    burst(d, x + w - 34, y + h / 2, 6, (245, 200, 40))

def panel_ebola(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(242, 228, 222))
    cx, cy = x + 36, y + h / 2
    for k in range(10):
        ang = k * math.pi / 5
        d.line([cx + 11 * math.cos(ang), cy + 11 * math.sin(ang),
                cx + 18 * math.cos(ang), cy + 18 * math.sin(ang)], fill=RED, width=2)
    d.ellipse([cx - 12, cy - 12, cx + 12, cy + 12], fill=RED)
    for sx, sy in [(-4, -3), (4, 2), (0, 5)]:
        d.ellipse([cx + sx - 2, cy + sy - 2, cx + sx + 2, cy + sy + 2], fill=(242, 228, 222))
    # clinic tent
    d.polygon([(x + 74, y + h - 8), (x + 74, y + 16), (x + 106, y + 6),
               (x + 138, y + 16), (x + 138, y + h - 8)], fill=(255, 255, 255),
              outline=(120, 120, 110))
    d.rectangle([x + 100, y + 18, x + 112, y + 30], fill=RED)
    d.rectangle([x + 104, y + 14, x + 108, y + 34], fill=RED)
    d.text((x + 150, y + 10), "11,000+", font=SANS_B(13), fill=RED)
    d.text((x + 150, y + 28), "CASES", font=SANS_B(10), fill=INK)

def panel_japan(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SKY)
    d.ellipse([x + w - 52, y + 6, x + w - 16, y + 42], fill=(188, 0, 45))
    jet(d, x + 14, y + 12, 8, (70, 74, 78))
    jet(d, x + 60, y + 26, 8, (70, 74, 78))
    jet(d, x + 118, y + 10, 9, (178, 40, 30))
    d.line([x + 14, y + 44, x + w - 14, y + 44], fill=(255, 255, 255), width=2)
    d.text((x + 10, y + h - 16), "FIRST BREACH SINCE 2024", font=SANS_B(8), fill=(90, 60, 50))

def panel_mongolia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(232, 226, 210))
    # parliament building
    d.rectangle([x + 12, y + 18, x + 86, y + h - 6], fill=(200, 188, 160))
    d.polygon([(x + 8, y + 18), (x + 49, y + 4), (x + 90, y + 18)], fill=(150, 130, 100))
    for i in range(4):
        d.rectangle([x + 20 + i * 16, y + 24, x + 26 + i * 16, y + h - 6], fill=(247, 242, 230))
    # resignation letter + arrow out the door
    d.rectangle([x + 106, y + 10, x + 158, y + h - 14], fill=(255, 255, 255),
                outline=(150, 150, 140))
    for i in range(3):
        d.line([x + 112, y + 18 + i * 7, x + 152, y + 18 + i * 7], fill=(160, 160, 150), width=2)
    d.text((x + 112, y + 38), "RESIGN", font=SANS_B(8), fill=RED)
    d.line([x + 172, y + h / 2, x + 200, y + h / 2], fill=TEAL, width=3)
    d.polygon([(x + 200, y + h / 2), (x + 190, y + h / 2 - 5), (x + 190, y + h / 2 + 5)],
              fill=TEAL)

def panel_serbia(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(228, 230, 232))
    # parliament dome
    d.rectangle([x + 12, y + 26, x + 92, y + h - 6], fill=(190, 190, 185))
    d.pieslice([x + 26, y + 2, x + 78, y + 34], 180, 360, fill=(140, 140, 135))
    for i in range(4):
        d.rectangle([x + 20 + i * 16, y + 32, x + 26 + i * 16, y + h - 6], fill=(247, 242, 230))
    # crowd dots
    for i in range(9):
        cx = x + 112 + (i % 3) * 14
        cy = y + 14 + (i // 3) * 13
        d.ellipse([cx - 4, cy - 4, cx + 4, cy + 4], fill=TEAL if i % 2 else AMBER)
    # ballot box
    d.rectangle([x + 158, y + 22, x + 196, y + h - 8], fill=(255, 255, 255),
                outline=(120, 120, 110))
    d.rectangle([x + 168, y + 14, x + 186, y + 22], fill=(255, 255, 255),
                outline=(120, 120, 110))
    d.text((x + 162, y + 30), "140", font=SANS_B(12), fill=TEAL)

# ---------------------------------------------------------------- world map
NA = [(-168, 66), (-158, 58), (-140, 60), (-130, 54), (-125, 49), (-124, 42),
      (-120, 34), (-114, 29), (-110, 24), (-105, 20), (-97, 16), (-94, 17),
      (-87, 13), (-83, 9), (-79, 9), (-77, 7), (-80, 8), (-83, 11), (-86, 15),
      (-90, 14), (-92, 15), (-97, 16), (-97, 26), (-93, 30), (-89, 30),
      (-84, 30), (-81, 25), (-80, 32), (-76, 35), (-74, 40), (-70, 42),
      (-68, 45), (-65, 44), (-60, 47), (-55, 52), (-60, 55), (-65, 58),
      (-68, 58), (-78, 62), (-85, 66), (-92, 66), (-95, 69), (-110, 68),
      (-125, 70), (-140, 70), (-155, 71), (-165, 68)]
SA = [(-79, 9), (-77, 4), (-80, -3), (-81, -6), (-77, -12), (-72, -18),
      (-70, -23), (-70, -30), (-72, -37), (-73, -44), (-74, -50), (-70, -54),
      (-66, -55), (-68, -50), (-65, -45), (-62, -41), (-58, -35), (-52, -32),
      (-48, -28), (-41, -23), (-39, -17), (-35, -9), (-35, -6), (-40, -3),
      (-44, -2), (-50, 0), (-53, 4), (-58, 6), (-62, 9), (-68, 11), (-72, 12),
      (-76, 10)]
AF = [(-17, 15), (-17, 21), (-15, 27), (-10, 31), (-5, 35), (0, 36), (10, 37),
      (11, 34), (20, 32), (30, 31), (32, 31), (34, 28), (35, 23), (37, 18),
      (39, 15), (41, 11), (44, 11), (48, 11), (51, 12), (51, 10), (48, 5),
      (46, 2), (42, -1), (40, -4), (40, -10), (39, -15), (36, -20), (33, -26),
      (32, -29), (28, -33), (26, -34), (20, -35), (17, -32), (15, -27),
      (12, -18), (12, -12), (13, -6), (12, -4), (9, 0), (9, 4), (4, 6),
      (-2, 5), (-8, 5), (-13, 8), (-17, 12)]
EU_ASIA = [(-10, 37), (-9, 43), (-2, 44), (-1, 46), (-4, 48), (0, 50), (3, 53),
           (8, 55), (8, 58), (12, 60), (18, 66), (25, 71), (32, 70), (40, 68),
           (50, 69), (60, 69), (70, 72), (80, 73), (95, 76), (110, 74),
           (125, 72), (140, 72), (155, 70), (170, 67), (178, 65), (170, 60),
           (162, 58), (158, 52), (156, 50), (150, 59), (142, 54), (141, 48),
           (140, 42), (135, 43), (130, 42), (127, 40), (126, 35), (122, 38),
           (120, 32), (121, 28), (118, 24), (110, 21), (108, 18), (105, 9),
           (103, 7), (100, 6), (98, 10), (95, 15), (92, 21), (89, 22),
           (86, 20), (82, 17), (80, 13), (77, 8), (75, 12), (73, 16),
           (70, 20), (66, 25), (62, 25), (58, 25), (57, 27), (54, 26),
           (52, 26), (50, 26), (48, 29), (44, 29), (42, 27), (40, 24),
           (38, 22), (36, 20), (35, 17), (33, 14), (35, 12), (39, 15),
           (43, 12), (43, 15), (40, 20), (38, 24), (36, 28), (35, 32),
           (33, 36), (30, 36), (27, 37), (23, 36), (22, 37), (19, 40),
           (16, 38), (15, 40), (12, 42), (10, 44), (8, 44), (3, 43),
           (0, 40), (-2, 37), (-6, 36), (-9, 37)]
ARABIA = [(43, 12), (45, 15), (48, 18), (52, 20), (55, 22), (57, 24), (55, 26),
          (52, 27), (50, 28), (48, 29), (45, 28), (42, 26), (40, 22), (38, 18),
          (36, 15), (34, 13), (36, 12), (40, 12)]
AU = [(114, -22), (114, -30), (115, -35), (118, -35), (124, -33), (129, -32),
      (132, -32), (135, -35), (138, -35), (140, -38), (145, -38), (150, -37),
      (153, -32), (153, -27), (150, -23), (146, -19), (142, -15), (142, -11),
      (140, -18), (136, -15), (135, -12), (132, -11), (130, -13), (126, -14),
      (122, -17), (118, -20)]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (-2, 51)]
JP = [(130, 31), (132, 33), (134, 34), (136, 35), (138, 35), (140, 37),
      (141, 39), (141, 41), (140, 42), (142, 44), (144, 44), (142, 42),
      (140, 40), (139, 38), (137, 37), (135, 34), (133, 34), (131, 32)]

def draw_map(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=SEA)
    lon0, lon1, lat0, lat1 = -170, 190, -58, 84
    def P(lon, lat):
        return (x + (lon - lon0) / (lon1 - lon0) * w,
                y + (lat1 - lat) / (lat1 - lat0) * h)
    for poly in (NA, SA, AF, EU_ASIA, ARABIA, AU, UK, JP):
        d.polygon([P(lo, la) for lo, la in poly], fill=(228, 210, 175))
    # graticule, kept faint so it does not chop the map up
    for lon in range(-150, 181, 30):
        px = x + (lon - lon0) / (lon1 - lon0) * w
        d.line([px, y, px, y + h], fill=(216, 229, 225), width=1)
    for lat in range(-40, 81, 20):
        py = y + (lat1 - lat) / (lat1 - lat0) * h
        d.line([x, py, x + w, py], fill=(216, 229, 225), width=1)
    # numbered pins for stories 1-11; crowded clusters get offset circles
    # with a leader line back to the true spot
    pins = {1: (56, 26.5), 2: (34, 45.3), 3: (114, 22.5), 4: (121, 14.6),
            5: (-122, 37.4), 6: (-77, 39), 7: (30.7, 36.9), 8: (25, -2),
            9: (130.5, 34), 10: (106.9, 47.9), 11: (20.5, 44.8)}
    offs = {2: (17, -9), 7: (-2, 15), 11: (-17, -10), 3: (-13, -9), 4: (11, 11)}
    for n, (lo, la) in pins.items():
        px, py = P(lo, la)
        dx, dy = offs.get(n, (0, 0))
        if (dx, dy) != (0, 0):
            d.line([px, py, px + dx, py + dy], fill=TEAL, width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=TEAL)
            px, py = px + dx, py + dy
        d.ellipse([px - 9, py - 9, px + 9, py + 9], fill=TEAL, outline=(255, 255, 255), width=1)
        f = SANS_B(9)
        tw = f.getlength(str(n))
        d.text((px - tw / 2, py - 6.5), str(n), font=f, fill=(255, 255, 255))
    # dots for briefs 12-40
    dots = [(87, 55), (-122, 37.4), (30.5, 50.5), (37.6, 55.8), (28.8, 47),
            (2.3, 48.9), (21, 52.2), (14.4, 50.1), (35.2, 31.8), (28.9, 41),
            (30.1, -1.9), (0, 51.5), (8.7, 50.1), (-74, 40.7), (80, 16),
            (-160, -21), (32.5, 15.6), (36.8, -1.3), (12.5, 41.9), (12.6, 55.7),
            (103.8, 1.35), (1.2, 6.1), (130.8, -12.5), (-77, 38.9), (127, 37.5),
            (121, 23.5), (90.4, 23.8), (32.6, -25.9)]
    for lo, la in dots:
        px, py = P(lo, la)
        d.ellipse([px - 2.5, py - 2.5, px + 2.5, py + 2.5], fill=AMBER,
                  outline=(255, 255, 255), width=1)
    return P

# ------------------------------------------------------------------ content
LEADS = [
    ("1 · GULF — WAR", "Tankers burn as US jets strike Iran",
     "US jets hit an IRGC missile site on Qeshm after drones aimed at a US "
     "radar in Bahrain were shot down. Iran says tankers hit mines — unverified.",
     panel_hormuz),
    ("2 · EUROPE — WAR", "Crimean Bridge falls for a second day",
     "Ukraine's strike drops the road arch into the Kerch Strait; rail traffic "
     "resumes on one track. Russia hits Kyiv's Dnipro bridges in reply.",
     panel_crimea),
    ("3 · ASIA — DIPLOMACY", "Trump, Xi and Putin to meet on Thursday",
     "The first-ever trilateral of the three leaders is set for 19 November "
     "in Shenzhen, on the APEC sidelines. Nuclear arms top the agenda.",
     panel_shenzhen),
]

GRID = [
    ("4 · ASIA — DIPLOMACY", "Quad leaders meet in Manila",
     "Trump, Modi, Takaichi and Albanese strike critical-minerals deals.",
     panel_quad),
    ("5 · US — MARKETS", "Nvidia posts a $115.8bn quarter",
     "Sales double; the Dow falls 849 points, its fourth straight drop.",
     panel_nvidia),
    ("6 · AMERICAS — HEALTH", "US loses measles-free status",
     "PAHO ends the status held since 2000; Mexico and Bolivia lose it too.",
     panel_measles),
    ("7 · WORLD — CLIMATE", "COP31 draft splits over fossil fuels",
     "Ministers take over in Antalya; the draft urges a faster phase-out.",
     panel_cop31),
    ("8 · AFRICA — HEALTH", "Ebola cases pass 11,000 in DR Congo",
     "WHO: the toll has more than doubled in three months; children hit hardest.",
     panel_ebola),
    ("9 · ASIA — DEFENCE", "Japan scrambles jets at Russian planes",
     "Two suspected Russian planes enter airspace off Fukuoka; Tokyo protests.",
     panel_japan),
    ("10 · ASIA — POLITICS", "Mongolia's president says he will resign",
     "Khurelsukh denies a $25m bribe claim; parliament must accept his exit.",
     panel_mongolia),
    ("11 · EUROPE — POLITICS", "Serbia's students take their seats",
     "The Student List's 140 MPs are sworn in, ending 14 years of SNS rule.",
     panel_serbia),
]

BRIEFS = [
    "An-12 crash in Siberia kills all 19",
    "Apple outage: a bad update, not a hack",
    "Kyiv's Dnipro bridges hit by missiles",
    "Russia claims 1,441 drones downed",
    "Moldova shuts airspace over 7 drones",
    "France: 146,000 march in pay strike",
    "Tusk survives no-confidence vote",
    "Prague: two trains collide, 46 hurt",
    "Kahana elected Knesset speaker, 66–52",
    "Turkey seizes opposition channel Sözcü TV",
    "Five EU states plan Rwanda asylum hub",
    "UK sanctions 8 settlement firms",
    "Deutsche Bank falls 6% on leaked files",
    "JPMorgan outage cuts off Zelle users",
    "Cyclone Akvan nears Andhra Pradesh",
    "Cyclone Xavier, Cat 4, nears Cook Is.",
    "UN: 2,230 civilian deaths in Sudan",
    "WFP feeds 30,000 fleeing Ethiopia clashes",
    "Pope Leo XIV back from South America",
    "Voyager 1 nears one light-day out",
    "Norway 3–2 Denmark; Haaland scores twice",
    "Brazil 7–0 Singapore; Vinícius treble",
    "Togo 3–0 Algeria in AFCON qualifier",
    "M6.6 Banda Sea quake shakes Darwin",
    "NSA network down; DNI denies cyberattack",
    "South Korea scrambles jets over Russians",
    "Taiwan spots two Russian planes offshore",
    "Dhaka police tear-gas garment workers",
    "Mozambique: Mondlane on trial, 5 charges",
]

# ------------------------------------------------------------------ compose
def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    # ---- masthead: own nameplate, teal + sand (not the tops' red/navy) ----
    d.text((M, 12), "ONE DAY ON EARTH", font=SANS_B(16), fill=TEAL)
    right = "40 STORIES · 6 CONTINENTS · ONE DAY"
    d.text((W - M - SANS_B(11).getlength(right), 16), right, font=SANS_B(11),
           fill=(150, 96, 20))
    d.text((M, 34), "Tuesday 17 November 2026", font=SERIF_B(52), fill=INK)
    d.rectangle([M, 96, W - M, 99], fill=TEAL)
    d.rectangle([M, 102, W - M, 103], fill=BORDER)
    d.text((M, 108),
           "The whole world's news on one page — every story here happened or was "
           "first reported on this day.",
           font=SANS(11), fill=GREY)

    # ---- three leads ----
    lx = [M, 356, 686]
    for i, (kick, head, deck, fn) in enumerate(LEADS):
        x = lx[i]
        fn(d, x, 126, 306, 116)
        d.text((x, 250), kick, font=SANS_B(10), fill=TEAL)
        hl = wrap(head, SERIF_B(19), 306)
        y = text_block(d, x, 268, hl, SERIF_B(19), INK, 23)
        dl = wrap(deck, SANS(11), 306)
        text_block(d, x, y + 6, dl, SANS(11), (60, 60, 55), 14.5)

    # ---- stat strip ----
    d.rectangle([M, 382, W - M, 412], fill=TEAL)
    stats = ("40 STORIES    ·    6 CONTINENTS    ·    13 FIELDS    ·    "
             "$115.8BN NVIDIA QUARTER    ·    1,441 DRONES DOWNED, RUSSIA SAYS")
    f = SANS_B(12)
    d.text(((W - f.getlength(stats)) / 2, 391), stats, font=f, fill=(255, 255, 255))

    # ---- grid of eight ----
    gx = [M, 268, 510, 752]
    gy = [422, 556]
    for i, (kick, head, deck, fn) in enumerate(GRID):
        x, y = gx[i % 4], gy[i // 4]
        fn(d, x, y, 234, 52)
        d.text((x, y + 58), kick, font=SANS_B(9), fill=TEAL)
        hl = wrap(head, SERIF_B(13), 234)
        yy = text_block(d, x, y + 71, hl, SERIF_B(13), INK, 16)
        dl = wrap(deck, SANS(10), 234)
        text_block(d, x, yy + 3, dl, SANS(10), (60, 60, 55), 12.5)

    # ---- bottom: map + briefs ----
    d.rectangle([M, 692, W - M, 693], fill=BORDER)
    d.text((M, 700), "WHERE IT HAPPENED", font=SANS_B(12), fill=TEAL)
    draw_map(d, M, 722, 470, 240)
    d.ellipse([M, 970, M + 8, 978], fill=TEAL)
    d.text((M + 12, 966), "1–11  stories above", font=SANS(9), fill=GREY)
    d.ellipse([M + 138, 970, M + 146, 978], fill=AMBER)
    d.text((M + 150, 966), "briefs 12–40", font=SANS(9), fill=GREY)

    d.line([504, 700, 504, 986], fill=BORDER, width=1)
    d.text((512, 700), "ALSO ON TUESDAY 17 NOVEMBER", font=SANS_B(12), fill=TEAL)
    bx = [512, 758]
    for i, b in enumerate(BRIEFS):
        col, row = i // 15, i % 15
        x = bx[col]
        y = 722 + row * 17.5
        num = str(12 + i)
        d.text((x, y), num, font=SANS_B(10), fill=TEAL)
        d.text((x + 24, y), b, font=SANS(10), fill=INK)

    # ---- footer ----
    d.rectangle([M, 992, W - M, 993], fill=BORDER)
    d.text((M, 998),
           "Every story on this page happened or was first reported on Tuesday "
           "17 November 2026. Claims are labelled as claims.",
           font=SANS(9), fill=GREY)
    d.text((M, 1010),
           "Sources: Reuters, AP, AFP, BBC, Al Jazeera, UN News, WHO, PAHO. "
           "All drawings original.",
           font=SANS(9), fill=GREY)

    img.save("entry.png", optimize=True)
    print("saved entry.png")

if __name__ == "__main__":
    main()
