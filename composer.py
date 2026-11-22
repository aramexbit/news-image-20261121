"""The World Herald — front page for Saturday 21 November 2026.

Draws one 1024x1024 classic newspaper front page (35 stories) with
Pillow. Deterministic: fixed palette, fixed fonts, fixed assets, no
clock, no network, no randomness. The paper background is a real
newsprint photograph (assets/paper_bg.png) cover-cropped to the page,
so every run writes identical bytes.
"""

import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968

PAPER = (243, 234, 211)  # kept for the globe's meridians and land
NAVY = (22, 41, 77)
NAVY_SOFT = (31, 56, 100)
RED = (163, 22, 33)
RED_SOFT = (178, 34, 44)
GOLD = (176, 141, 62)
INK = (28, 26, 22)
MUTED = (90, 83, 72)
RULE = (138, 125, 95)
WHITE = (250, 247, 238)

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
SERIF = os.path.join(FONT_DIR, "DejaVuSerif.ttf")
SERIF_B = os.path.join(FONT_DIR, "DejaVuSerif-Bold.ttf")
SANS = os.path.join(FONT_DIR, "DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf")

_cache = {}


def font(path, size):
    key = (path, size)
    if key not in _cache:
        _cache[key] = ImageFont.truetype(path, size)
    return _cache[key]


def fit_font(draw, text, path, max_w, start, minimum=8):
    """Largest font size (<= start) that fits text inside max_w."""
    size = start
    while size > minimum:
        f = font(path, size)
        if draw.textlength(text, font=f) <= max_w:
            return f
        size -= 1
    return font(path, minimum)


def wrap(draw, text, f, max_w):
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = (cur + " " + word).strip()
        if draw.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_italic(canvas, xy, text, f, fill):
    """Draw serif text with a slight right lean (no italic face here)."""
    tmp = Image.new("RGBA", (1100, 64), (0, 0, 0, 0))
    d = ImageDraw.Draw(tmp)
    d.text((6, 2), text, font=f, fill=fill + (255,))
    w = int(d.textlength(text, font=f)) + 12
    tmp = tmp.crop((0, 0, w, 56))
    sheared = tmp.transform(
        (w + 14, 56), Image.AFFINE, (1, 0.18, 0, 0, 1, 0),
        resample=Image.BICUBIC,
    )
    canvas.paste(sheared, (int(xy[0]), int(xy[1])), sheared)


def cover(path, w, h, focus_y=0.5):
    """Center-crop an asset to w x h (focus_y shifts the crop band)."""
    im = Image.open(path).convert("RGB")
    sw, sh = im.size
    target = w / h
    src = sw / sh
    if src > target:
        nw = int(sh * target)
        x0 = (sw - nw) // 2
        box = (x0, 0, x0 + nw, sh)
    else:
        nh = int(sw / target)
        y0 = int((sh - nh) * focus_y)
        box = (0, y0, sw, y0 + nh)
    return im.crop(box).resize((w, h), Image.LANCZOS)


def draw_globe(d, cx, cy, r):
    d.ellipse([cx - r, cy - r, cx + r, cy + r],
              fill=NAVY, outline=GOLD, width=2)
    for k in (-0.55, 0.0, 0.55):
        x0 = cx + int(k * r)
        d.ellipse([x0 - int(r * 0.30), cy - r, x0 + int(r * 0.30), cy + r],
                  outline=PAPER, width=1)
    for k in (-0.5, 0.0, 0.5):
        y0 = cy + int(k * r)
        half = int((r * r - (int(k * r)) ** 2) ** 0.5)
        d.line([cx - half, y0, cx + half, y0], fill=PAPER, width=1)
    d.ellipse([cx - int(r * 0.72), cy - int(r * 0.78),
               cx - int(r * 0.12), cy - int(r * 0.18)], fill=PAPER)
    d.ellipse([cx + int(r * 0.08), cy + int(r * 0.08),
               cx + int(r * 0.62), cy + int(r * 0.68)], fill=PAPER)


# Simplified continents, drawn in a 300 x 132 box (rough but readable).
CONTINENTS = [
    [(8, 28), (30, 14), (62, 10), (88, 18), (96, 30), (78, 40),
     (70, 52), (58, 58), (44, 52), (30, 48), (14, 40)],
    [(78, 66), (96, 62), (108, 72), (104, 92), (92, 112), (82, 100),
     (74, 82)],
    [(140, 52), (166, 44), (192, 50), (200, 66), (192, 88),
     (174, 104), (158, 92), (146, 72)],
    [(148, 30), (168, 22), (188, 26), (184, 38), (168, 40), (152, 40)],
    [(206, 26), (240, 14), (282, 20), (292, 38), (272, 52), (250, 58),
     (232, 48), (214, 44), (206, 36)],
    [(248, 96), (276, 92), (288, 102), (272, 116), (252, 110)],
]

# Story number -> (x, y) inside the 300 x 132 map box.
MAP_DOTS = {
    1: (178, 28), 2: (52, 38), 3: (150, 22), 4: (258, 62),
    5: (238, 66), 6: (208, 48), 7: (146, 38), 8: (196, 64),
    11: (88, 88), 29: (262, 88),
}


def draw_world_map(canvas, x0, y0, w, h):
    """Numbered world map, clipped strictly inside its w x h box.

    Continents and red story dots are drawn on a separate layer the
    exact size of the box, then pasted with its own alpha mask, so no
    pixel can escape the box, cover the briefs, or cross a rule. No
    box outline and no grid lines: continents and dots sit directly
    on the paper texture.
    """
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    sx, sy = w / 300.0, h / 132.0
    for poly in CONTINENTS:
        pts = [(int(px * sx), int(py * sy)) for px, py in poly]
        d.polygon(pts, fill=(232, 218, 182, 255), outline=NAVY + (255,))
    nf = font(SANS_B, 8)
    for num, (mx, my) in sorted(MAP_DOTS.items()):
        cx, cy = int(mx * sx), int(my * sy)
        d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=RED + (255,),
                  outline=WHITE + (255,), width=1)
        label = str(num)
        tw = d.textlength(label, font=nf)
        th = d.textbbox((0, 0), label, font=nf)[3]
        d.text((cx - tw / 2, cy - th / 2 - 1), label, font=nf,
               fill=WHITE + (255,))
    canvas.paste(layer, (x0, y0), layer)


# ---------------------------------------------------------------- stories
# All facts verified from the morning brief of 21 November 2026.

FEATURED = [
    dict(num=3, kicker="3  •  THE HAGUE — JUSTICE", photo="feat_icj7.png",
         head="Court: Myanmar committed genocide",
         deck="The world court rules on the Rohingya case in a historic judgment."),
    dict(num=4, kicker="4  •  SHENZHEN — DIPLOMACY", photo="feat_summit7.png",
         head="Trump, Xi and Putin agree to meet",
         deck="A first three-way summit is set for Shenzhen. Zelenskyy calls it a 'failure'."),
    dict(num=5, kicker="5  •  ODISHA — DISASTER", photo="feat_akvan7.png",
         head="Cyclone Akvan makes landfall",
         deck="300,000 people are evacuated as the storm hits the Odisha coast."),
    dict(num=6, kicker="6  •  TEHRAN — WAR", photo="feat_iran7.png",
         head="Iran war nears its ninth month",
         deck="Trump is in no rush; a decision may come in 2027."),
    dict(num=7, kicker="7  •  BRUSSELS — DIPLOMACY", photo="feat_ukeu7.png",
         head="UK and EU agree a new post-Brexit deal",
         deck="Food trade, carbon markets and youth mobility sealed in Brussels."),
    dict(num=8, kicker="8  •  RIYADH — SECURITY", photo="feat_saudi7.png",
         head="Saudi forces down three Houthi missiles",
         deck="Debris falls on the city; none hurt. The coalition strikes Hodeidah."),
]

WIDE = [
    dict(num=9, kicker="9  •  TÜRKIYE — CLIMATE", photo="feat_cop317.png",
         head="COP31 talks enter final phase",
         deck="Negotiators race to a deal as the summit in Türkiye reaches its endgame."),
    dict(num=10, kicker="10  •  HEALTH", photo="feat_cancer7.png",
         head="Cancer pill breakthrough",
         deck="A new pill shows promise against pancreatic cancer."),
]

BRIEFS = [
    (11, "Bolsonaro rushed to hospital"),
    (12, "Estonia shuts crossings to Russia"),
    (13, "France seeks UN session on Poland"),
    (14, "UK sends 1,000 drones to Kyiv"),
    (15, "EU borrows €45bn for Ukraine"),
    (16, "Nvidia falls 14% as chief quits"),
    (17, "Anthropic down 9% after $83bn IPO"),
    (18, "India 159/1 in first Test in NZ"),
    (19, "Sensex climbs about 898 points"),
    (20, "NSE passes Nasdaq in size"),
    (21, "Banks report vendor cyberattack"),
    (22, "Gupta jailed for about 20 years"),
    (23, "Suicide blast kills five in Pakistan"),
    (24, "UN warns global hunger worsening"),
    (25, "Voyager 1 reaches one light-day"),
    (26, "GTA VI rollout continues"),
    (27, "Nepal PM visits India"),
    (28, "Malaysia to resettle 10,000 Rohingya"),
    (29, "Indonesia fire losses may hit $30bn"),
    (30, "Carlsen quits rapid game"),
    (31, "Hyundai Elantra 2027 debuts in LA"),
    (32, "Fiji declares national disaster"),
    (33, "Hayabusa2 fails to land on asteroid"),
    (34, "Korea court clears ex-PM Han"),
    (35, "Kushner: Russia 'comfortable' on guarantees"),
]


def draw_feature(d, canvas, x, y, w, story, photo_h, head_size=15):
    assets = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "assets")
    img = cover(os.path.join(assets, story["photo"]), w, photo_h,
                focus_y=0.45)
    canvas.paste(img, (x, y))
    d.rectangle([x, y, x + w - 1, y + photo_h - 1], outline=NAVY, width=1)
    y += photo_h + 5
    kf = font(SANS_B, 10)
    d.text((x, y), story["kicker"], font=kf, fill=RED)
    y += 14
    hf = font(SERIF_B, head_size)
    for line in wrap(d, story["head"], hf, w):
        d.text((x, y), line, font=hf, fill=INK)
        y += head_size + 3
    df = font(SERIF, 11)
    for line in wrap(d, story["deck"], df, w)[:2]:
        d.text((x, y), line, font=df, fill=MUTED)
        y += 14
    return y


def draw_wide(d, canvas, x, y, w, story):
    assets = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "assets")
    pw = 168
    img = cover(os.path.join(assets, story["photo"]), pw, 92, focus_y=0.45)
    canvas.paste(img, (x, y))
    d.rectangle([x, y, x + pw - 1, y + 91], outline=NAVY, width=1)
    tx = x + pw + 10
    tw = w - pw - 10
    kf = font(SANS_B, 10)
    d.text((tx, y + 2), story["kicker"], font=kf, fill=RED)
    hf = font(SERIF_B, 16)
    yy = y + 18
    for line in wrap(d, story["head"], hf, tw):
        d.text((tx, yy), line, font=hf, fill=INK)
        yy += 19
    df = font(SERIF, 11)
    for line in wrap(d, story["deck"], df, tw):
        d.text((tx, yy), line, font=df, fill=MUTED)
        yy += 14
    return max(y + 92, yy)


def build_page(out_path):
    assets = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                          "assets")
    # Real newsprint photograph as the base layer: cover-cropped to
    # the full page, so the paper grain, vignette and fold are even
    # across the sheet. No flat fill, no arithmetic speckle, and no
    # flat paper patch anywhere else on the page.
    img = cover(os.path.join(assets, "paper_bg.png"), W, H)
    d = ImageDraw.Draw(img)

    # Gold top rule.
    d.rectangle([MARGIN, 6, W - MARGIN, 10], fill=GOLD)

    # Masthead: globe + huge serif title + tagline.
    draw_globe(d, 66, 48, 32)
    title_f = fit_font(d, "THE WORLD HERALD", SERIF_B, 860, 58)
    tw = d.textlength("THE WORLD HERALD", font=title_f)
    d.text(((W - tw) / 2, 14), "THE WORLD HERALD", font=title_f, fill=NAVY)
    tag_f = font(SANS_B, 12)
    tag = "INFORM  •  ANALYZE  •  CONNECT"
    tw = d.textlength(tag, font=tag_f)
    d.text(((W - tw) / 2, 70), tag, font=tag_f, fill=MUTED)
    d.line([MARGIN, 86, W - MARGIN, 86], fill=RULE, width=1)

    # Navy date bar.
    d.rectangle([MARGIN, 90, W - MARGIN, 112], fill=NAVY)
    dl_f = font(SANS_B, 13)
    d.text((MARGIN + 10, 95),
           "WORLD EDITION  •  SATURDAY, 21 NOVEMBER 2026",
           font=dl_f, fill=WHITE)
    dr_f = font(SANS, 11)
    rt = "A MORE INFORMED WORLD"
    d.text((W - MARGIN - 10 - d.textlength(rt, font=dr_f), 96),
           rt, font=dr_f, fill=WHITE)

    # Giant red hero headline.
    head_f = fit_font(d, "MISSILES FALL ON POLAND", SERIF_B, CW, 64)
    hw = d.textlength("MISSILES FALL ON POLAND", font=head_f)
    hb = d.textbbox((0, 0), "MISSILES FALL ON POLAND", font=head_f)
    d.text(((W - hw) / 2, 118), "MISSILES FALL ON POLAND",
           font=head_f, fill=RED)

    # Italic deck, two lines, centred below the headline's real bottom.
    deck_f = font(SERIF, 15)
    deck = [
        "Two Russian missiles and a jet drone fall in the south-east amid",
        "a 400-drone barrage on Ukraine. Tusk: 'intentional provocation'.",
    ]
    dy = 118 + hb[3] + 6
    for line in deck:
        lw = d.textlength(line, font=deck_f)
        draw_italic(img, ((W - lw) / 2, dy), line, deck_f, INK)
        dy += 17
    ry = dy + 4
    d.line([MARGIN, ry, W - MARGIN, ry], fill=RED, width=2)
    d.line([MARGIN, ry + 4, W - MARGIN, ry + 4], fill=NAVY, width=1)

    # Hero band: wide Europe map + Wall Street column.
    hy = ry + 10
    hero_map = cover(os.path.join(assets, "hero_map7.png"), 672, 160,
                     focus_y=0.42)
    img.paste(hero_map, (MARGIN, hy))
    d.rectangle([MARGIN, hy, MARGIN + 671, hy + 159], outline=NAVY, width=1)
    cap_f = font(SERIF, 10)
    d.text((MARGIN, hy + 164),
           "NATO jets scramble as Russian missiles fall in south-east Poland.",
           font=cap_f, fill=MUTED)

    mx = MARGIN + 672 + 12
    mw = W - MARGIN - mx  # 284
    mk = cover(os.path.join(assets, "hero_markets7.png"), mw, 78,
               focus_y=0.5)
    img.paste(mk, (mx, hy))
    d.rectangle([mx, hy, mx + mw - 1, hy + 77], outline=NAVY, width=1)
    my = hy + 82
    kf = font(SANS_B, 10)
    d.text((mx, my), "2  •  MARKETS — WALL STREET", font=kf, fill=RED)
    my += 14
    hf = font(SERIF_B, 15)
    for line in wrap(d, "WALL STREET IN FREEFALL AS TECH CRASHES", hf, mw):
        d.text((mx, my), line, font=hf, fill=INK)
        my += 18
    df = font(SERIF, 11)
    for line in wrap(d, "The S&P 500 sinks 3.7% in a seventh straight "
                        "fall; the Nasdaq plunges 5.3% in its worst week "
                        "since 2020.", df, mw):
        d.text((mx, my), line, font=df, fill=MUTED)
        my += 13

    y = hy + 192
    lab = "MORE OF THE DAY"
    lf = font(SERIF_B, 16)
    lw = d.textlength(lab, font=lf)
    lab_end = MARGIN + 18 + lw + 12
    # No flat paper chip behind the label: the rule starts after the
    # label, so the red square and the navy title sit straight on the
    # paper texture with no patch showing.
    d.rectangle([MARGIN, y - 6, MARGIN + 12, y + 6], fill=RED)
    d.text((MARGIN + 18, y - 8), lab, font=lf, fill=NAVY)
    d.line([lab_end + 6, y, W - MARGIN, y], fill=NAVY, width=1)
    y += 10

    # Featured grid: 3 columns x 2 rows, all with photographs.
    col_w = (CW - 28) // 3
    for row in range(2):
        row_y = y + row * (152 + 8)
        for col in range(3):
            story = FEATURED[row * 3 + col]
            draw_feature(d, img, MARGIN + col * (col_w + 14), row_y,
                         col_w, story, 80, head_size=14)
    y += 2 * 152 + 8 + 6

    # Wide row: COP31 + cancer pill, photo left, text right.
    wide_w = (CW - 14) // 2
    for i, story in enumerate(WIDE):
        draw_wide(d, img, MARGIN + i * (wide_w + 14), y, wide_w, story)
    y += 80 + 6
    d.line([MARGIN, y, W - MARGIN, y], fill=NAVY, width=1)
    y += 6

    # Bottom block: numbered world map + 25 briefs in two columns.
    bh_f = font(SERIF_B, 14)
    d.text((MARGIN, y), "AROUND THE WORLD", font=bh_f, fill=NAVY)
    bt = "ALSO ON SATURDAY — 25 MORE STORIES"
    d.text((MARGIN + 312, y), bt, font=bh_f, fill=NAVY)
    y += 18
    draw_world_map(img, MARGIN, y, 300, 126)
    src_f = font(SANS, 9)
    d.text((MARGIN, y + 130),
           "Sources: wire reports from 21 Nov 2026. "
           "Hero images are AI-generated illustrations.",
           font=src_f, fill=MUTED)
    bx = MARGIN + 312
    bw = W - MARGIN - bx
    colw = (bw - 12) // 2
    bf = font(SANS, 10)
    bnf = font(SANS_B, 10)
    for i, (num, text) in enumerate(BRIEFS):
        col = i // 13
        row = i % 13
        lx = bx + col * (colw + 12)
        ly = y + row * 10
        d.text((lx, ly), str(num), font=bnf, fill=RED)
        d.text((lx + 20, ly), text, font=bf, fill=INK)
    y += 142

    # Markets ticker bar.
    d.rectangle([MARGIN, y, W - MARGIN, y + 18], fill=NAVY)
    tk_f = font(SANS_B, 11)
    tick = ("GLOBAL MARKETS  •  S&P 500 -3.7%  •  NASDAQ -5.3%  •  "
            "DOW -950 PTS  •  NVIDIA -14%  •  ANTHROPIC -9%  •  VIX 35.89")
    tw = d.textlength(tick, font=tk_f)
    d.text(((W - tw) / 2, y + 3), tick, font=tk_f, fill=WHITE)
    y += 18

    img.save(out_path, format="PNG")
    return y
