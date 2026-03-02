"""
Image Generator — dynamic Pexels image fetching.

What makes it dynamic:
  1. Per-deity search variations  — each deity has 5-7 different query angles
     (meditation, cosmic, battle, blessing, festival, close-up, wide…)
  2. Random Pexels page           — pages 1-5 so we don't always get the same top photos
  3. Scene modifiers appended     — "golden light", "ancient temple", "celestial" etc.
  4. Used-photo deduplication     — tracks photo IDs within a single video run
  5. Multiple query fallbacks     — tries 3 different queries before giving up
"""

import time
from io import BytesIO
from pathlib import Path

import requests
from PIL import Image, ImageDraw

from config import VIDEO_WIDTH, VIDEO_HEIGHT, TEMP_DIR, PEXELS_API_KEY

# ── Rich per-deity query variations ──────────────────────────────────────────
_DEITY_QUERIES: dict[str, list[str]] = {
    "shiva": [
        "lord shiva meditation",
        "shiva cosmic dance tandav",
        "mahadev shiva third eye",
        "shiva mount kailash",
        "shiva lingam temple offering",
        "lord shiva ascetic yogi",
        "shiva destroyer transformation",
    ],
    "krishna": [
        "lord krishna flute divine",
        "krishna radha love spiritual",
        "krishna warrior bhagavad gita",
        "krishna childhood butter pot",
        "krishna peacock feather portrait",
        "krishna cosmic vishwaroop",
        "krishna devotion bhakti",
    ],
    "ganesha": [
        "lord ganesha golden statue",
        "ganesha elephant god blessing",
        "ganesha festival celebration",
        "ganesha wisdom prosperity",
        "ganesh chaturthi idol",
        "ganesha om sacred",
    ],
    "durga": [
        "goddess durga warrior lion",
        "durga navratri festival",
        "goddess shakti powerful divine",
        "durga mahishasura battle",
        "durga temple offerings lamp",
        "navdurga nine forms",
    ],
    "lakshmi": [
        "goddess lakshmi lotus gold",
        "lakshmi diwali prosperity",
        "goddess wealth abundance flowers",
        "lakshmi four hands divine",
        "lakshmi temple offering",
    ],
    "vishnu": [
        "lord vishnu preserver cosmic",
        "vishnu blue divine four arms",
        "vishnu avatar dashavatara",
        "vishnu ocean serpent ananta",
        "vishnu vaikunta celestial",
    ],
    "hanuman": [
        "lord hanuman devotion bhakti",
        "hanuman flying mountain",
        "hanuman strength warrior",
        "hanuman ram devotee",
        "hanuman anjali pose",
        "hanuman chalisa sacred",
    ],
    "rama": [
        "lord rama bow arrow warrior",
        "ram sita divine couple",
        "dussehra rama victory",
        "ram navami celebration",
        "rama ayodhya temple",
    ],
    "saraswati": [
        "goddess saraswati veena music",
        "saraswati knowledge learning",
        "saraswati vasant panchami",
        "goddess wisdom white swan",
    ],
    "brahma": [
        "lord brahma creator four heads",
        "brahma lotus creation",
        "brahma temple pushkar",
    ],
    "kali": [
        "goddess kali powerful divine",
        "kali ma fierce shakti",
        "kali puja festival",
    ],
    "parvati": [
        "goddess parvati divine mother",
        "parvati shiva family",
        "parvati beauty sacred",
    ],
    "murugan": [
        "lord murugan vel warrior",
        "murugan tamilnadu temple",
        "murugan peacock kavadi",
    ],
}

# Generic fallback queries when no deity matched
_GENERIC_QUERIES = [
    "hindu temple golden architecture",
    "india spiritual devotion",
    "diwali festival lights celebration",
    "indian classical dance sacred",
    "yoga meditation sunrise spiritual",
    "hindu ritual puja lamp",
    "india religious festival colorful",
    "ancient indian sculpture stone",
]

# Saffron-themed fallback palettes
_FALLBACK_PALETTES = [
    [(255, 140, 0),  (200, 60,  0)],
    [(75,  0,   130), (148, 0,  211)],
    [(0,   80,  160), (0,  160, 220)],
    [(139, 0,   0),   (220, 20,  60)],
    [(0,   100, 0),   (34,  139, 34)],
    [(180, 120, 0),   (255, 215,  0)],
    [(70,  0,   90),  (220, 50,  150)],
    [(20,  60,  100), (100, 180, 255)],
]


def _build_queries(prompt: str) -> list[str]:
    """
    Build 2-3 specific search queries from a prompt.
    Returns [deity_query_1, deity_query_2, generic_fallback].
    No randomness — picks the first 2 variations for the deity found.
    """
    prompt_lower = prompt.lower()
    queries = []

    for deity, variations in _DEITY_QUERIES.items():
        if deity in prompt_lower:
            # Take the first 2 variations (most specific/popular for this deity)
            for base in variations[:2]:
                queries.append(base)
            break

    # Always add one generic fallback as the 3rd query
    queries.append(_GENERIC_QUERIES[0])
    return queries[:3]


def _fetch_best_image(queries: list[str], output_path: Path, used_ids: set) -> bool:
    """
    For each of the 2-3 queries, fetch the top 3 results from page 1.
    Combine into a pool of up to 9 photos, sort by resolution (highest first),
    then download the best unused one. No random selection.
    """
    if not PEXELS_API_KEY:
        return False

    pool: list = []
    seen_ids: set = set()

    for query in queries:
        try:
            resp = requests.get(
                "https://api.pexels.com/v1/search",
                headers={"Authorization": PEXELS_API_KEY},
                params={
                    "query": query,
                    "orientation": "portrait",
                    "per_page": 3,   # top 3 from each keyword
                    "page": 1,
                    "size": "large",
                },
                timeout=20,
            )
            if resp.status_code == 200:
                photos = resp.json().get("photos", [])
                # Deduplicate across queries
                for p in photos:
                    if p["id"] not in seen_ids:
                        seen_ids.add(p["id"])
                        pool.append(p)
                print(f"    '{query}' → {len(photos)} results")
        except Exception as exc:
            print(f"    Pexels error for '{query}': {exc}")

    # Remove already-used photos
    pool = [p for p in pool if p["id"] not in used_ids]
    if not pool:
        return False

    # Sort by resolution — highest quality first, no random
    pool.sort(key=lambda p: p["width"] * p["height"], reverse=True)

    for photo in pool:
        try:
            img_url = photo["src"]["portrait"]
            img_resp = requests.get(img_url, timeout=30)
            if img_resp.status_code == 200 and len(img_resp.content) > 5_000:
                img = Image.open(BytesIO(img_resp.content)).convert("RGB")
                img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)
                img.save(output_path, "JPEG", quality=95)
                used_ids.add(photo["id"])
                print(f"    Selected: {photo['width']}×{photo['height']}px  (id={photo['id']})")
                return True
        except Exception as exc:
            print(f"    Download error: {exc}")

    return False


def _fallback_image(index: int, output_path: Path) -> Path:
    """Last-resort gradient fallback using Pillow."""
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


def generate_all_images(prompts: list, run_id: str) -> list[Path]:
    """Fetch all images for a video with maximum variety."""
    if not PEXELS_API_KEY:
        print("  [WARN] PEXELS_API_KEY not set — all images will be gradients.")

    image_dir = TEMP_DIR / run_id / "images"
    image_dir.mkdir(parents=True, exist_ok=True)

    used_ids: set = set()   # prevent duplicate photos within one video
    paths = []

    for i, prompt in enumerate(prompts):
        out = image_dir / f"image_{i:02d}.jpg"
        print(f"  [{i + 1}/{len(prompts)}] Fetching image…")

        queries = _build_queries(prompt)
        if not _fetch_best_image(queries, out, used_ids):
            print(f"    Using gradient fallback")
            out = _fallback_image(i, out)

        paths.append(out)
        if i < len(prompts) - 1:
            time.sleep(0.3)

    return paths
