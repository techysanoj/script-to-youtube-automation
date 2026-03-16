"""
setup_fonts.py — Download required fonts for Devanagari rendering.

Run once before first use:
    python scripts/setup_fonts.py

Downloads:
  - NotoSansDevanagari-Bold.ttf  → assets/fonts/
  - NotoSansDevanagari-Regular.ttf → assets/fonts/

These fonts are used by:
  - FFmpeg subtitle rendering (karaoke captions)
  - Pillow thumbnail text rendering
  - Pillow hook-frame text overlay

On GitHub Actions (Ubuntu), fonts-noto-extra is installed via apt,
so this script is only needed for local macOS/Windows development.
"""

import sys
from pathlib import Path

import requests

FONTS_DIR = Path(__file__).parent.parent / "assets" / "fonts"

FONTS = {
    "NotoSansDevanagari-Bold.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari"
        "/static/NotoSansDevanagari-Bold.ttf"
    ),
    "NotoSansDevanagari-Regular.ttf": (
        "https://github.com/google/fonts/raw/main/ofl/notosansdevanagari"
        "/static/NotoSansDevanagari-Regular.ttf"
    ),
}


def download_font(name: str, url: str) -> None:
    dest = FONTS_DIR / name
    if dest.exists():
        print(f"  ✓ {name} already exists — skipping")
        return

    print(f"  Downloading {name}…", end=" ", flush=True)
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        dest.write_bytes(r.content)
        print(f"done ({len(r.content) // 1024} KB)")
    except Exception as e:
        print(f"FAILED: {e}")
        sys.exit(1)


def main() -> None:
    FONTS_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Downloading fonts to {FONTS_DIR}\n")
    for name, url in FONTS.items():
        download_font(name, url)
    print("\nAll fonts ready. Devanagari will now render correctly in subtitles and thumbnails.")


if __name__ == "__main__":
    main()
