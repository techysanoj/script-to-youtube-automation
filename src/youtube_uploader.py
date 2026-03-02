"""
YouTube Uploader — uploads videos via YouTube Data API v3 (free, 10k units/day).

Auth strategy (designed for GitHub Actions):
  - youtube_token.json holds the refresh_token + client credentials.
  - At runtime we exchange the refresh_token for a fresh access_token.
  - No interactive browser step in CI — run scripts/auth_youtube.py locally ONCE
    to generate the token, then store it as a GitHub Secret.
"""

import json
from pathlib import Path

import google.oauth2.credentials
import googleapiclient.discovery
import googleapiclient.errors
import googleapiclient.http
from google.auth.transport.requests import Request

from config import (
    YOUTUBE_CLIENT_SECRETS_FILE,
    YOUTUBE_TOKEN_FILE,
    YOUTUBE_SCOPES,
    YOUTUBE_CATEGORY_ID,
    YOUTUBE_PRIVACY,
)


def _load_credentials() -> google.oauth2.credentials.Credentials:
    token_file = Path(YOUTUBE_TOKEN_FILE)
    if not token_file.exists():
        raise FileNotFoundError(
            f"YouTube token not found at '{YOUTUBE_TOKEN_FILE}'. "
            "Run scripts/auth_youtube.py locally to generate it, "
            "then add it as a GitHub Secret YOUTUBE_TOKEN."
        )
    data = json.loads(token_file.read_text())
    return google.oauth2.credentials.Credentials(
        token=data.get("token"),
        refresh_token=data["refresh_token"],
        token_uri=data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=data["client_id"],
        client_secret=data["client_secret"],
        scopes=YOUTUBE_SCOPES,
    )


def _get_service():
    creds = _load_credentials()
    # Always refresh to get a valid access token
    creds.refresh(Request())
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)


def upload_video(
    video_path: Path,
    title: str,
    description: str,
    tags: list[str],
) -> str:
    """
    Upload video_path to YouTube and return the video ID.
    Automatically marks it as a YouTube Short (vertical ≤ 60s + #Shorts tag).
    """
    youtube = _get_service()

    # YouTube Shorts must have #Shorts in title or description
    if "#Shorts" not in title and "#shorts" not in title:
        title = (title[:93] + " #Shorts") if len(title) > 93 else title + " #Shorts"

    if "#Shorts" not in description and "#shorts" not in description:
        description += "\n\n#Shorts #HinduGods #Motivation #Spiritual #Devotional"

    # Deduplicate and cap tags
    seen = set()
    unique_tags = []
    for t in (tags + ["Shorts", "HinduGods", "Motivation", "Spiritual"]):
        key = t.lower()
        if key not in seen:
            seen.add(key)
            unique_tags.append(t)
        if len(unique_tags) >= 30:
            break

    body = {
        "snippet": {
            "title": title[:100],
            "description": description[:4990],
            "tags": unique_tags,
            "categoryId": YOUTUBE_CATEGORY_ID,
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": YOUTUBE_PRIVACY,
            "selfDeclaredMadeForKids": False,
        },
    }

    media = googleapiclient.http.MediaFileUpload(
        str(video_path),
        mimetype="video/mp4",
        resumable=True,
        chunksize=2 * 1024 * 1024,  # 2 MB chunks
    )

    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"  Upload: {pct}%", end="\r", flush=True)

    video_id = response["id"]
    print(f"  Upload complete — https://www.youtube.com/shorts/{video_id}")
    return video_id
