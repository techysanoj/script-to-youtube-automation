"""
main.py — YouTube Shorts Automation Orchestrator

Runs the full pipeline VIDEOS_PER_RUN times:
  Gemini script → AI images → edge-tts voiceover → FFmpeg video → YouTube upload

Usage:
  python main.py              # full pipeline (all 6 steps)
  python main.py --steps 5   # stop after video assembly (skip upload)
  python main.py --steps 3   # stop after voiceover (skip video + upload)

Steps:
  1 = Script generation
  2 = Image fetching
  3 = Voiceover + subtitles
  4 = Background music
  5 = Video assembly
  6 = YouTube upload (default)
"""

import argparse
import shutil
import time
from datetime import datetime, timezone

from config import VIDEOS_PER_RUN, TEMP_DIR
from src.script_generator import generate_video_content
from src.image_generator import generate_all_images
from src.voiceover import generate_voiceover
from src.audio_manager import get_background_music
from src.video_creator import create_video
from src.youtube_uploader import upload_video


def run_pipeline(video_index: int, stop_after: int = 6) -> dict:
    """Execute the pipeline for one video up to `stop_after` step."""
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    run_id = f"{ts}_{video_index}"

    sep = "=" * 56
    print(f"\n{sep}")
    print(f"  Video {video_index + 1}/{VIDEOS_PER_RUN}  (run_id: {run_id})")
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

        # ── 2. Images ─────────────────────────────────────────────────────────
        print(f"\n[2/6] Fetching images ({len(content['search_terms'])} terms × 2 = up to 10, using first 8)…")
        image_paths = generate_all_images(content["search_terms"], run_id)
        if not image_paths:
            raise RuntimeError("Image generation returned no usable files.")
        print(f"  {len(image_paths)} images ready.")
        if stop_after == 2:
            print("\n  Stopped after step 2 (images).")
            return {"run_id": run_id, "stopped_at": 2, "title": content["title"]}

        # ── 3. Voiceover + karaoke subtitles ─────────────────────────────────
        print("\n[3/6] Generating voiceover + subtitles (edge-tts)…")
        voiceover_path, subtitle_path = generate_voiceover(content["script"], run_id)
        if stop_after == 3:
            print("\n  Stopped after step 3 (voiceover).")
            return {"run_id": run_id, "stopped_at": 3, "title": content["title"]}

        # ── 4. Background music ───────────────────────────────────────────────
        print("\n[4/6] Selecting background music…")
        bg_music = get_background_music()
        if stop_after == 4:
            print("\n  Stopped after step 4 (music).")
            return {"run_id": run_id, "stopped_at": 4, "title": content["title"]}

        # ── 5. Assemble video ─────────────────────────────────────────────────
        print("\n[5/6] Assembling video (FFmpeg)…")
        video_path = create_video(
            image_paths=image_paths,
            voiceover_path=voiceover_path,
            subtitle_path=subtitle_path,
            bg_music=bg_music,
            run_id=run_id,
            video_index=video_index,
        )
        if stop_after == 5:
            print(f"\n  Stopped after step 5 (video). File saved to: {video_path}")
            return {"run_id": run_id, "stopped_at": 5, "title": content["title"], "video_path": str(video_path)}

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
        # Keep temp files when stopping early so you can inspect them
        if stop_after >= 6:
            run_temp = TEMP_DIR / run_id
            if run_temp.exists():
                shutil.rmtree(run_temp, ignore_errors=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="YouTube Shorts Automation Pipeline")
    parser.add_argument(
        "--steps", type=int, default=6, choices=range(1, 7), metavar="N",
        help="Stop after step N (1=script, 2=images, 3=voiceover, 4=music, 5=video, 6=upload). Default: 6",
    )
    args = parser.parse_args()

    start = datetime.now(timezone.utc)
    print(f"\nYouTube Shorts Automation — {start.strftime('%Y-%m-%d %H:%M UTC')}")
    print(f"Scheduled videos: {VIDEOS_PER_RUN}  |  Running up to step {args.steps}/6")

    results, failures = [], []

    for i in range(VIDEOS_PER_RUN):
        try:
            result = run_pipeline(i, stop_after=args.steps)
            results.append(result)
        except Exception as exc:
            print(f"\n[ERROR] Video {i + 1} failed: {exc}")
            failures.append({"index": i + 1, "error": str(exc)})

        # Brief pause between videos to respect API rate limits
        if i < VIDEOS_PER_RUN - 1:
            print("\nPausing 15 s before next video…")
            time.sleep(15)

    # ── Summary ───────────────────────────────────────────────────────────────
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
                print(f"    Video: {r['video_path']}")
    for f in failures:
        print(f"  ✗ Video {f['index']} — {f['error'][:80]}")
    print("=" * 56)

    if failures and not results:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
