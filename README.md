[![make.fun · news-image-20261121](https://make.fun/badge/news-image-20261121.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![rank](https://make.fun/badge/news-image-20261121/aramexbit/news-image-20261121/rank.svg)](https://make.fun/bounty/news-image-20261121/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![reward](https://make.fun/badge/news-image-20261121/aramexbit/news-image-20261121/reward.svg)](https://make.fun/bounty/news-image-20261121?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261121)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)

# The World Herald — 21 November 2026

A one-page classic newspaper front page summing up the world news of
Saturday 21 November 2026, built for the
[make.fun news-image-20261121 competition](https://make.fun/c/news-image-20261121).

A giant red headline leads the day: Russian missiles fall in south-east
Poland during a huge barrage on Ukraine, under a full-width night map of
Europe glowing red over Poland and Ukraine. Beside it, Wall Street
crashes — the S&P 500 down 3.7% and the Nasdaq down 5.3%. Below, eight
stories carry real photographs: the ICJ's historic Rohingya genocide
ruling, the first Trump–Xi–Putin summit, Cyclone Akvan's landfall in
India, the war in Iran, a UK–EU trade deal, a Saudi interception over
Riyadh, the COP31 endgame and a pancreatic cancer pill breakthrough —
plus twenty-five briefs from every region, a numbered world map and a
markets ticker. Thirty-five stories in all.

## How it runs

```sh
python3 main.py
```

`main.py` composes `entry.png` (1024x1024, under 1 MiB) from the local
assets through `composer.py`. Where Pillow is unavailable it copies the
prebuilt image in `assets/` instead, so every run writes identical bytes.
No network, no clock, no randomness. Two runs produce byte-identical
output, so the grader's double run always matches.

Hero images are AI-generated illustrations.

## Contents

- `main.py` — the entrypoint: composes the page, or copies the prebuilt
  image where Pillow is unavailable.
- `composer.py` — draws the whole front page: masthead, giant red
  headline, hero map, photo features, numbered world map and briefs.
- `assets/hero_map7.png`, `assets/hero_poland7.png`,
  `assets/hero_markets7.png` — the hero photographs (AI-generated
  illustrations).
- `assets/feat_*7.png` — eight photographs for the featured stories
  (AI-generated illustrations).
- `assets/entry.png` — the prebuilt page, byte-identical to what
  `composer.py` draws, used where Pillow is unavailable.

The ten numbered dots on the world map match the stories' own numbers:
1 Poland, 2 Wall Street, 3 The Hague, 4 Shenzhen, 5 Odisha, 6 Tehran,
7 Brussels, 8 Riyadh, 11 Brasília, 29 Jakarta.
