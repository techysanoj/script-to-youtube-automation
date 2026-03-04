"""
Image Generator — Wikimedia Commons → Unsplash → Pexels fallback chain.

Gemini provides 5 two-word search terms.
We fetch 2 images per term (up to 10 total) and return the first
IMAGES_PER_VIDEO (8) results.

Source priority for each image slot:
  1. Wikimedia Commons  (free, no key — rich Hindu deity art + illustrations)
  2. Unsplash           (free Access Key — high quality photography)
  3. Pexels             (free key — good general stock photos)
  4. Gradient           (last-resort Pillow fallback)
"""

import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw

from config import (
    VIDEO_WIDTH, VIDEO_HEIGHT, TEMP_DIR,
    UNSPLASH_ACCESS_KEY, PEXELS_API_KEY, IMAGES_PER_VIDEO,
)

# Saffron-themed gradient fallback palettes
_FALLBACK_PALETTES = [
    [(255, 140, 0),   (200, 60,  0)],
    [(75,  0,   130), (148, 0,  211)],
    [(0,   80,  160), (0,  160, 220)],
    [(139, 0,   0),   (220, 20,  60)],
    [(0,   100, 0),   (34,  139, 34)],
    [(180, 120, 0),   (255, 215,  0)],
    [(70,  0,   90),  (220, 50,  150)],
    [(20,  60,  100), (100, 180, 255)],
]

_HEADERS = {"User-Agent": "YTShortsBot/1.0"}


# ── Shared helpers ─────────────────────────────────────────────────────────────

def _download_and_save(url: str, output_path: Path, extra_headers: dict | None = None) -> bool:
    """Download an image URL, resize to portrait 9:16, save as JPEG. Returns True on success."""
    try:
        h = {**_HEADERS, **(extra_headers or {})}
        resp = requests.get(url, headers=h, timeout=30)
        if resp.status_code == 200 and len(resp.content) > 5_000:
            img = Image.open(BytesIO(resp.content)).convert("RGB")
            img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)
            img.save(output_path, "JPEG", quality=95)
            return True
    except Exception as exc:
        print(f"      Download error: {exc}")
    return False


def _fallback_image(index: int, output_path: Path) -> Path:
    """Last-resort gradient image using Pillow."""
    colors = _FALLBACK_PALETTES[index % len(_FALLBACK_PALETTES)]
    img = Image.new("RGB", (VIDEO_WIDTH, VIDEO_HEIGHT))
    draw = ImageDraw.Draw(img)
    for y in range(VIDEO_HEIGHT):
        t = y / VIDEO_HEIGHT
        r = int(colors[0][0] * (1 - t) + colors[1][0] * t)
        g = int(colors[0][1] * (1 - t) + colors[1][1] * t)
        b = int(colors[0][2] * (1 - t) + colors[1][2] * t)
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(r, g, b))
    img.save(output_path)
    return output_path


# ── Source 1: Wikimedia Commons ────────────────────────────────────────────────

def _fetch_wikimedia(
    query: str, image_dir: Path, start_idx: int, needed: int, used_ids: set
) -> list[Path]:
    """Fetch up to `needed` images from Wikimedia Commons (no API key required)."""
    paths: list[Path] = []
    try:
        # Step 1: search File namespace (ns=6) for matching titles
        search = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "list": "search",
                "srsearch": query,
                "srnamespace": 6,
                "srlimit": needed * 4,
                "format": "json",
            },
            headers=_HEADERS,
            timeout=20,
        )
        if search.status_code != 200:
            return []
        results = search.json().get("query", {}).get("search", [])
        titles = [r["title"] for r in results if r["title"] not in used_ids]
        if not titles:
            return []

        # Step 2: batch-fetch image URLs + mime types
        info = requests.get(
            "https://commons.wikimedia.org/w/api.php",
            params={
                "action": "query",
                "titles": "|".join(titles[: needed * 3]),
                "prop": "imageinfo",
                "iiprop": "url|size|mime",
                "iiurlwidth": VIDEO_WIDTH,
                "format": "json",
            },
            headers=_HEADERS,
            timeout=20,
        )
        if info.status_code != 200:
            return []

        pages = info.json().get("query", {}).get("pages", {}).values()
        for page in pages:
            if len(paths) >= needed:
                break
            if page.get("pageid", -1) < 0:   # missing page
                continue
            title = page.get("title", "")
            if title in used_ids:
                continue
            info_list = page.get("imageinfo", [])
            if not info_list:
                continue
            ii = info_list[0]
            if ii.get("mime", "") not in ("image/jpeg", "image/png", "image/webp"):
                continue
            url = ii.get("thumburl") or ii.get("url")
            if not url:
                continue
            out = image_dir / f"image_{start_idx + len(paths):02d}.jpg"
            if _download_and_save(url, out):
                used_ids.add(title)
                paths.append(out)
                print(f"      [Wikimedia] {title[5:55]}")   # strip "File:" prefix

    except Exception as exc:
        print(f"      [Wikimedia] error: {exc}")

    return paths


# ── Source 2: Unsplash ─────────────────────────────────────────────────────────

def _fetch_unsplash(
    query: str, image_dir: Path, start_idx: int, needed: int, used_ids: set
) -> list[Path]:
    """Fetch up to `needed` images from Unsplash (requires Access Key)."""
    if not UNSPLASH_ACCESS_KEY:
        return []
    paths: list[Path] = []
    try:
        resp = requests.get(
            "https://api.unsplash.com/search/photos",
            params={
                "query": query,
                "orientation": "portrait",
                "per_page": needed * 2,
                "client_id": UNSPLASH_ACCESS_KEY,
            },
            headers=_HEADERS,
            timeout=20,
        )
        if resp.status_code != 200:
            print(f"      [Unsplash] HTTP {resp.status_code}")
            return []
        photos = [p for p in resp.json().get("results", []) if p["id"] not in used_ids]
        for photo in photos:
            if len(paths) >= needed:
                break
            url = photo["urls"]["regular"]   # ~1080px wide
            out = image_dir / f"image_{start_idx + len(paths):02d}.jpg"
            if _download_and_save(url, out):
                used_ids.add(photo["id"])
                paths.append(out)
                print(f"      [Unsplash] id={photo['id']}")
                # Trigger download tracking as required by Unsplash API guidelines
                try:
                    requests.get(
                        f"https://api.unsplash.com/photos/{photo['id']}/download",
                        params={"client_id": UNSPLASH_ACCESS_KEY},
                        headers=_HEADERS,
                        timeout=5,
                    )
                except Exception:
                    pass

    except Exception as exc:
        print(f"      [Unsplash] error: {exc}")

    return paths


# ── Source 3: Pexels ───────────────────────────────────────────────────────────

def _fetch_pexels(
    query: str, image_dir: Path, start_idx: int, needed: int, used_ids: set
) -> list[Path]:
    """Fetch up to `needed` images from Pexels (requires API key)."""
    if not PEXELS_API_KEY:
        return []
    paths: list[Path] = []
    try:
        resp = requests.get(
            "https://api.pexels.com/v1/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={
                "query": query,
                "orientation": "portrait",
                "per_page": needed * 2,
                "page": 1,
                "size": "large",
            },
            timeout=20,
        )
        if resp.status_code != 200:
            return []
        photos = [p for p in resp.json().get("photos", []) if p["id"] not in used_ids]
        photos.sort(key=lambda p: p["width"] * p["height"], reverse=True)
        for photo in photos:
            if len(paths) >= needed:
                break
            url = photo["src"]["portrait"]
            out = image_dir / f"image_{start_idx + len(paths):02d}.jpg"
            if _download_and_save(url, out):
                used_ids.add(photo["id"])
                paths.append(out)
                print(f"      [Pexels] id={photo['id']}")

    except Exception as exc:
        print(f"      [Pexels] error: {exc}")

    return paths


# ── Main entry point ───────────────────────────────────────────────────────────

def generate_all_images(search_terms: list[str], run_id: str) -> list[Path]:
    """Fetch 2 images per search term using Wikimedia → Unsplash → Pexels.

    5 terms × 2 images = up to 10 fetched; returns first IMAGES_PER_VIDEO (8).
    Any remaining slots are filled with gradient fallbacks.
    """
    image_dir = TEMP_DIR / run_id / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    used_ids: set = set()
    all_paths: list[Path] = []

    for term in search_terms:
        if len(all_paths) >= IMAGES_PER_VIDEO:
            break

        needed = min(2, IMAGES_PER_VIDEO - len(all_paths))
        start_idx = len(all_paths)
        print(f"  Searching '{term}' (need {needed})…")

        batch: list[Path] = []

        # 1. Wikimedia Commons
        batch += _fetch_wikimedia(term, image_dir, start_idx + len(batch), needed - len(batch), used_ids)

        # 2. Unsplash (if still short)
        if len(batch) < needed:
            batch += _fetch_unsplash(term, image_dir, start_idx + len(batch), needed - len(batch), used_ids)

        # 3. Pexels (if still short)
        if len(batch) < needed:
            batch += _fetch_pexels(term, image_dir, start_idx + len(batch), needed - len(batch), used_ids)

        all_paths.extend(batch)
        print(f"    → {len(batch)}/{needed} images fetched")

        if len(all_paths) < IMAGES_PER_VIDEO:
            time.sleep(0.4)

    # Gradient fallback for any remaining slots
    while len(all_paths) < IMAGES_PER_VIDEO:
        idx = len(all_paths)
        out = image_dir / f"image_{idx:02d}.jpg"
        print(f"  [{idx + 1}] Gradient fallback")
        all_paths.append(_fallback_image(idx, out))

    return all_paths[:IMAGES_PER_VIDEO]
