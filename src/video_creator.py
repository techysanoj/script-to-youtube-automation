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

from PIL import Image, ImageDraw, ImageFont

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


# ── Step 1b — Hook text overlay on first frame ────────────────────────────────

def _load_font(size: int) -> ImageFont.FreeTypeFont:
    """Load Noto Sans Devanagari Bold; fall back to system Devanagari fonts."""
    from config import ASSETS_DIR
    candidates = [
        # 1. Local downloaded font (run scripts/setup_fonts.py once)
        str(ASSETS_DIR / "fonts" / "NotoSansDevanagari-Bold.ttf"),
        # 2. Ubuntu / GitHub Actions (fonts-noto-extra apt package)
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari[wdth,wght].ttf",
        # 3. macOS built-in Devanagari fonts (no download needed)
        "/System/Library/Fonts/Kohinoor.ttc",            # Kohinoor Devanagari Bold
        "/System/Library/Fonts/Supplemental/ITFDevanagari.ttc",
        "/System/Library/Fonts/Supplemental/DevanagariMT.ttc",
        # 4. Generic Latin fallback (Devanagari won't render, but won't crash)
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, Exception):
            pass
    return ImageFont.load_default()


def _wrap_hook(text: str, max_chars: int = 13) -> list[str]:
    """Wrap hook text into short lines (Devanagari chars are wide)."""
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
    return lines[:3]  # max 3 lines to keep it punchy


def _add_hook_overlay(img_path: Path, hook_text: str, out: Path) -> None:
    """
    Burn the hook sentence onto the first frame as a bold text overlay.
    Placed in the upper-center area so it's the very first thing viewers read.

    Layout:
      - Subtle dark tint over the whole image (improves text contrast)
      - Saffron top accent line
      - Dark semi-transparent rounded panel (center-top)
      - White bold Devanagari text with black drop-shadow
      - Saffron bottom accent line
    """
    img = Image.open(img_path).convert("RGBA")
    w, h = img.size  # 1080 × 1920

    # ── 1. Subtle full-image dark tint ────────────────────────────────────────
    tint = Image.new("RGBA", (w, h), (0, 0, 0, 90))
    img = Image.alpha_composite(img, tint)

    draw = ImageDraw.Draw(img)

    font_size = 88
    font = _load_font(font_size)
    line_gap = font_size + 20

    lines = _wrap_hook(hook_text)
    if not lines:
        img.convert("RGB").save(out, "JPEG", quality=95)
        return

    # ── 2. Measure text block ─────────────────────────────────────────────────
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
    panel_h = total_text_h + pad_y * 2 + 12   # +12 for accent lines

    # ── 3. Position: upper-center (~18% from top) ─────────────────────────────
    panel_x = (w - panel_w) // 2
    panel_y = int(h * 0.18)

    # ── 4. Draw dark rounded panel ────────────────────────────────────────────
    panel_rect = [(panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h)]
    panel_overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    panel_draw = ImageDraw.Draw(panel_overlay)
    try:
        panel_draw.rounded_rectangle(panel_rect, radius=20, fill=(10, 10, 10, 200))
    except AttributeError:
        panel_draw.rectangle(panel_rect, fill=(10, 10, 10, 200))
    img = Image.alpha_composite(img, panel_overlay)
    draw = ImageDraw.Draw(img)

    # ── 5. Saffron accent lines (top + bottom of panel) ───────────────────────
    draw.rectangle(
        [(panel_x, panel_y), (panel_x + panel_w, panel_y + 7)],
        fill=(255, 153, 0),    # saffron
    )
    draw.rectangle(
        [(panel_x, panel_y + panel_h - 7), (panel_x + panel_w, panel_y + panel_h)],
        fill=(255, 153, 0),
    )

    # ── 6. Draw text lines ────────────────────────────────────────────────────
    y = panel_y + pad_y + 4
    for i, line in enumerate(lines):
        x = (w - line_sizes[i]) // 2
        # Black drop-shadow
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 220))
        # White text
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_gap

    img.convert("RGB").save(out, "JPEG", quality=95)


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
    from config import ASSETS_DIR

    # Copy ASS to work dir with a simple name — FFmpeg resolves it relative to cwd
    safe_ass = video.parent / "subs.ass"
    shutil.copy(subtitle_path, safe_ass)

    # Use local assets/fonts if NotoSansDevanagari-Bold.ttf was downloaded there
    # (run scripts/setup_fonts.py once to download it).
    # On GitHub Actions, fonts-noto-extra is installed system-wide so no fontsdir needed.
    font_file = ASSETS_DIR / "fonts" / "NotoSansDevanagari-Bold.ttf"
    if font_file.exists():
        sub_filter = f"subtitles=subs.ass:fontsdir={font_file.parent}"
    else:
        sub_filter = "subtitles=subs.ass"  # rely on system fontconfig (GitHub Actions)

    _run(
        [
            "ffmpeg", "-y",
            "-i", str(video),
            "-i", str(audio),
            "-filter_complex", f"[0:v]{sub_filter}[v]",
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
    hook_text: str = "",
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

        # First frame: burn hook text overlay so viewers see the hook instantly
        if i == 0 and hook_text:
            hook_frame = work / "hook_frame.jpg"
            _add_hook_overlay(resized, hook_text, hook_frame)
            frame_src = hook_frame
            print(f"  Hook overlay applied to frame 1: "{hook_text[:40]}…"")
        else:
            frame_src = resized

        clip = work / f"clip_{i:02d}.mp4"
        print(f"  Ken Burns clip {i + 1}/{len(image_paths)}…")
        _make_clip(frame_src, per_img, clip, directions[i])
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
