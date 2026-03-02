"""
Audio Manager — provides background music for videos.

Priority order:
  1. Any .mp3 / .wav file in assets/music/  (user-provided real tracks)
  2. Auto-generated tanpura drone (devotional ambient, created once & cached)

The auto-generated track is a warm Indian tanpura drone with Sa-Pa-Sa tuning —
perfect for Hindu devotional / motivational Shorts. No downloads, no internet needed.
"""

import random
import wave
from pathlib import Path

import numpy as np

from config import MUSIC_DIR

_GENERATED_PATH = MUSIC_DIR / "generated_tanpura_drone.wav"
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


def get_background_music() -> Path:
    """
    Return a background music file path.
    Uses user-provided tracks first; falls back to auto-generated drone.
    """
    # User-provided tracks take priority (drop .mp3/.wav in assets/music/)
    user_files = [
        f for f in (list(MUSIC_DIR.glob("*.mp3")) + list(MUSIC_DIR.glob("*.wav")))
        if f.name != _GENERATED_PATH.name
    ]
    if user_files:
        choice = random.choice(user_files)
        print(f"  Background music: {choice.name}")
        return choice

    # Auto-generate if not already cached
    if not _GENERATED_PATH.exists():
        _generate_tanpura_drone(_GENERATED_PATH)
    else:
        print(f"  Background music: {_GENERATED_PATH.name} (cached)")

    return _GENERATED_PATH
