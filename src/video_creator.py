"""
Video Creator — assembles the final YouTube Short using FFmpeg + Pillow.
No MoviePy dependency; everything goes through subprocess FFmpeg calls.

Pipeline per video:
  1. Resize each image to 1080×1920
  2. Apply Ken Burns (zoompan) effect via FFmpeg — alternating zoom-in / zoom-out
  3. Concatenate all image clips
  4. Mix voiceover + background music (ducked to 15%)
  5. Burn a caption (first sentence) onto the bottom of the video
  6. Add fade-in / fade-out
  7. Write final MP4
"""

import json
import subprocess
from pathlib import Path

from PIL import Image

from config import (
    VIDEO_FPS,
    VIDEO_HEIGHT,
    VIDEO_WIDTH,
    BG_MUSIC_VOLUME,
    TEMP_DIR,
    OUTPUT_DIR,
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def _ffprobe_duration(path: Path) -> float:
    """Return the duration of a media file in seconds."""
    result = subprocess.run(
        [
            "ffprobe", "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            str(path),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def _run(cmd: list, step: str, cwd: Path | None = None) -> None:
    """Run an FFmpeg command; raise with context on failure."""
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed at [{step}]:\n{result.stderr[-1000:]}")


# ── Step 1 — resize image ─────────────────────────────────────────────────────

def _resize_image(src: Path, dst: Path) -> None:
    img = Image.open(src).convert("RGB")
    img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)
    img.save(dst, "JPEG", quality=95)


# ── Step 2 — Ken Burns clip ───────────────────────────────────────────────────

def _make_clip(img_path: Path, duration: float, out: Path, direction: str) -> None:
    """
    Create a short MP4 clip from one image with Ken Burns zoom effect.
    direction = "in"  → zoom from 1.0x to 1.3x  (slow push-in)
    direction = "out" → zoom from 1.3x to 1.0x  (slow pull-back)
    """
    frames = int(duration * VIDEO_FPS)
    rate = 0.3 / frames  # total zoom range 0.3 spread over all frames

    if direction == "in":
        # Start at 1.0, increment each frame
        zoom_expr = f"min(zoom+{rate:.8f},1.3)"
    else:
        # Start at 1.3, decrement each frame
        zoom_expr = f"if(eq(on\\,1)\\,1.3\\,max(zoom-{rate:.8f}\\,1.0))"

    zoompan = (
        f"scale={VIDEO_WIDTH * 2}:{VIDEO_HEIGHT * 2},"
        f"zoompan=z='{zoom_expr}'"
        f":d={frames}"
        f":x='iw/2-(iw/zoom/2)'"
        f":y='ih/2-(ih/zoom/2)'"
        f":s={VIDEO_WIDTH}x{VIDEO_HEIGHT},"
        f"setsar=1"
    )

    _run(
        [
            "ffmpeg", "-y",
            "-loop", "1",
            "-i", str(img_path),
            "-vf", zoompan,
            "-t", str(duration),
            "-r", str(VIDEO_FPS),
            "-pix_fmt", "yuv420p",
            "-c:v", "libx264",
            "-preset", "veryfast",
            "-tune", "stillimage",
            str(out),
        ],
        step=f"ken-burns {img_path.name}",
    )


# ── Step 3 — concatenate clips ────────────────────────────────────────────────

def _concat_clips(clip_paths: list[Path], out: Path) -> None:
    concat_txt = out.parent / "concat_list.txt"
    concat_txt.write_text(
        "\n".join(f"file '{p.resolve()}'" for p in clip_paths)
    )
    _run(
        [
            "ffmpeg", "-y",
            "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", "medium",
            str(out),
        ],
        step="concat",
    )
    concat_txt.unlink(missing_ok=True)


# ── Step 4 — mix audio ────────────────────────────────────────────────────────

def _mix_audio(vo: Path, music: Path | None, duration: float, out: Path) -> None:
    if music is None:
        _run(
            ["ffmpeg", "-y", "-i", str(vo), "-c:a", "aac", "-b:a", "128k", str(out)],
            step="audio-copy",
        )
        return

    _run(
        [
            "ffmpeg", "-y",
            "-i", str(vo),
            "-stream_loop", "-1", "-i", str(music),
            "-filter_complex",
            (
                f"[1:a]volume={BG_MUSIC_VOLUME},"
                f"atrim=0:{duration:.3f}[bg];"
                "[0:a][bg]amix=inputs=2:duration=first[out]"
            ),
            "-map", "[out]",
            "-c:a", "aac", "-b:a", "128k",
            str(out),
        ],
        step="audio-mix",
    )


# ── Step 5 — burn ASS karaoke subtitles ──────────────────────────────────────

def _burn_subtitles(video: Path, subtitle_path: Path, audio: Path, out: Path) -> None:
    """
    Burn an ASS subtitle file onto the video using FFmpeg's subtitles filter.
    The subtitle file contains 4-word timed chunks with fade+pop animation.
    """
    import shutil
    # Copy ASS to work dir with a simple name — FFmpeg resolves it relative to cwd
    safe_ass = video.parent / "subs.ass"
    shutil.copy(subtitle_path, safe_ass)

    _run(
        [
            "ffmpeg", "-y",
            "-i", str(video),
            "-i", str(audio),
            "-filter_complex", "[0:v]subtitles=subs.ass[v]",
            "-map", "[v]",
            "-map", "1:a",
            "-c:v", "libx264", "-preset", "medium", "-crf", "23",
            "-c:a", "aac", "-b:a", "128k",
            "-pix_fmt", "yuv420p",
            "-shortest",
            str(out),
        ],
        step="subtitle-burn",
        cwd=video.parent,   # FFmpeg resolves subs.ass relative to this directory
    )


# ── Public API ────────────────────────────────────────────────────────────────

def create_video(
    image_paths: list[Path],
    voiceover_path: Path,
    subtitle_path: Path,
    bg_music: Path,
    run_id: str,
    video_index: int,
) -> Path:
    """
    Full pipeline: images + voiceover + karaoke subtitles + music → final MP4.
    Returns the path to the output video.
    """
    work = TEMP_DIR / run_id / "video"
    work.mkdir(parents=True, exist_ok=True)

    # ── 0. Measure voiceover duration ─────────────────────────────────────────
    vo_duration = _ffprobe_duration(voiceover_path)
    per_img = max(vo_duration / len(image_paths), 3.0)
    print(f"  Voiceover: {vo_duration:.1f}s  |  {len(image_paths)} images × {per_img:.1f}s each")

    # ── 1 & 2. Resize + Ken Burns for each image ──────────────────────────────
    clip_paths = []
    directions = ["in", "out"] * (len(image_paths) // 2 + 1)
    for i, src in enumerate(image_paths):
        resized = work / f"resized_{i:02d}.jpg"
        _resize_image(src, resized)
        clip = work / f"clip_{i:02d}.mp4"
        print(f"  Ken Burns clip {i + 1}/{len(image_paths)}…")
        _make_clip(resized, per_img, clip, directions[i])
        clip_paths.append(clip)

    # ── 3. Concatenate ────────────────────────────────────────────────────────
    print("  Concatenating clips…")
    concat_vid = work / "concat.mp4"
    _concat_clips(clip_paths, concat_vid)

    # ── 4. Mix audio ──────────────────────────────────────────────────────────
    print("  Mixing audio…")
    mixed_audio = work / "mixed.aac"
    _mix_audio(voiceover_path, bg_music, vo_duration, mixed_audio)

    # ── 5. Burn karaoke subtitles + final output ───────────────────────────────
    print("  Burning karaoke subtitles…")
    output_path = OUTPUT_DIR / f"short_{run_id}_{video_index}.mp4"
    _burn_subtitles(concat_vid, subtitle_path, mixed_audio, output_path)

    print(f"  Video ready → {output_path.name}")
    return output_path
