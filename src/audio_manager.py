"""
Audio Manager — provides background music for videos.

Priority order:
  1. Any .mp3 / .wav file in assets/music/  (user-provided real tracks)
  2. Trending YouTube music (auto-downloaded daily — set YOUTUBE_API_KEY in .env)
  3. Auto-generated tanpura drone (devotional ambient, created once & cached)
"""

import json
import random
import re
import wave
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

from config import MUSIC_DIR, YOUTUBE_API_KEY

_GENERATED_PATH = MUSIC_DIR / "generated_tanpura_drone.wav"
_TRENDING_DIR   = MUSIC_DIR / "trending"
_TRENDING_CACHE = _TRENDING_DIR / "cache.json"
_CACHE_MAX_AGE_HOURS = 24
_DURATION_SECS = 210   # 3.5 min — long enough for any video
_SAMPLE_RATE = 44100


def _generate_tanpura_drone(output: Path) -> None:
    """
    Generate a warm tanpura-style devotional drone and save as WAV.
    Tuning: C3 (Sa) + G3 (Pa) + C4 (Sa) — classic Indian classical base.
    Includes slow LFO pulse (breathing effect) and gentle harmonics.
    """
    print("  Generating devotional background music (tanpura drone)…")
    t = np.linspace(0, _DURATION_SECS, _SAMPLE_RATE * _DURATION_SECS, endpoint=False)

    # Tanpura string frequencies (C3 tuning)
    sa_low  = 130.81   # C3 — bass Sa
    sa_mid  = 261.63   # C4 — mid Sa
    pa      = 196.00   # G3 — Pa (5th)
    sa_high = 523.25   # C5 — high Sa
    ga      = 329.63   # E4 — Ga (for warmth)

    # Layered harmonics — mimics tanpura resonance
    drone = (
        0.38 * np.sin(2 * np.pi * sa_low  * t) +
        0.28 * np.sin(2 * np.pi * sa_mid  * t) +
        0.22 * np.sin(2 * np.pi * pa      * t) +
        0.10 * np.sin(2 * np.pi * sa_high * t) +
        0.06 * np.sin(2 * np.pi * ga      * t) +
        # Subtle overtones for richness
        0.04 * np.sin(2 * np.pi * sa_low  * 3 * t) +
        0.03 * np.sin(2 * np.pi * pa      * 2 * t)
    )

    # Slow breathing LFO (0.20 Hz = 5-second pulse cycle)
    lfo = 0.78 + 0.22 * np.sin(2 * np.pi * 0.20 * t)
    drone = drone * lfo

    # Fade in (4s) and fade out (4s)
    fade = _SAMPLE_RATE * 4
    drone[:fade] *= np.linspace(0, 1, fade)
    drone[-fade:] *= np.linspace(1, 0, fade)

    # Normalise & convert to 16-bit PCM
    drone = (drone / np.max(np.abs(drone)) * 0.55 * 32767).astype(np.int16)

    # Stereo — duplicate mono to both channels for wider sound
    stereo = np.column_stack([drone, drone])

    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "w") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(_SAMPLE_RATE)
        wf.writeframes(stereo.tobytes())

    size_kb = output.stat().st_size // 1024
    print(f"  Tanpura drone ready → {output.name} ({size_kb} KB)")


def _is_cache_fresh() -> bool:
    if not _TRENDING_CACHE.exists():
        return False
    try:
        data = json.loads(_TRENDING_CACHE.read_text())
        cached_at = datetime.fromisoformat(data["cached_at"])
        age_hours = (datetime.now(timezone.utc) - cached_at).total_seconds() / 3600
        return age_hours < _CACHE_MAX_AGE_HOURS
    except Exception:
        return False


def _fetch_trending_ids(api_key: str, max_results: int = 5) -> list[dict]:
    """Fetch top trending music video IDs from YouTube Data API v3."""
    import requests
    resp = requests.get(
        "https://www.googleapis.com/youtube/v3/videos",
        params={
            "part": "snippet",
            "chart": "mostPopular",
            "videoCategoryId": "10",  # Music category
            "regionCode": "IN",
            "maxResults": max_results,
            "key": api_key,
        },
        timeout=10,
    )
    resp.raise_for_status()
    return [
        {"id": item["id"], "title": item["snippet"]["title"]}
        for item in resp.json().get("items", [])
    ]


def _download_audio(video_id: str, title: str) -> Path | None:
    """Download audio as MP3 via yt-dlp. Returns path or None on failure."""
    try:
        import yt_dlp
    except ImportError:
        print("  yt-dlp not installed — run: pip install yt-dlp")
        return None

    safe = re.sub(r"[^\w\s-]", "", title)[:50].strip()
    expected = _TRENDING_DIR / f"{safe}_{video_id}.mp3"
    if expected.exists():
        return expected

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": str(_TRENDING_DIR / f"{safe}_{video_id}.%(ext)s"),
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([f"https://www.youtube.com/watch?v={video_id}"])
        return expected if expected.exists() else None
    except Exception as e:
        print(f"  Warning: download failed for '{title[:40]}': {e}")
        return None


def _get_trending_music() -> Path | None:
    """
    Fetch top 5 trending music IDs, pick 1 randomly, download only that one.
    Cached locally for 24h (saves re-download on repeated local runs).
    Requires YOUTUBE_API_KEY in .env.
    """
    _TRENDING_DIR.mkdir(parents=True, exist_ok=True)

    # Use local cache if fresh (avoids re-download on same machine within 24h)
    if _is_cache_fresh():
        try:
            data = json.loads(_TRENDING_CACHE.read_text())
            cached_paths = [Path(p) for p in data.get("paths", []) if Path(p).exists()]
            if cached_paths:
                choice = random.choice(cached_paths)
                print(f"  Trending music (cached): {choice.stem[:55]}")
                return choice
        except Exception:
            pass

    # Fetch trending IDs, pick 1 at random, download only that one
    print("  Fetching trending YouTube music (Music chart, IN)…")
    try:
        tracks = _fetch_trending_ids(YOUTUBE_API_KEY)
    except Exception as e:
        print(f"  Warning: Could not fetch trending music: {e}")
        return None

    track = random.choice(tracks)
    print(f"  Selected: {track['title'][:55]}")
    path = _download_audio(track["id"], track["title"])
    if not path:
        return None

    _TRENDING_CACHE.write_text(json.dumps({
        "cached_at": datetime.now(timezone.utc).isoformat(),
        "paths": [str(path)],
    }))

    print(f"  Trending background music ready: {path.stem[:55]}")
    return path


def get_background_music() -> Path:
    """
    Return a background music file path.

    Priority:
      1. User-provided .mp3/.wav in assets/music/
      2. Trending YouTube music (auto-downloaded, refreshed every 24h, needs YOUTUBE_API_KEY)
      3. Auto-generated tanpura drone fallback
    """
    # 1. User-provided tracks (drop .mp3/.wav directly in assets/music/)
    user_files = [
        f for f in (list(MUSIC_DIR.glob("*.mp3")) + list(MUSIC_DIR.glob("*.wav")))
        if f.name != _GENERATED_PATH.name
    ]
    if user_files:
        choice = random.choice(user_files)
        print(f"  Background music: {choice.name}")
        return choice

    # 2. Trending YouTube music
    if YOUTUBE_API_KEY:
        trending = _get_trending_music()
        if trending:
            return trending
    else:
        print("  (Set YOUTUBE_API_KEY in .env to enable trending music)")

    # 3. Auto-generated tanpura drone fallback
    if not _GENERATED_PATH.exists():
        _generate_tanpura_drone(_GENERATED_PATH)
    else:
        print(f"  Background music: {_GENERATED_PATH.name} (cached)")

    return _GENERATED_PATH
