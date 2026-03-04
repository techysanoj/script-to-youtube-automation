import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── API Keys ──────────────────────────────────────────────────────────────────
GEMINI_API_KEY       = os.getenv("GEMINI_API_KEY", "")
UNSPLASH_ACCESS_KEY  = os.getenv("UNSPLASH_ACCESS_KEY", "")
PEXELS_API_KEY       = os.getenv("PEXELS_API_KEY", "")

# ── YouTube OAuth ─────────────────────────────────────────────────────────────
YOUTUBE_CLIENT_SECRETS_FILE = os.getenv("YOUTUBE_CLIENT_SECRETS_FILE", "client_secrets.json")
YOUTUBE_TOKEN_FILE = os.getenv("YOUTUBE_TOKEN_FILE", "youtube_token.json")
YOUTUBE_SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly",
]
YOUTUBE_CATEGORY_ID = "22"   # People & Blogs
YOUTUBE_PRIVACY = os.getenv("YOUTUBE_PRIVACY", "public")  # public | private | unlisted

# ── Video Settings ────────────────────────────────────────────────────────────
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
VIDEO_FPS = 24
IMAGE_DURATION = 5.0      # seconds per image clip
BG_MUSIC_VOLUME = 0.35    # 35% — background music under voiceover

# ── Content Settings ──────────────────────────────────────────────────────────
VIDEOS_PER_RUN = int(os.getenv("VIDEOS_PER_RUN", "2"))
IMAGES_PER_VIDEO = 8
VOICE = "hi-IN-SwaraNeural"  # edge-tts Hindi female voice (free, natural Hinglish)

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
OUTPUT_DIR = BASE_DIR / "output"
ASSETS_DIR = BASE_DIR / "assets"
MUSIC_DIR = ASSETS_DIR / "music"
TEMP_DIR = BASE_DIR / "temp"

OUTPUT_DIR.mkdir(exist_ok=True)
TEMP_DIR.mkdir(exist_ok=True)
MUSIC_DIR.mkdir(parents=True, exist_ok=True)
