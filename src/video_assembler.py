"""
Video Assembler (clip-based) — assembles the final YouTube Short from real video clips.

Pipeline:
  1. Concatenate pre-cropped, pre-trimmed video clips (already 1080×1920, exact duration)
  2. Mix voiceover + background music (music ducked under voice)
  3. Burn karaoke ASS subtitles
  4. Write final MP4

No Ken Burns needed — the real video clips provide their own motion.
"""

import json
import subprocess
import shutil
from pathlib import Path

from config import (
    BG_MUSIC_VOLUME,
    OUTPUT_DIR,
    TEMP_DIR,
)


# ── Helpers ────────────────────────────────────────────────────────────────────

def _run(cmd: list, step: str, cwd: Path | None = None) -> None:
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg failed at [{step}]:\n{result.stderr[-1000:]}")


def _ffprobe_duration(path: Path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


# ── Step 1 — concatenate clips ─────────────────────────────────────────────────

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


# ── Step 2 — mix audio ────────────────────────────────────────────────────────

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


# ── Step 3 — burn karaoke subtitles ───────────────────────────────────────────

def _burn_subtitles(video: Path, subtitle_path: Path, audio: Path, out: Path) -> None:
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
        cwd=video.parent,
    )


# ── Public API ─────────────────────────────────────────────────────────────────

def assemble_video_from_clips(
    clip_paths: list[Path],
    voiceover_path: Path,
    subtitle_path: Path,
    bg_music: Path | None,
    run_id: str,
    video_index: int,
) -> Path:
    """
    Full assembly pipeline: video clips + voiceover + karaoke subtitles + music → MP4.
    Returns the path to the output video.
    """
    work = TEMP_DIR / run_id / "video"
    work.mkdir(parents=True, exist_ok=True)

    vo_duration = _ffprobe_duration(voiceover_path)
    total_clip_dur = sum(_ffprobe_duration(c) for c in clip_paths)
    print(f"  Voiceover: {vo_duration:.1f}s  |  Total clips: {total_clip_dur:.1f}s  |  {len(clip_paths)} clips")

    # ── 1. Concatenate clips ───────────────────────────────────────────────────
    print("  Concatenating clips…")
    concat_vid = work / "concat.mp4"
    _concat_clips(clip_paths, concat_vid)

    # ── 2. Mix audio ──────────────────────────────────────────────────────────
    print("  Mixing audio…")
    mixed_audio = work / "mixed.aac"
    _mix_audio(voiceover_path, bg_music, vo_duration, mixed_audio)

    # ── 3. Burn karaoke subtitles + final output ───────────────────────────────
    print("  Burning karaoke subtitles…")
    output_path = OUTPUT_DIR / f"short_video_{run_id}_{video_index}.mp4"
    _burn_subtitles(concat_vid, subtitle_path, mixed_audio, output_path)

    print(f"  Video ready → {output_path.name}")
    return output_path
