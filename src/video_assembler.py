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

from PIL import Image, ImageDraw, ImageFont

from config import (
    BG_MUSIC_VOLUME,
    OUTPUT_DIR,
    TEMP_DIR,
    VIDEO_WIDTH,
    VIDEO_HEIGHT,
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


# ── Hook overlay helpers ───────────────────────────────────────────────────────

def _load_font_va(size: int) -> ImageFont.FreeTypeFont:
    """Load Devanagari font with cross-platform fallbacks."""
    from config import ASSETS_DIR
    candidates = [
        str(ASSETS_DIR / "fonts" / "NotoSansDevanagari-Bold.ttf"),
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari[wdth,wght].ttf",
        "/System/Library/Fonts/Kohinoor.ttc",
        "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc",
        "/System/Library/Fonts/Supplemental/DevanagariMT.ttc",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, Exception):
            pass
    return ImageFont.load_default()


def _wrap_hook_va(text: str, max_chars: int = 13) -> list[str]:
    """Wrap hook text into short lines."""
    words = text.split()
    lines, current = [], ""
    for word in words:
        test = (current + " " + word).strip() if current else word
        if len(test) <= max_chars:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines[:3]


def _create_hook_png(hook_text: str, out: Path) -> bool:
    """
    Create a transparent PNG (1080×1920) with hook text panel.
    Returns True if PNG was created, False if skipped.
    """
    lines = _wrap_hook_va(hook_text)
    if not lines:
        return False

    w, h = VIDEO_WIDTH, VIDEO_HEIGHT
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    font_size = 88
    font = _load_font_va(font_size)
    line_gap = font_size + 20

    max_text_w = 0
    line_sizes = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        lw = bbox[2] - bbox[0]
        line_sizes.append(lw)
        max_text_w = max(max_text_w, lw)

    total_text_h = len(lines) * line_gap - (line_gap - font_size)
    pad_x, pad_y = 52, 32
    panel_w = min(max_text_w + pad_x * 2, w - 72)
    panel_h = total_text_h + pad_y * 2 + 12

    panel_x = (w - panel_w) // 2
    panel_y = int(h * 0.18)

    # Dark semi-transparent panel
    try:
        draw.rounded_rectangle(
            [(panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h)],
            radius=20, fill=(10, 10, 10, 200),
        )
    except AttributeError:
        draw.rectangle(
            [(panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h)],
            fill=(10, 10, 10, 200),
        )

    # Saffron accent lines
    draw.rectangle([(panel_x, panel_y), (panel_x + panel_w, panel_y + 7)], fill=(255, 153, 0, 255))
    draw.rectangle([(panel_x, panel_y + panel_h - 7), (panel_x + panel_w, panel_y + panel_h)], fill=(255, 153, 0, 255))

    # Text with drop-shadow
    y = panel_y + pad_y + 4
    for i, line in enumerate(lines):
        x = (w - line_sizes[i]) // 2
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 220))
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_gap

    img.save(out, "PNG")
    return True


def _overlay_hook(video: Path, hook_png: Path, out: Path) -> None:
    """Overlay hook PNG on the first 3 seconds of the video."""
    _run(
        [
            "ffmpeg", "-y",
            "-i", str(video),
            "-i", str(hook_png),
            "-filter_complex",
            "[0:v][1:v]overlay=0:0:enable='between(t,0,3)'[v]",
            "-map", "[v]",
            "-an",   # drop clip audio — final audio comes from mixed.aac
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
            "-pix_fmt", "yuv420p",
            str(out),
        ],
        step="hook-overlay",
    )


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
    hook_text: str = "",
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

    # ── 1b. Hook overlay on first 3 seconds ───────────────────────────────────
    if hook_text:
        hook_png = work / "hook_overlay.png"
        if _create_hook_png(hook_text, hook_png):
            hook_vid = work / "concat_hook.mp4"
            print(f'  Hook overlay applied: "{hook_text[:40]}..."')
            _overlay_hook(concat_vid, hook_png, hook_vid)
            concat_vid = hook_vid

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
