"""
Facebook Uploader — uploads videos as Reels via Facebook Graph API.

Auth strategy (designed for GitHub Actions):
  - FACEBOOK_PAGE_ID: your Facebook Page numeric ID
  - FACEBOOK_PAGE_ACCESS_TOKEN: long-lived Page Access Token (60-day or never-expiring)

  Generate a long-lived token once:
    1. Go to https://developers.facebook.com/tools/explorer/
    2. Select your App → Generate Token with permissions:
         pages_show_list, pages_read_engagement, pages_manage_posts,
         pages_manage_videos (or publish_video)
    3. Exchange for long-lived token via:
         GET https://graph.facebook.com/v21.0/oauth/access_token
           ?grant_type=fb_exchange_token
           &client_id={APP_ID}
           &client_secret={APP_SECRET}
           &fb_exchange_token={SHORT_LIVED_TOKEN}
    4. Get a Page token from the long-lived User token:
         GET https://graph.facebook.com/v21.0/me/accounts?access_token={LONG_LIVED_USER_TOKEN}
    5. Store the page token as GitHub Secret FACEBOOK_PAGE_ACCESS_TOKEN

Upload flow (Facebook Reels 3-phase resumable upload):
  Phase 1 — Initialize: get video_id + upload_url
  Phase 2 — Upload:     POST raw video bytes to upload_url
  Phase 3 — Publish:    set video_state=PUBLISHED with caption
"""

import json
import os
import time
from pathlib import Path

import requests
from google import genai
from google.genai import types

from config import GEMINI_API_KEY

GRAPH_API_VERSION = "v21.0"
GRAPH_API_BASE = f"https://graph.facebook.com/{GRAPH_API_VERSION}"

FACEBOOK_PAGE_ID = os.getenv("FACEBOOK_PAGE_ID", "")
FACEBOOK_PAGE_ACCESS_TOKEN = os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN", "")

_gemini_client = genai.Client(api_key=GEMINI_API_KEY)

# ── Facebook caption prompt ───────────────────────────────────────────────────
_FB_CAPTION_PROMPT = """You are a Facebook Reels content specialist for Indian Hindu devotional content.
Generate an optimised Facebook Reels caption for the video described below.

Return ONLY valid JSON — no markdown fences, no extra text:
{
  "caption": "Full caption text (rules below)"
}

FACEBOOK CAPTION RULES:
- The first 125 characters appear before "See more" — make them the strongest hook.
- Line 1: 1-2 emojis + compelling Hindi or bilingual (Hindi+English) hook statement about the deity/topic.
- Lines 2-3: 2-3 short sentences summarising the video's core divine message or teaching.
- CTA line: "👍 Like करें | ❤️ Share करें | 🔔 Follow करें"
- Hashtag block at the very end — 8-12 hashtags mixing deity-specific, topic, and trending tags.
- Total caption length: under 500 characters for maximum feed reach.
- Language: Natural mix of Hindi (Devanagari) and English — how real Indians write on Facebook.

TRENDING HASHTAG CATEGORIES (pick the most relevant 8-12):
  Deity tags (match the video deity EXACTLY ONE):
    #JaiMahadev  #JaiShriRam  #JaiShriKrishna  #JaiHanuman
    #JaiMaaDurga  #JaiMaaLakshmi  #JaiGanesha  #JaiMaaSaraswati
  Content tags (pick 2-3):
    #Bhakti  #HinduDharma  #Spiritual  #DivineBlessing  #BhaktiSadhna
    #Devotional  #HinduGod  #IndianCulture  #Motivation
  Format/reach tags (always include these 3):
    #Reels  #FacebookReels  #Viral
  Audience tags (pick 1-2):
    #India  #HindiContent  #BharatMata  #IndianValues

GOOD EXAMPLE (Shiva video):
  "🙏 महादेव का यह रहस्य सुनकर आपकी जिंदगी बदल जाएगी!

  Shiva की शक्ति हर मुश्किल में आपके साथ है।
  इस video को अंत तक जरूर देखें — यह message आपके दिल को छू जाएगा।

  👍 Like करें | ❤️ Share करें | 🔔 Follow करें

  #JaiMahadev #Bhakti #HinduDharma #Spiritual #DivineBlessing #Reels #FacebookReels #Viral #India #HindiContent"

Generate a UNIQUE caption that MATCHES this video's specific deity and theme."""


def generate_facebook_caption(content: dict) -> str:
    """Use Gemini to generate a Facebook-optimised Reels caption."""
    user_prompt = (
        f"Video title: {content.get('title', '')}\n"
        f"Script (first 250 chars): {content.get('script', '')[:250]}\n"
        f"Tags: {', '.join(content.get('tags', [])[:8])}\n\n"
        "Generate the Facebook Reels caption now."
    )

    try:
        response = _gemini_client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                types.Content(role="user", parts=[types.Part(text=_FB_CAPTION_PROMPT)]),
                types.Content(role="user", parts=[types.Part(text=user_prompt)]),
            ],
            config=types.GenerateContentConfig(temperature=0.9, max_output_tokens=1024),
        )

        if not response.text:
            raise ValueError("Empty Gemini response")

        text = response.text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()

        start = text.find("{")
        end = text.rfind("}") + 1
        if start != -1 and end > 0:
            data = json.loads(text[start:end])
            caption = data.get("caption", "").strip()
            if caption:
                return caption

    except Exception as exc:
        print(f"  [FB] Caption generation failed ({exc}), using fallback.")

    # Fallback: build a simple caption from existing content
    fallback = (
        f"🙏 {content.get('title', 'भक्ति')}\n\n"
        f"{content.get('description', '')[:300]}\n\n"
        "👍 Like करें | ❤️ Share करें | 🔔 Follow करें\n\n"
        "#Bhakti #HinduGod #Spiritual #Reels #FacebookReels #Viral #India"
    )
    return fallback


def _upload_reel(video_path: Path, caption: str, page_id: str, access_token: str) -> str:
    """
    Upload video as a Facebook Reel using the 3-phase resumable upload API.
    Returns the Facebook video ID.
    """
    video_size = video_path.stat().st_size
    reels_url = f"{GRAPH_API_BASE}/{page_id}/video_reels"

    # ── Phase 1: Initialize ───────────────────────────────────────────────────
    print("  [FB] Phase 1/3 — Initializing reel upload…")
    init_resp = requests.post(
        reels_url,
        data={"upload_phase": "start", "access_token": access_token},
        timeout=30,
    )
    init_resp.raise_for_status()
    init_data = init_resp.json()

    if "video_id" not in init_data or "upload_url" not in init_data:
        raise RuntimeError(f"Unexpected Phase 1 response: {init_data}")

    video_id = init_data["video_id"]
    upload_url = init_data["upload_url"]
    print(f"  [FB] Assigned video_id: {video_id}")

    # ── Phase 2: Upload binary ────────────────────────────────────────────────
    print(f"  [FB] Phase 2/3 — Uploading {video_size / 1_048_576:.1f} MB…")
    with open(video_path, "rb") as f:
        upload_resp = requests.post(
            upload_url,
            headers={
                "Authorization": f"OAuth {access_token}",
                "offset": "0",
                "file_size": str(video_size),
            },
            data=f,
            timeout=300,  # 5-minute timeout for large files
        )
    upload_resp.raise_for_status()
    upload_result = upload_resp.json()
    if not upload_result.get("success"):
        raise RuntimeError(f"Phase 2 upload failed: {upload_result}")
    print("  [FB] Binary upload complete.")

    # ── Phase 3: Publish ──────────────────────────────────────────────────────
    print("  [FB] Phase 3/3 — Publishing reel…")
    time.sleep(3)  # brief pause — let FB process the binary

    publish_resp = requests.post(
        reels_url,
        data={
            "upload_phase": "finish",
            "video_id": video_id,
            "video_state": "PUBLISHED",
            "description": caption[:2200],
            "access_token": access_token,
        },
        timeout=60,
    )
    publish_resp.raise_for_status()
    publish_result = publish_resp.json()

    if not publish_result.get("success"):
        raise RuntimeError(f"Phase 3 publish failed: {publish_result}")

    return video_id


def _upload_as_page_video(video_path: Path, caption: str, page_id: str, access_token: str) -> str:
    """
    Fallback: upload as a standard Facebook Page video (not Reel).
    Used automatically if the Reels endpoint fails.
    Returns Facebook video ID.
    """
    url = f"https://graph-video.facebook.com/{GRAPH_API_VERSION}/{page_id}/videos"
    print("  [FB] Using standard video upload (fallback)…")
    with open(video_path, "rb") as f:
        resp = requests.post(
            url,
            data={"description": caption[:2200], "access_token": access_token},
            files={"source": ("video.mp4", f, "video/mp4")},
            timeout=300,
        )
    resp.raise_for_status()
    result = resp.json()
    video_id = result.get("id", "")
    if not video_id:
        raise RuntimeError(f"Standard video upload returned no ID: {result}")
    return video_id


def upload_video_facebook(
    video_path: Path,
    content: dict,
) -> str:
    """
    Upload video to Facebook Page as a Reel with an AI-generated caption.

    Args:
        video_path: Path to the .mp4 file.
        content:    Full content dict from generate_video_content()
                    (keys: title, description, script, tags).

    Returns:
        Facebook video ID string.
    """
    page_id = FACEBOOK_PAGE_ID
    access_token = FACEBOOK_PAGE_ACCESS_TOKEN

    if not page_id:
        raise ValueError(
            "FACEBOOK_PAGE_ID is not set. "
            "Add it as a GitHub Secret or set the env var."
        )
    if not access_token:
        raise ValueError(
            "FACEBOOK_PAGE_ACCESS_TOKEN is not set. "
            "Generate a long-lived Page Access Token and add it as a GitHub Secret."
        )

    # Generate Facebook-optimised caption via Gemini
    print("  [FB] Generating Facebook caption (Gemini)…")
    caption = generate_facebook_caption(content)
    print(f"  [FB] Caption preview: {caption[:120].replace(chr(10), ' ')}…")

    # Try Reels upload first; fall back to standard video upload
    try:
        video_id = _upload_reel(video_path, caption, page_id, access_token)
        reel_url = f"https://www.facebook.com/reel/{video_id}"
        print(f"  [FB] Reel published — {reel_url}")
    except Exception as exc:
        print(f"  [FB] Reels upload failed ({exc}). Falling back to standard video upload…")
        video_id = _upload_as_page_video(video_path, caption, page_id, access_token)
        print(f"  [FB] Video published — https://www.facebook.com/video/{video_id}")

    return video_id
