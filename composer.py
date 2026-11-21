"""The World Herald -- composer for news-image-20261121.

Builds a 1024x1024 classic-newspaper front page summing up the world news
of Saturday 21 November 2026. All drawing is done with Pillow; the module
is deterministic: no network, no clock, no randomness. If a required font
or photo is missing, compose() raises, so the caller can fall back to the
prebuilt image instead of producing different bytes.

Layout: masthead, two photorealistic hero panels, six featured stories
with real photographs, three more featured stories with drawn icons, a
schematic world map with ten numbered places, twenty numbered briefs and
a one-line footer. Stories are numbered 1-31 in reading order and the map
dots use the same numbers, so a reader can find any story on the map.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
PAPER = (247, 241, 222)
INK = (27, 42, 74)
RED = (164, 30, 34)
GOLD = (166, 124, 0)
TAN = (233, 221, 193)
TAN_LINE = (203, 191, 164)
GREY = (96, 91, 80)

SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def _font(path, size):
    if not os.path.exists(path):
        raise FileNotFoundError("missing font: " + path)
    return ImageFont.truetype(path, size)


def _wrap(draw, text, font, max_width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        trial = current + " " + word if current else word
        if draw.textlength(trial, font=font) <= max_width:
            current = trial
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def _fit_one_line(draw, text, font, max_width):
    """Truncate a single line with an ellipsis so it never overflows."""
    if draw.textlength(text, font=font) <= max_width:
        return text
    while text and draw.textlength(text + "\u2026", font=font) > max_width:
        text = text[:-1]
    return text + "\u2026"


def _crop_to(img, tw, th, fy=0.5):
    """Centre-crop to the target aspect, then resize. fy moves the crop
    window vertically (0.0 = top, 1.0 = bottom) for tall source images."""
    sw, sh = img.size
    target = tw / th
    src = sw / sh
    if src > target:
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        box = (x0, 0, x0 + nw, sh)
    else:
        nh = int(sw / target)
        y0 = int((sh - nh) * fy)
        y0 = max(0, min(y0, sh - nh))
        box = (0, y0, sw, y0 + nh)
    return img.crop(box).resize((tw, th), Image.LANCZOS)


# ---------------------------------------------------------------- icons

def _icon_scales(d, x, y):
    d.line([(x + 2, y + 8), (x + 24, y + 8)], fill=INK, width=2)
    d.line([(x + 13, y + 2), (x + 13, y + 22)], fill=INK, width=2)
    d.ellipse([x + 1, y + 15, x + 12, y + 21], outline=INK, width=2)
    d.ellipse([x + 14, y + 15, x + 25, y + 21], outline=INK, width=2)
    d.line([(x + 2, y + 8), (x + 6, y + 16)], fill=INK, width=1)
    d.line([(x + 12, y + 8), (x + 8, y + 16)], fill=INK, width=1)
    d.line([(x + 14, y + 8), (x + 19, y + 16)], fill=INK, width=1)
    d.line([(x + 24, y + 8), (x + 20, y + 16)], fill=INK, width=1)


def _icon_summit(d, x, y):
    for cx, col in ((x + 6, RED), (x + 13, INK), (x + 20, GOLD)):
        d.ellipse([cx - 4, y + 3, cx + 4, y + 11], fill=col)
        d.arc([cx - 6, y + 12, cx + 6, y + 24], 180, 360, fill=INK, width=2)


def _icon_cyclone(d, x, y):
    d.arc([x + 3, y + 3, x + 23, y + 23], 200, 20, fill=INK, width=2)
    d.arc([x + 7, y + 7, x + 19, y + 19], 20, 200, fill=RED, width=2)
    d.arc([x + 11, y + 11, x + 15, y + 15], 200, 20, fill=INK, width=2)


def _icon_flame(d, x, y):
    d.polygon([(x + 13, y + 1), (x + 20, y + 12), (x + 18, y + 21),
               (x + 8, y + 21), (x + 6, y + 12)], fill=RED)
    d.polygon([(x + 13, y + 10), (x + 17, y + 15), (x + 15, y + 20),
               (x + 11, y + 20), (x + 9, y + 15)], fill=GOLD)


def _icon_rings(d, x, y):
    d.ellipse([x + 2, y + 6, x + 14, y + 18], outline=INK, width=2)
    d.ellipse([x + 12, y + 6, x + 24, y + 18], outline=RED, width=2)


def _icon_shield(d, x, y):
    d.polygon([(x + 13, y + 2), (x + 23, y + 6), (x + 23, y + 14),
               (x + 13, y + 24), (x + 3, y + 14), (x + 3, y + 6)],
              outline=INK, width=2)
    d.line([(x + 8, y + 13), (x + 12, y + 17), (x + 19, y + 8)],
           fill=RED, width=2)


def _icon_capsule(d, x, y):
    d.rounded_rectangle([x + 2, y + 9, x + 24, y + 17], radius=4,
                        outline=INK, width=2)
    d.rectangle([x + 4, y + 11, x + 12, y + 15], fill=RED)
    d.line([(x + 13, y + 9), (x + 13, y + 17)], fill=INK, width=1)


def _icon_cross(d, x, y):
    d.rounded_rectangle([x + 2, y + 2, x + 24, y + 24], radius=4,
                        outline=INK, width=2)
    d.rectangle([x + 11, y + 6, x + 15, y + 20], fill=RED)
    d.rectangle([x + 6, y + 11, x + 20, y + 15], fill=RED)


def _icon_leaf(d, x, y):
    d.polygon([(x + 13, y + 2), (x + 23, y + 12), (x + 13, y + 24),
               (x + 3, y + 12)], outline=INK, width=2)
    d.line([(x + 13, y + 4), (x + 13, y + 22)], fill=GOLD, width=2)
    d.line([(x + 13, y + 22), (x + 17, y + 25)], fill=INK, width=2)


ICONS = {
    "scales": _icon_scales,
    "summit": _icon_summit,
    "cyclone": _icon_cyclone,
    "flame": _icon_flame,
    "rings": _icon_rings,
    "shield": _icon_shield,
    "capsule": _icon_capsule,
    "cross": _icon_cross,
    "leaf": _icon_leaf,
}

# ---------------------------------------------------------------- data

HEROES = [
    {
        "img": "hero_poland.png",
        "kicker": "1 \u2022 POLAND \u2014 NATO ON ALERT",
        "headline": "RUSSIAN MISSILES FALL ON POLAND",
        "deck": "Two missiles and a jet drone fall in the south-east amid a "
                "400-drone barrage on Ukraine. Tusk: \u2018intentional "
                "provocation\u2019. Rutte: \u2018grave violation\u2019.",
    },
    {
        "img": "hero_markets.png",
        "kicker": "2 \u2022 MARKETS \u2014 WALL STREET",
        "headline": "WALL STREET IN FREEFALL AS TECH CRASHES",
        "deck": "The S&P 500 sinks 3.7% in a seventh straight fall; the "
                "Nasdaq plunges 5.3% in its worst week since 2020. Nvidia "
                "falls 14% as its chief executive quits.",
    },
]

# Six featured stories with real photographs (number, image, focus,
# kicker, headline, one-line summary). Numbers match the map dots.
PHOTO_FEATURED = [
    ("feat_icj.png", 0.62, 3, "3 \u2022 THE HAGUE \u2014 JUSTICE",
     "Court: Myanmar committed genocide",
     "China calls the ruling \u2018unjust\u2019."),
    ("feat_summit.png", 0.5, 4, "4 \u2022 SHENZHEN \u2014 DIPLOMACY",
     "Trump, Xi and Putin agree to meet",
     "A three-way summit is set for Shenzhen."),
    ("feat_cyclone.png", 0.5, 5, "5 \u2022 ODISHA \u2014 DISASTER",
     "Cyclone Akvan kills 18 in Odisha",
     "Over 11 lakh people were evacuated."),
    ("feat_iran.png", 0.5, 6, "6 \u2022 TEHRAN \u2014 WAR",
     "US strikes on Iran cost $48.3bn",
     "The campaign\u2019s price tag is revealed."),
    ("feat_ukeu.png", 0.5, 7, "7 \u2022 BRUSSELS \u2014 DIPLOMACY",
     "UK and EU agree a new post-Brexit deal",
     "A summit in Burnham seals the pact."),
    ("feat_saudi.png", 0.5, 8, "8 \u2022 RIYADH \u2014 SECURITY",
     "Saudi forces down three Houthi missiles",
     "Debris falls on the city; none hurt."),
]

# Three more featured stories, drawn icons (icon, number, kicker,
# headline, one-line summary).
ICON_FEATURED = [
    ("capsule", 9, "9 \u2022 HEALTH",
     "CANCER PILL BREAKTHROUGH",
     "A new pill shows promise against cancer."),
    ("leaf", 10, "10 \u2022 CLIMATE",
     "COP31 TALKS ENTER FINAL PHASE",
     "Climate summit races to a deal."),
    ("shield", 11, "11 \u2022 SECURITY",
     "ESTONIA SHUTS CROSSINGS TO RUSSIA",
     "The border move follows the strikes."),
]

# Twenty briefs, numbered 12-31 in reading order.
BRIEFS = [
    "India 159/1 in first Test in New Zealand",
    "Sensex up ~898; NSE passes Nasdaq",
    "JPMorgan, Visa, Mastercard hit by hack",
    "US jails Nikhil Gupta for ~20 years",
    "Pakistan suicide bomb kills 5, hurts 13",
    "UN warns global hunger is worsening",
    "Voyager 1 passes one-light-day mark",
    "Nepal PM visits India, 22\u201323 Nov",
    "Bolsonaro rushed to hospital",
    "Indonesia fire losses may hit $30bn",
    "Fiji declares disaster as drought bites",
    "Seoul court clears ex-PM Han Duck-soo",
    "Kushner: Russia open to Kyiv deal",
    "France seeks UN session on Poland",
    "UK sends 1,000 drones worth \u00a3260m",
    "EU to borrow \u20ac45bn for Ukraine",
    "Hyundai Elantra 2027 debuts in LA",
    "Carlsen quits a rapid game mid-event",
    "Hayabusa2 fails to land on asteroid",
    "GTA VI rollout continues apace",
]

# Rough continent outlines as (lon, lat) pairs, drawn schematically.
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 71), (-95, 80), (-75, 72), (-60, 60),
     (-55, 47), (-70, 42), (-75, 35), (-80, 25), (-90, 20), (-97, 16),
     (-105, 20), (-115, 28), (-125, 40), (-125, 49), (-140, 60), (-165, 60)],
    [(-80, 10), (-75, 5), (-60, 5), (-50, 0), (-35, -8), (-40, -20),
     (-48, -28), (-58, -35), (-65, -40), (-70, -50), (-73, -35), (-72, -20),
     (-77, -12), (-80, -5)],
    [(-17, 15), (-10, 30), (0, 36), (10, 37), (20, 32), (32, 31), (35, 28),
     (43, 12), (51, 11), (48, 0), (40, -10), (35, -20), (32, -28), (20, -35),
     (15, -27), (12, -18), (9, -1), (-8, 4), (-13, 8)],
    [(-10, 36), (-9, 43), (-2, 48), (0, 51), (5, 53), (8, 57), (10, 59),
     (18, 56), (21, 55), (24, 59), (28, 60), (30, 62), (25, 65), (20, 70),
     (15, 70), (10, 68), (5, 60), (0, 55), (-5, 50), (-10, 44), (-9, 38)],
    [(30, 62), (40, 68), (60, 70), (80, 73), (100, 77), (120, 73),
     (140, 72), (160, 70), (178, 65), (170, 60), (160, 55), (150, 45),
     (140, 40), (130, 35), (127, 38), (120, 30), (110, 20), (105, 10),
     (100, 8), (95, 15), (90, 22), (80, 15), (75, 8), (70, 20), (60, 25),
     (50, 28), (45, 30), (40, 36), (35, 36), (30, 42)],
    [(113, -22), (114, -30), (120, -34), (130, -32), (135, -35), (140, -38),
     (145, -38), (150, -37), (153, -32), (153, -27), (146, -19), (142, -11),
     (135, -12), (130, -13), (125, -14), (120, -20), (114, -22)],
]

# (lon, lat, number, dx, dy) -- the ten numbered places on the map.
# Numbers are the stories' numbers in reading order (1-2 heroes, 3-8
# photo featured, 20-21 briefs), so each dot finds its story.
MAP_POINTS = [
    (21.0, 52.2, 1, 0, 0),
    (-74.0, 40.7, 2, 0, 0),
    (4.3, 52.1, 3, -7, -7),
    (114.1, 22.5, 4, 0, 0),
    (85.5, 20.0, 5, 0, 0),
    (51.4, 35.7, 6, -8, -4),
    (4.35, 50.85, 7, 7, 6),
    (46.7, 24.6, 8, 8, 7),
    (-47.9, -15.8, 20, 0, 0),
    (106.8, -6.2, 21, 0, 0),
]


def _project(lon, lat, x0, y0, w, h):
    x = x0 + (lon + 168.0) / 358.0 * w
    y = y0 + (84.0 - lat) / 142.0 * h
    return x, y


def _draw_map(d, x0, y0, w, h):
    d.rectangle([x0, y0, x0 + w, y0 + h], outline=TAN_LINE, width=1)
    for lon in range(-150, 181, 30):
        gx, _ = _project(lon, 0, x0, y0, w, h)
        d.line([(gx, y0), (gx, y0 + h)], fill=TAN_LINE, width=1)
    for lat in range(-30, 81, 30):
        _, gy = _project(0, lat, x0, y0, w, h)
        d.line([(x0, gy), (x0 + w, gy)], fill=TAN_LINE, width=1)
    for poly in CONTINENTS:
        pts = [_project(lon, lat, x0, y0, w, h) for lon, lat in poly]
        d.polygon(pts, fill=TAN, outline=INK, width=2)
    num_font = _font(SANS_B, 9)
    for lon, lat, num, dx, dy in MAP_POINTS:
        cx, cy = _project(lon, lat, x0, y0, w, h)
        cx += dx
        cy += dy
        r = 7
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=RED,
                  outline=(255, 255, 255), width=1)
        label = str(num)
        tw = d.textlength(label, font=num_font)
        d.text((cx - tw / 2, cy - 5), label, font=num_font,
               fill=(255, 255, 255))


def _photo(d, img, x, y, w, h, path, fy=0.5):
    if not os.path.exists(path):
        raise FileNotFoundError("missing photo: " + path)
    photo = Image.open(path).convert("RGB")
    photo = _crop_to(photo, w, h, fy)
    img.paste(photo, (x, y))
    d.rectangle([x, y, x + w - 1, y + h - 1], outline=INK, width=1)


def compose(root):
    """Compose the 1024x1024 front page. root is the repository dir."""
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)

    serif_b56 = _font(SERIF_B, 56)
    serif_b25 = _font(SERIF_B, 25)
    serif_b17 = _font(SERIF_B, 17)
    serif_b16 = _font(SERIF_B, 16)
    serif_b15 = _font(SERIF_B, 15)
    serif_b14 = _font(SERIF_B, 14)
    sans = _font(SANS, 12)
    sans_b13 = _font(SANS_B, 13)
    sans14 = _font(SANS, 14)
    sans11 = _font(SANS, 11)
    sans_b105 = _font(SANS_B, 11)
    sans105 = _font(SANS, 11)
    sans_b10 = _font(SANS_B, 10)

    # ---- masthead (16-126)
    d.rectangle([MARGIN, 16, W - MARGIN, 19], fill=GOLD)
    title = "THE WORLD HERALD"
    tw = d.textlength(title, font=serif_b56)
    d.text(((W - tw) / 2, 22), title, font=serif_b56, fill=INK)
    d.line([(MARGIN, 86), (W - MARGIN, 86)], fill=INK, width=1)
    d.text((MARGIN, 94), "VOL. I \u2014 No. 325", font=sans, fill=GREY)
    date = "SATURDAY, 21 NOVEMBER 2026"
    tw = d.textlength(date, font=serif_b25)
    d.text(((W - tw) / 2, 92), date, font=serif_b25, fill=INK)
    right = "ONE DAY \u2022 ONE PAGE"
    tw = d.textlength(right, font=sans)
    d.text((W - MARGIN - tw, 94), right, font=sans, fill=GREY)
    d.rectangle([MARGIN, 122, W - MARGIN, 124], fill=INK)
    d.rectangle([MARGIN, 126, W - MARGIN, 127], fill=INK)

    # ---- hero panels (134-466)
    panel_w = 472
    img_h = 200
    panels = [(MARGIN, HEROES[0]), (524, HEROES[1])]
    for px, hero in panels:
        path = os.path.join(root, "assets", hero["img"])
        _photo(d, img, px, 134, panel_w, img_h, path)
        d.text((px, 342), hero["kicker"], font=sans_b13, fill=RED)
        lines = _wrap(d, hero["headline"], serif_b25, panel_w)[:2]
        y = 346
        for line in lines:
            d.text((px, y), line, font=serif_b25, fill=INK)
            y += 26
        deck_lines = _wrap(d, hero["deck"], sans14, panel_w)[:3]
        y = 402
        for line in deck_lines:
            d.text((px, y), line, font=sans14, fill=(43, 43, 43))
            y += 16
    d.line([(512, 134), (512, 450)], fill=TAN_LINE, width=1)

    # ---- featured header (466-482)
    d.rectangle([MARGIN, 458, W - MARGIN, 460], fill=INK)
    d.rectangle([MARGIN, 466, MARGIN + 10, 476], fill=RED)
    d.text((MARGIN + 16, 464), "MORE OF THE DAY", font=serif_b17, fill=INK)

    # ---- six photo featured (486-636, 636-786)
    col_x = [MARGIN, 356, 684]
    row_y = [486, 636]
    for i, (fname, fy, num, kicker, head, summ) in enumerate(PHOTO_FEATURED):
        cx = col_x[i % 3]
        cy = row_y[i // 3]
        path = os.path.join(root, "assets", fname)
        _photo(d, img, cx, cy, 300, 82, path, fy)
        d.text((cx, cy + 88), kicker, font=sans_b10, fill=RED)
        head_lines = _wrap(d, head, serif_b15, 300)[:2]
        y = cy + 104
        for line in head_lines:
            d.text((cx, y), line, font=serif_b15, fill=INK)
            y += 15
        summ = _fit_one_line(d, summ, sans11, 300)
        d.text((cx, cy + 136), summ, font=sans11, fill=GREY)

    # ---- three icon featured (790-852)
    for i, (icon, num, kicker, head, summ) in enumerate(ICON_FEATURED):
        cx = col_x[i]
        cy = 790
        d.ellipse([cx, cy + 8, cx + 40, cy + 48], fill=TAN)
        ICONS[icon](d, cx + 7, cy + 15)
        tx = cx + 48
        twd = 252
        d.text((tx, cy), kicker, font=sans_b10, fill=RED)
        head_lines = _wrap(d, head, serif_b14, twd)[:2]
        y = cy + 12
        for line in head_lines:
            d.text((tx, y), line, font=serif_b14, fill=INK)
            y += 14
        summ = _fit_one_line(d, summ, sans11, twd)
        d.text((tx, cy + 42), summ, font=sans11, fill=GREY)

    # ---- map + briefs (868-1000)
    d.rectangle([MARGIN, 860, W - MARGIN, 862], fill=INK)
    d.text((MARGIN, 868), "AROUND THE WORLD", font=serif_b16, fill=INK)
    d.text((508, 868), "ALSO ON SATURDAY \u2014 20 MORE STORIES",
           font=serif_b16, fill=INK)
    _draw_map(d, MARGIN, 888, 460, 112)
    brief_cols = [(508, BRIEFS[:10], 12), (758, BRIEFS[10:], 22)]
    for bx, items, first_num in brief_cols:
        y = 888
        for j, text in enumerate(items):
            n = first_num + j
            num_label = "%d." % n
            d.text((bx, y), num_label, font=sans_b105, fill=RED)
            nw = d.textlength(num_label + " ", font=sans105)
            shown = _fit_one_line(d, text, sans105, 238 - nw)
            d.text((bx + nw, y), shown, font=sans105, fill=(43, 43, 43))
            y += 11

    # ---- footer (1004-1019, one line)
    d.rectangle([MARGIN, 1004, W - MARGIN, 1006], fill=INK)
    foot = ("Sources: wire reports from 21 November 2026. "
            "Hero images are AI-generated illustrations. \u2014 "
            "THE WORLD HERALD \u2022 make.fun news-image-20261121")
    tw = d.textlength(foot, font=sans105)
    d.text(((W - tw) / 2, 1008), foot, font=sans105, fill=GREY)

    return img
