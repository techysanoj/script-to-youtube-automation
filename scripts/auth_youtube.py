"""
scripts/auth_youtube.py

Run this script ONCE on your local machine to authorise the app with YouTube.
It opens a browser tab for Google OAuth consent and saves the token locally.

After running:
  1. Add the contents of client_secrets.json as GitHub Secret → YOUTUBE_CLIENT_SECRETS
  2. Add the contents of youtube_token.json   as GitHub Secret → YOUTUBE_TOKEN

Usage:
  python scripts/auth_youtube.py
"""

import json
import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import google_auth_oauthlib.flow
from config import YOUTUBE_CLIENT_SECRETS_FILE, YOUTUBE_TOKEN_FILE, YOUTUBE_SCOPES


def main() -> None:
    secrets = Path(YOUTUBE_CLIENT_SECRETS_FILE)
    token = Path(YOUTUBE_TOKEN_FILE)

    if not secrets.exists():
        print(f"\n[ERROR] '{YOUTUBE_CLIENT_SECRETS_FILE}' not found.\n")
        print("Steps to get it:")
        print("  1. Go to https://console.cloud.google.com/")
        print("  2. Create a project (or select an existing one)")
        print("  3. Navigate to: APIs & Services → Library")
        print("  4. Search for 'YouTube Data API v3' and Enable it")
        print("  5. Go to: APIs & Services → Credentials")
        print("  6. Click 'Create Credentials' → 'OAuth client ID'")
        print("  7. Application type: Desktop app")
        print("  8. Download JSON → rename it to client_secrets.json")
        print("  9. Place client_secrets.json in the project root")
        print(" 10. Re-run this script\n")
        sys.exit(1)

    print("\nOpening browser for YouTube OAuth consent…")
    flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
        str(secrets), YOUTUBE_SCOPES
    )
    credentials = flow.run_local_server(port=0)

    token_data = {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": list(credentials.scopes or YOUTUBE_SCOPES),
    }

    token.write_text(json.dumps(token_data, indent=2))
    print(f"\n[OK] Token saved → {YOUTUBE_TOKEN_FILE}\n")

    print("─" * 60)
    print("Next steps — add these two GitHub Secrets:")
    print("  Secret name : YOUTUBE_CLIENT_SECRETS")
    print(f"  Secret value: (copy the full contents of {YOUTUBE_CLIENT_SECRETS_FILE})")
    print()
    print("  Secret name : YOUTUBE_TOKEN")
    print(f"  Secret value: (copy the full contents of {YOUTUBE_TOKEN_FILE})")
    print()
    print("  Also add:  GEMINI_API_KEY  ← your Gemini API key")
    print("─" * 60)
    print("\nTo get Gemini API key (free): https://aistudio.google.com/\n")


if __name__ == "__main__":
    main()
