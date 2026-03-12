"""
Video Fetcher — Pexels Videos → Pixabay Videos fallback chain.

Downloads video clips and trims them to an EXACT duration calculated from the
voiceover length.  The caller passes `vo_duration` so we know precisely how
many seconds each clip needs to be before we start downloading:

    clip_duration = vo_duration / CLIPS_PER_VIDEO

Every downloaded clip is center-cropped to 9:16 (1080×1920) and trimmed to
exactly `clip_duration` seconds — no stretching, no silent gaps, no padding.

Source priority:
  1. Pexels Videos  (existing PEXELS_API_KEY)
  2. Pixabay Videos (free PIXABAY_API_KEY — register at pixabay.com/api/docs/)
  3. Solid-colour gradient fallback (FFmpeg lavfi — last resort)
"""

import json
import subprocess
import time
from pathlib import Path

import requests

from config import VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_FPS, TEMP_DIR, PEXELS_API_KEY, PIXABAY_API_KEY

CLIPS_PER_VIDEO = 8   # number of clips to assemble per Short

_HEADERS = {"User-Agent": "YTShortsBot/1.0"}


# ── FFmpeg helpers ─────────────────────────────────────────────────────────────

def _run_ffmpeg(cmd: list, step: str) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed [{step}]:\n{result.stderr[-800:]}")


def _probe_duration(path: Path) -> float:
    """Return media duration in seconds via ffprobe."""
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def _crop_and_trim(src: Path, dst: Path, duration: float) -> bool:
    """
    Center-crop the video to 9:16, scale to 1080×1920, trim to `duration` seconds.
    Audio is stripped — we overlay our own voiceover during assembly.
    Returns True on success.
    """
    try:
        # Crop the narrower dimension: keep full height, crop width to ih*(9/16)
        crop_filter = (
            f"crop=ih*9/16:ih:(iw-ih*9/16)/2:0,"
            f"scale={VIDEO_WIDTH}:{VIDEO_HEIGHT},"
            "setsar=1"
        )
        _run_ffmpeg(
            [
                "ffmpeg", "-y",
                "-i", str(src),
                "-t", f"{duration:.3f}",
                "-vf", crop_filter,
                "-r", str(VIDEO_FPS),
                "-c:v", "libx264",
                "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                "-an",          # strip audio — voiceover replaces it
                str(dst),
            ],
            step=f"crop-trim {src.name}",
        )
        return dst.exists() and dst.stat().st_size > 10_000
    except Exception as exc:
        print(f"      Crop/trim error: {exc}")
        return False


# ── Source 1: Pexels Videos ────────────────────────────────────────────────────

def _fetch_pexels_videos(
    query: str, clip_dir: Path, start_idx: int, needed: int,
    clip_duration: float, used_ids: set,
) -> list[Path]:
    if not PEXELS_API_KEY:
        return []
    paths: list[Path] = []
    try:
        resp = requests.get(
            "https://api.pexels.com/videos/search",
            headers={"Authorization": PEXELS_API_KEY},
            params={
                "query": query,
                "orientation": "portrait",
                "per_page": needed * 4,
                "page": 1,
                "size": "medium",
            },
            timeout=20,
        )
        if resp.status_code != 200:
            print(f"      [Pexels Video] HTTP {resp.status_code}")
            return []

        videos = [v for v in resp.json().get("videos", []) if v["id"] not in used_ids]

        for video in videos:
            if len(paths) >= needed:
                break
            # Only consider clips at least as long as what we need
            if video.get("duration", 0) < clip_duration:
                continue

            # Pick the best quality file that fits in 1080p (avoid huge 4K downloads)
            files = sorted(
                [f for f in video.get("video_files", []) if f.get("width") and f["width"] <= 1920],
                key=lambda f: f["width"] * f.get("height", 0),
                reverse=True,
            )
            if not files:
                continue

            url = files[0]["link"]
            raw = clip_dir / f"pex_raw_{start_idx + len(paths):02d}.mp4"
            out = clip_dir / f"clip_{start_idx + len(paths):02d}.mp4"

            # Download
            try:
                r = requests.get(url, headers=_HEADERS, timeout=90, stream=True)
                if r.status_code != 200:
                    continue
                with open(raw, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=65536):
                        fh.write(chunk)
            except Exception as exc:
                print(f"      [Pexels Video] download error: {exc}")
                raw.unlink(missing_ok=True)
                continue

            # Verify actual downloaded duration (API duration field can be wrong)
            try:
                actual_dur = _probe_duration(raw)
                if actual_dur < clip_duration:
                    print(f"      [Pexels Video] too short ({actual_dur:.1f}s < {clip_duration:.1f}s), skip")
                    raw.unlink(missing_ok=True)
                    continue
            except Exception:
                raw.unlink(missing_ok=True)
                continue

            if _crop_and_trim(raw, out, clip_duration):
                used_ids.add(video["id"])
                paths.append(out)
                print(f"      [Pexels Video] id={video['id']} → {out.name}")
            raw.unlink(missing_ok=True)

    except Exception as exc:
        print(f"      [Pexels Video] error: {exc}")

    return paths


# ── Source 2: Pixabay Videos ───────────────────────────────────────────────────

def _fetch_pixabay_videos(
    query: str, clip_dir: Path, start_idx: int, needed: int,
    clip_duration: float, used_ids: set,
) -> list[Path]:
    if not PIXABAY_API_KEY:
        return []
    paths: list[Path] = []
    try:
        resp = requests.get(
            "https://pixabay.com/api/videos/",
            params={
                "key": PIXABAY_API_KEY,
                "q": query,
                "per_page": needed * 4,
                "orientation": "vertical",
                "safesearch": "true",
            },
            headers=_HEADERS,
            timeout=20,
        )
        if resp.status_code != 200:
            print(f"      [Pixabay Video] HTTP {resp.status_code}")
            return []

        hits = [h for h in resp.json().get("hits", []) if h["id"] not in used_ids]

        for hit in hits:
            if len(paths) >= needed:
                break
            if hit.get("duration", 0) < clip_duration:
                continue

            # Prefer medium quality; fall back to large then small
            videos_dict = hit.get("videos", {})
            chosen = (
                videos_dict.get("medium")
                or videos_dict.get("large")
                or videos_dict.get("small")
            )
            if not chosen or not chosen.get("url"):
                continue

            url = chosen["url"]
            raw = clip_dir / f"pix_raw_{start_idx + len(paths):02d}.mp4"
            out = clip_dir / f"clip_{start_idx + len(paths):02d}.mp4"

            try:
                r = requests.get(url, headers=_HEADERS, timeout=90, stream=True)
                if r.status_code != 200:
                    continue
                with open(raw, "wb") as fh:
                    for chunk in r.iter_content(chunk_size=65536):
                        fh.write(chunk)
            except Exception as exc:
                print(f"      [Pixabay Video] download error: {exc}")
                raw.unlink(missing_ok=True)
                continue

            try:
                actual_dur = _probe_duration(raw)
                if actual_dur < clip_duration:
                    raw.unlink(missing_ok=True)
                    continue
            except Exception:
                raw.unlink(missing_ok=True)
                continue

            if _crop_and_trim(raw, out, clip_duration):
                used_ids.add(hit["id"])
                paths.append(out)
                print(f"      [Pixabay Video] id={hit['id']} → {out.name}")
            raw.unlink(missing_ok=True)

    except Exception as exc:
        print(f"      [Pixabay Video] error: {exc}")

    return paths


# ── Gradient fallback ──────────────────────────────────────────────────────────

_FALLBACK_COLORS = [
    ("0xFF8C00", "0xC83C00"),   # saffron
    ("0x4B0082", "0x9400D3"),   # violet
    ("0x00509E", "0x00A0DC"),   # blue
    ("0x8B0000", "0xDC143C"),   # crimson
    ("0x006400", "0x228B22"),   # green
    ("0xB47800", "0xFFD700"),   # gold
]


def _gradient_clip_fallback(index: int, clip_dir: Path, duration: float) -> Path:
    """Generate a simple gradient video clip using FFmpeg as last resort."""
    c1, c2 = _FALLBACK_COLORS[index % len(_FALLBACK_COLORS)]
    out = clip_dir / f"clip_{index:02d}.mp4"
    try:
        _run_ffmpeg(
            [
                "ffmpeg", "-y",
                "-f", "lavfi",
                "-i", (
                    f"gradients=s={VIDEO_WIDTH}x{VIDEO_HEIGHT}"
                    f":c0={c1}:c1={c2}"
                    f":duration={duration:.3f}:speed=0.01"
                ),
                "-t", f"{duration:.3f}",
                "-r", str(VIDEO_FPS),
                "-c:v", "libx264", "-preset", "veryfast",
                "-pix_fmt", "yuv420p",
                str(out),
            ],
            step=f"gradient-fallback {index}",
        )
        if out.exists() and out.stat().st_size > 1000:
            return out
    except Exception:
        pass

    # Ultra-fallback: solid colour
    _run_ffmpeg(
        [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={c1}:s={VIDEO_WIDTH}x{VIDEO_HEIGHT}:r={VIDEO_FPS}",
            "-t", f"{duration:.3f}",
            "-c:v", "libx264", "-preset", "veryfast",
            "-pix_fmt", "yuv420p",
            str(out),
        ],
        step=f"solid-fallback {index}",
    )
    return out


# ── Public API ─────────────────────────────────────────────────────────────────

def fetch_all_video_clips(
    search_terms: list[str], run_id: str, vo_duration: float
) -> list[Path]:
    """
    Fetch CLIPS_PER_VIDEO video clips, each trimmed to exactly:

        clip_duration = vo_duration / CLIPS_PER_VIDEO

    The clips are downloaded AT the right length so total video time equals the
    voiceover duration — every second of every clip is used, nothing wasted.

    Returns list of CLIPS_PER_VIDEO ready-to-concatenate clip paths.
    """
    clip_dir = TEMP_DIR / run_id / "clips"
    clip_dir.mkdir(parents=True, exist_ok=True)

    clip_duration = max(vo_duration / CLIPS_PER_VIDEO, 3.0)
    print(f"  Target: {CLIPS_PER_VIDEO} clips × {clip_duration:.2f}s = {clip_duration * CLIPS_PER_VIDEO:.1f}s total")

    used_ids: set = set()
    all_clips: list[Path] = []

    for term in search_terms:
        if len(all_clips) >= CLIPS_PER_VIDEO:
            break

        needed = min(2, CLIPS_PER_VIDEO - len(all_clips))
        start_idx = len(all_clips)
        print(f"  Searching '{term}' (need {needed} clips × {clip_duration:.2f}s)…")

        batch: list[Path] = []

        # 1. Pexels Videos
        batch += _fetch_pexels_videos(
            term, clip_dir, start_idx + len(batch), needed - len(batch),
            clip_duration, used_ids,
        )

        # 2. Pixabay Videos (if still short)
        if len(batch) < needed:
            batch += _fetch_pixabay_videos(
                term, clip_dir, start_idx + len(batch), needed - len(batch),
                clip_duration, used_ids,
            )

        all_clips.extend(batch)
        print(f"    → {len(batch)}/{needed} clips fetched")

        if len(all_clips) < CLIPS_PER_VIDEO:
            time.sleep(0.4)

    # Gradient fallback for remaining slots
    while len(all_clips) < CLIPS_PER_VIDEO:
        idx = len(all_clips)
        print(f"  [{idx + 1}] Gradient fallback clip")
        all_clips.append(_gradient_clip_fallback(idx, clip_dir, clip_duration))

    return all_clips[:CLIPS_PER_VIDEO]
