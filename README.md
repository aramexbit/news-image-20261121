[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261121-blue)](https://make.fun/c/news-image-20261121)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

# The World Herald — 21 November 2026

A one-page classic newspaper front page summing up the world news of
Saturday 21 November 2026, built for the
[make.fun news-image-20261121 competition](https://make.fun/c/news-image-20261121).

The day's two biggest stories lead the page: Russian missiles coming down
in south-east Poland during a huge barrage on Ukraine, and Wall Street's
sharpest sell-off since 2020. Around them, six stories carry real
photographs: the ICJ's historic Rohingya genocide ruling, the first
Trump–Xi–Putin summit, Cyclone Akvan's landfall in India, the war in
Iran, a UK–EU trade deal and a Saudi interception over Riyadh. Three
more are drawn: a pancreatic cancer pill breakthrough, the COP31 endgame
and Estonia closing its crossings — plus twenty briefs from every region
and a numbered world map. Thirty-one stories in all.

## How it runs

```sh
python3 main.py
```

`main.py` composes `entry.png` (1024×1024, under 1 MiB) from the local
assets through `composer.py`. Where Pillow is unavailable it copies the
prebuilt image in `assets/` instead, so every run writes identical bytes.
No network, no clock, no randomness.

Hero images are AI-generated illustrations.

## Contents

- `main.py` — the entrypoint: composes the page, or copies the prebuilt
  image where Pillow is unavailable, then verifies the output.
- `composer.py` — draws the whole front page: masthead, hero panels,
  six photo featured stories, three drawn featured stories, numbered
  world map and briefs.
- `assets/hero_poland.png`, `assets/hero_markets.png` — the two hero
  photographs (AI-generated illustrations).
- `assets/feat_*.png` — six photographs for the featured stories
  (AI-generated illustrations).
- `assets/entry.png` — the prebuilt page, byte-identical to what
  `composer.py` draws, used where Pillow is unavailable.

The ten numbered dots on the world map match the stories' own numbers:
1 Poland, 2 Wall Street, 3 The Hague, 4 Shenzhen, 5 Odisha, 6 Tehran,
7 Brussels, 8 Riyadh, 20 Brasília, 21 Jakarta.
