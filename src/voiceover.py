"""
Voiceover — edge-tts (free) with karaoke-style word-timed subtitles.

Returns both:
  - audio_path   : the MP3 voiceover
  - subtitle_path: an ASS subtitle file (4 words per line, timed to audio)

Animation per subtitle chunk:
  - Fast fade-in (120 ms)
  - Scale pop: 115% → 100% (snappy entrance)
  - Fast fade-out (60 ms)
  - Bold white text + thick black outline — readable on any image
"""

import asyncio
from pathlib import Path

import edge_tts

from config import VOICE, TEMP_DIR

# ── ASS style constants ───────────────────────────────────────────────────────
# Colors in ASS &HAABBGGRR format
_WHITE   = "&H00FFFFFF"
_BLACK   = "&H00000000"
_SHADOW  = "&HAA000000"   # semi-transparent black shadow
_WORDS_PER_LINE = 4

_ASS_HEADER = """\
[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
Collisions: Normal

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Noto Sans,82,{white},&H000000FF,{black},{shadow},1,0,0,0,100,100,2,0,1,5,2,2,50,50,260,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
""".format(white=_WHITE, black=_BLACK, shadow=_SHADOW)


def _to_ass_time(secs: float) -> str:
    """Convert seconds → ASS time format  H:MM:SS.cc (hundredths)."""
    h = int(secs // 3600)
    m = int((secs % 3600) // 60)
    s = secs % 60
    return f"{h}:{m:02d}:{s:05.2f}"


def _build_ass(word_events: list[dict]) -> str:
    """Group word events into 4-word chunks and build ASS subtitle content."""
    lines = [_ASS_HEADER]

    for i in range(0, len(word_events), _WORDS_PER_LINE):
        chunk = word_events[i : i + _WORDS_PER_LINE]
        start = chunk[0]["start"]

        # End = last word's end, but don't overlap with next chunk's start
        end = chunk[-1]["end"]
        if i + _WORDS_PER_LINE < len(word_events):
            next_start = word_events[i + _WORDS_PER_LINE]["start"]
            end = min(end + 0.05, next_start - 0.02)

        text = " ".join(w["word"] for w in chunk)
        # Escape braces that aren't ASS override tags
        text = text.replace("\\", "\\\\")

        # Animation: fade-in 120ms + scale pop 115→100% + fade-out 60ms
        anim = r"{\fad(120,60)\t(0,180,\fscx115\fscy115)\t(180,320,\fscx100\fscy100)}"

        t_start = _to_ass_time(start)
        t_end   = _to_ass_time(end)
        lines.append(f"Dialogue: 0,{t_start},{t_end},Default,,0,0,0,,{anim}{text}")

    return "\n".join(lines) + "\n"


async def _stream_tts(
    text: str, audio_path: Path, voice: str
) -> list[dict]:
    """
    Stream TTS audio to file while collecting WordBoundary events.
    Returns list of {word, start, end} dicts (times in seconds).
    """
    communicate = edge_tts.Communicate(text, voice, boundary="WordBoundary")
    word_events: list[dict] = []

    with open(audio_path, "wb") as f:
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                f.write(chunk["data"])
            elif chunk["type"] == "WordBoundary":
                start    = chunk["offset"]   / 10_000_000   # 100ns → seconds
                duration = chunk["duration"] / 10_000_000
                word_events.append({
                    "word":  chunk["text"],
                    "start": start,
                    "end":   start + duration,
                })

    return word_events


def generate_voiceover(
    script: str, run_id: str, voice: str = VOICE
) -> tuple[Path, Path]:
    """
    Generate voiceover + timed subtitle file.
    Returns (audio_path, subtitle_path).
    """
    audio_dir = TEMP_DIR / run_id / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)

    audio_path    = audio_dir / "voiceover.mp3"
    subtitle_path = audio_dir / "subtitles.ass"

    word_events = asyncio.run(_stream_tts(script, audio_path, voice))

    if word_events:
        ass_content = _build_ass(word_events)
        subtitle_path.write_text(ass_content, encoding="utf-8")
        print(f"  Voiceover: {audio_path.name}  |  {len(word_events)} words → {len(word_events) // _WORDS_PER_LINE + 1} subtitle lines")
    else:
        # No word boundaries returned — write empty subtitle file
        subtitle_path.write_text(_ASS_HEADER, encoding="utf-8")
        print(f"  Voiceover saved (no word timings available)")

    return audio_path, subtitle_path
