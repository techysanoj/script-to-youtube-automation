"""
main_video.py — YouTube Shorts Automation (Video Clip Pipeline)

Runs the full pipeline VIDEOS_PER_RUN times using real video clips instead of images:
  Gemini script → edge-tts voiceover → Pexels/Pixabay clips → FFmpeg → YouTube upload

KEY DIFFERENCE from main.py (photo pipeline):
  Voiceover is generated BEFORE fetching clips so we know the exact duration.
  Each clip is downloaded and trimmed to: vo_duration / CLIPS_PER_VIDEO seconds.
  Total clip duration = voiceover duration — every frame is used, nothing wasted.

Steps:
  1 = Script generation
  2 = Voiceover + subtitles       ← moved before video fetch (needs duration)
  3 = Background music
  4 = Video clip fetching          ← clips trimmed to exact per-clip duration
  5 = Video assembly
  6 = YouTube upload (default)

Usage:
  python main_video.py              # full pipeline
  python main_video.py --steps 5   # stop after assembly (skip upload)
"""

import argparse
import json
import re
import shutil
import subprocess
import time
from datetime import datetime, timezone

from config import VIDEOS_PER_RUN, TEMP_DIR, YOUTUBE_VIDEOS_DIR
from src.script_generator import generate_video_content
from src.voiceover import generate_voiceover
from src.audio_manager import get_background_music
from src.video_fetcher import fetch_all_video_clips
from src.video_assembler import assemble_video_from_clips
from src.youtube_uploader import upload_video


def _probe_duration(path) -> float:
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", str(path)],
        capture_output=True, text=True, check=True,
    )
    return float(json.loads(result.stdout)["format"]["duration"])


def run_pipeline(video_index: int, stop_after: int = 6) -> dict:
    """Execute the video-clip pipeline for one Short up to `stop_after` step."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"vid_{ts}_{video_index}"

    sep = "=" * 56
    print(f"\n{sep}")
    print(f"  Video {video_index + 1}/{VIDEOS_PER_RUN}  [VIDEO mode]  (run_id: {run_id})")
    if stop_after < 6:
        print(f"  Stopping after step {stop_after}")
    print(sep)

    try:
        # ── 1. Script ─────────────────────────────────────────────────────────
        print("\n[1/6] Generating script (Gemini 2.5 Flash)…")
        content = generate_video_content()
        print(f"  Title  : {content['title'][:72]}")
        print(f"  Script : {content['script'][:90]}…")
        if stop_after == 1:
            print("\n  Stopped after step 1 (script).")
            return {"run_id": run_id, "stopped_at": 1, "title": content["title"]}

        # ── 2. Voiceover — BEFORE video fetch so we know exact clip duration ──
        print("\n[2/6] Generating voiceover + subtitles (edge-tts)…")
        voiceover_path, subtitle_path = generate_voiceover(content["script"], run_id)
        vo_duration = _probe_duration(voiceover_path)
        print(f"  Voiceover duration: {vo_duration:.1f}s")
        if stop_after == 2:
            print("\n  Stopped after step 2 (voiceover).")
            return {"run_id": run_id, "stopped_at": 2, "title": content["title"]}

        # ── 3. Background music ───────────────────────────────────────────────
        print("\n[3/6] Selecting background music…")
        bg_music = get_background_music()
        if stop_after == 3:
            print("\n  Stopped after step 3 (music).")
            return {"run_id": run_id, "stopped_at": 3, "title": content["title"]}

        # ── 4. Fetch video clips (duration-matched to voiceover) ──────────────
        print(f"\n[4/6] Fetching video clips ({len(content['search_terms'])} search terms)…")
        clip_paths = fetch_all_video_clips(
            search_terms=content["search_terms"],
            run_id=run_id,
            vo_duration=vo_duration,
        )
        if not clip_paths:
            raise RuntimeError("Video clip fetching returned no usable files.")
        print(f"  {len(clip_paths)} clips ready.")
        if stop_after == 4:
            print("\n  Stopped after step 4 (clips).")
            return {"run_id": run_id, "stopped_at": 4, "title": content["title"]}

        # ── 5. Assemble video ─────────────────────────────────────────────────
        print("\n[5/6] Assembling video (FFmpeg)…")
        video_path = assemble_video_from_clips(
            clip_paths=clip_paths,
            voiceover_path=voiceover_path,
            subtitle_path=subtitle_path,
            bg_music=bg_music,
            run_id=run_id,
            video_index=video_index,
        )
        if stop_after == 5:
            safe_title = re.sub(r"[^\w\s-]", "", content["title"])[:60].strip()
            safe_title = re.sub(r"\s+", "_", safe_title)
            dest_video = YOUTUBE_VIDEOS_DIR / f"{safe_title}_{run_id}.mp4"
            dest_txt   = YOUTUBE_VIDEOS_DIR / f"{safe_title}_{run_id}.txt"

            shutil.copy2(video_path, dest_video)

            txt_content = (
                f"TITLE:\n{content['title']}\n\n"
                f"DESCRIPTION:\n{content['description']}\n\n"
                f"TAGS:\n{', '.join(content['tags'])}\n"
            )
            dest_txt.write_text(txt_content, encoding="utf-8")

            print(f"\n  Video   → {dest_video}")
            print(f"  Metadata→ {dest_txt}")
            return {
                "run_id": run_id,
                "stopped_at": 5,
                "title": content["title"],
                "video_path": str(dest_video),
                "txt_path": str(dest_txt),
            }

        # ── 6. Upload ─────────────────────────────────────────────────────────
        print("\n[6/6] Uploading to YouTube…")
        video_id = upload_video(
            video_path=video_path,
            title=content["title"],
            description=content["description"],
            tags=content["tags"],
        )

        return {
            "run_id": run_id,
            "video_id": video_id,
            "title": content["title"],
            "url": f"https://www.youtube.com/shorts/{video_id}",
        }

    finally:
        if stop_after >= 6:
            run_temp = TEMP_DIR / run_id
            if run_temp.exists():
                shutil.rmtree(run_temp, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="YouTube Shorts Automation Pipeline (Video Clips)"
    )
    parser.add_argument(
        "--steps", type=int, default=6, choices=range(1, 7), metavar="N",
        help="Stop after step N (1=script, 2=voiceover, 3=music, 4=clips, 5=video, 6=upload). Default: 6",
    )
    args = parser.parse_args()

    start = datetime.now(timezone.utc)
    print(f"\nYouTube Shorts Automation [VIDEO MODE] — {start.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Scheduled videos: {VIDEOS_PER_RUN}  |  Running up to step {args.steps}/6")

    results, failures = [], []

    for i in range(VIDEOS_PER_RUN):
        try:
            result = run_pipeline(i, stop_after=args.steps)
            results.append(result)
        except Exception as exc:
            print(f"\n[ERROR] Video {i + 1} failed: {exc}")
            failures.append({"index": i + 1, "error": str(exc)})

        if i < VIDEOS_PER_RUN - 1:
            print("\nPausing 15 s before next video…")
            time.sleep(15)

    elapsed = (datetime.now(timezone.utc) - start).seconds // 60
    print(f"\n{'=' * 56}")
    if args.steps == 6:
        print(f"DONE — {len(results)}/{VIDEOS_PER_RUN} videos uploaded in ~{elapsed} min")
        for r in results:
            if "url" in r:
                print(f"  ✓ {r['title'][:60]}")
                print(f"    {r['url']}")
    else:
        print(f"DONE — {len(results)}/{VIDEOS_PER_RUN} videos processed (stopped at step {args.steps}) in ~{elapsed} min")
        for r in results:
            print(f"  ✓ {r['title'][:60]}")
            if "video_path" in r:
                print(f"    Video   : {r['video_path']}")
            if "txt_path" in r:
                print(f"    Metadata: {r['txt_path']}")
    for f in failures:
        print(f"  ✗ Video {f['index']} — {f['error'][:80]}")
    print("=" * 56)

    if failures and not results:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
