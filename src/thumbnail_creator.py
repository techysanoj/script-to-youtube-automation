"""
Thumbnail Creator — builds a YouTube Shorts thumbnail from the deity image.

Design:
  - Deity stock photo (image_paths[0]) as full background
  - Dark gradient overlay (top + bottom) for text contrast
  - Saffron border frame
  - Bold Hindi title text (Noto Sans Devanagari Bold) with black stroke
  - Red #Shorts badge (top-right corner)

Font required:
  Place NotoSansDevanagari-Bold.ttf in assets/fonts/
  Download free from: https://fonts.google.com/noto/specimen/Noto+Sans+Devanagari
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

from config import VIDEO_WIDTH, VIDEO_HEIGHT, TEMP_DIR, ASSETS_DIR

_FONT_PATH = ASSETS_DIR / "fonts" / "NotoSansDevanagari-Bold.ttf"


def _get_font(size: int) -> ImageFont.FreeTypeFont:
    """
    Load Noto Sans Devanagari Bold for correct Hindi rendering.

    Search order:
      1. assets/fonts/NotoSansDevanagari-Bold.ttf  (committed to repo / local dev)
      2. Ubuntu system path (GitHub Actions — installed via fonts-noto-extra apt package)
      3. macOS system fonts (local dev fallback)
      4. Pillow default (last resort — Devanagari will NOT render correctly)
    """
    candidates = [
        # 1. Repo-local font (works everywhere if committed)
        str(_FONT_PATH),
        # 2. Ubuntu / GitHub Actions — fonts-noto-extra apt package
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSansDevanagari[wdth,wght].ttf",
        "/usr/share/fonts/opentype/noto/NotoSansDevanagari-Bold.otf",
        # 3. macOS fallbacks (Latin only — Devanagari won't render)
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        # 4. Linux generic bold fallback
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    ]
    for path in candidates:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, Exception):
            pass
    return ImageFont.load_default()


def _wrap_title(title: str, max_chars: int = 14) -> list[str]:
    """
    Strip hashtags and wrap Hindi title into short lines.
    Devanagari chars are wide — keep max_chars low (12-16).
    """
    # Remove hashtags and trailing whitespace
    clean = title.split("#")[0].strip()

    words = clean.split()
    lines: list[str] = []
    current = ""

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

    return lines if lines else [clean[:max_chars]]


def _draw_gradient_overlay(img: Image.Image) -> Image.Image:
    """Add dark gradient at top (subtle) and bottom (strong) for text readability."""
    overlay = Image.new("RGBA", (VIDEO_WIDTH, VIDEO_HEIGHT), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Bottom gradient — covers lower 55% where title sits
    grad_h = int(VIDEO_HEIGHT * 0.55)
    for y in range(grad_h):
        # Exponential ramp: dark at bottom, transparent at top of gradient
        alpha = int(210 * (y / grad_h) ** 1.6)
        screen_y = VIDEO_HEIGHT - grad_h + y
        draw.line([(0, screen_y), (VIDEO_WIDTH, screen_y)], fill=(0, 0, 0, alpha))

    # Top gradient — subtle, covers top 12%
    top_h = int(VIDEO_HEIGHT * 0.12)
    for y in range(top_h):
        alpha = int(130 * (1 - y / top_h))
        draw.line([(0, y), (VIDEO_WIDTH, y)], fill=(0, 0, 0, alpha))

    return Image.alpha_composite(img.convert("RGBA"), overlay)


def _draw_saffron_border(draw: ImageDraw.Draw) -> None:
    """Draw a saffron (#FF9900) rectangular border frame."""
    margin = 20
    draw.rectangle(
        [(margin, margin), (VIDEO_WIDTH - margin, VIDEO_HEIGHT - margin)],
        outline=(255, 153, 0),   # saffron
        width=7,
    )
    # Inner thin gold line for depth
    inner = margin + 12
    draw.rectangle(
        [(inner, inner), (VIDEO_WIDTH - inner, VIDEO_HEIGHT - inner)],
        outline=(255, 215, 0),   # gold
        width=2,
    )


def _draw_title_text(draw: ImageDraw.Draw, lines: list[str]) -> None:
    """
    Draw a colored background panel behind the title, then render white text on top.

    Panel color scheme (bhakti style):
      - Background : deep maroon  rgba(90, 0, 15, 225)   — rich devotional red
      - Top accent  : saffron     rgb(255, 153, 0)        — 4 px line above panel
      - Text fill   : pure white  rgb(255, 255, 255)
      - Text shadow : black, 3 px offset
    """
    font_size = 96 if len(lines) <= 2 else 78
    font = _get_font(font_size)
    line_gap = font_size + 24

    pad_x = 48   # horizontal padding inside the panel
    pad_y = 28   # vertical padding inside the panel
    panel_margin = 36  # gap from left/right edge of thumbnail

    # ── measure the widest line ────────────────────────────────────────────────
    max_text_w = 0
    line_bboxes = []
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font)
        w = bbox[2] - bbox[0]
        line_bboxes.append((w, bbox))
        max_text_w = max(max_text_w, w)

    total_text_h = len(lines) * line_gap - (line_gap - font_size)  # remove trailing gap
    panel_w = min(max_text_w + pad_x * 2, VIDEO_WIDTH - panel_margin * 2)
    panel_h = total_text_h + pad_y * 2

    panel_x = (VIDEO_WIDTH - panel_w) // 2
    panel_y = VIDEO_HEIGHT - panel_h - 100   # 100 px from bottom edge

    # ── background panel (deep maroon, semi-transparent) ─────────────────────
    panel_rect = [(panel_x, panel_y), (panel_x + panel_w, panel_y + panel_h)]
    try:
        draw.rounded_rectangle(panel_rect, radius=18, fill=(90, 0, 15, 225))
    except AttributeError:
        draw.rectangle(panel_rect, fill=(90, 0, 15, 225))

    # ── saffron accent line on top of panel ───────────────────────────────────
    draw.rectangle(
        [(panel_x, panel_y), (panel_x + panel_w, panel_y + 6)],
        fill=(255, 153, 0),
    )
    # Matching accent line at bottom
    draw.rectangle(
        [(panel_x, panel_y + panel_h - 6), (panel_x + panel_w, panel_y + panel_h)],
        fill=(255, 153, 0),
    )

    # ── text lines (white with black drop-shadow) ─────────────────────────────
    y = panel_y + pad_y
    for i, line in enumerate(lines):
        text_w = line_bboxes[i][0]
        x = (VIDEO_WIDTH - text_w) // 2

        # Black drop-shadow (offset 3 px down-right)
        draw.text((x + 3, y + 3), line, font=font, fill=(0, 0, 0, 200))

        # White text on top
        draw.text((x, y), line, font=font, fill=(255, 255, 255, 255))
        y += line_gap


def _draw_shorts_badge(draw: ImageDraw.Draw) -> None:
    """Red #Shorts pill badge in the top-right corner."""
    font = _get_font(46)
    text = "#Shorts"
    bbox = draw.textbbox((0, 0), text, font=font)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]

    pad_x, pad_y = 18, 10
    bx = VIDEO_WIDTH - tw - pad_x * 2 - 38
    by = 48

    # Red pill background
    rect = [(bx, by), (bx + tw + pad_x * 2, by + th + pad_y * 2)]
    try:
        draw.rounded_rectangle(rect, radius=22, fill=(220, 0, 0))
    except AttributeError:
        # Pillow < 8.2 fallback
        draw.rectangle(rect, fill=(220, 0, 0))

    draw.text((bx + pad_x, by + pad_y), text, font=font, fill=(255, 255, 255))


def create_thumbnail(deity_image_path: Path, title: str, run_id: str) -> Path:
    """
    Build a YouTube Shorts thumbnail from the deity stock photo.

    Args:
        deity_image_path: Path to the first fetched image (deity photo).
        title:            Video title in Hindi Devanagari (hashtags stripped automatically).
        run_id:           Pipeline run ID used to place the file in the correct temp folder.

    Returns:
        Path to the saved thumbnail JPEG (1080 × 1920).
    """
    if not _FONT_PATH.exists():
        print(
            f"\n  [WARN] Devanagari font not found at {_FONT_PATH}\n"
            "         Hindi text will not render correctly.\n"
            "         Download NotoSansDevanagari-Bold.ttf from Google Fonts\n"
            "         and place it in assets/fonts/\n"
        )

    # 1. Load + resize deity image to portrait 1080×1920
    img = Image.open(deity_image_path).convert("RGB")
    img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)

    # 2. Dark gradient overlay
    img = _draw_gradient_overlay(img)

    # 3. Draw on top of the composited image
    draw = ImageDraw.Draw(img)

    _draw_saffron_border(draw)

    lines = _wrap_title(title, max_chars=14)
    _draw_title_text(draw, lines)

    _draw_shorts_badge(draw)

    # 4. Save
    out_dir = TEMP_DIR / run_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "thumbnail.jpg"
    img.convert("RGB").save(out_path, "JPEG", quality=95)
    print(f"  Thumbnail → {out_path.name}  ({len(lines)} title line(s))")
    return out_path
