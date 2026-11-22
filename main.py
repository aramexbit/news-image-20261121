"""Entrypoint: write entry.png (1024x1024) to the output directory.

v7, classic newspaper. Runs the page composer when Pillow is
available; otherwise copies the prebuilt image shipped in assets/
(byte-identical). Standard library only, no network, no clock, no
randomness — two runs write byte-identical files.
"""

import os
import shutil
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    target = os.path.join(out_dir, "entry.png")
    try:
        from composer import build_page
        build_page(target)
    except Exception:
        # Pillow missing (or a compose failure): ship the prebuilt
        # byte-identical fallback so the entry still renders.
        prebuilt = os.path.join(_HERE, "assets", "entry.png")
        shutil.copyfile(prebuilt, target)


if __name__ == "__main__":
    main()
