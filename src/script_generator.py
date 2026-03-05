"""
Script Generator — uses Gemini 1.5 Flash (free tier) to generate:
  - Motivational voiceover script tied to a Hindu god
  - 8 AI image prompts for the visual slideshow
  - YouTube-optimised title, description, and tags
"""

import json
import re
import random
import datetime
from pathlib import Path
from google import genai
from google.genai import types
from config import GEMINI_API_KEY

_client = genai.Client(api_key=GEMINI_API_KEY)

# ── Content history — tracks last N deity+theme combos to prevent repetition ──
_HISTORY_FILE = Path(__file__).parent.parent / "content_history.json"
_MAX_HISTORY = 15   # remember last 15 videos


def _load_history() -> list[str]:
    if _HISTORY_FILE.exists():
        try:
            return json.loads(_HISTORY_FILE.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_to_history(history: list[str], entry: str) -> None:
    history.append(entry)
    _HISTORY_FILE.write_text(
        json.dumps(history[-_MAX_HISTORY:], ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

_SYSTEM_PROMPT = f"""You are an expert Indian YouTube Shorts creator and Hindi SEO specialist \
creating viral Hindu spirituality content for Indian audiences.

Return ONLY valid JSON — no markdown fences, no extra text — in this exact structure:
{{
  "title": "Title in pure Hindi Devanagari script (SEO rules below)",
  "script": "40-second Hinglish voiceover script (rules below)",
  "search_terms": [
    "deity scene1",
    "deity scene2",
    "deity scene3",
    "temple word1",
    "india word2"
  ],
  "description": "YouTube description in Hindi Devanagari (SEO rules below)",
  "tags": ["8-12 highly specific SEO tags — rules below"]
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TITLE RULES — Hindi Devanagari, YouTube Shorts SEO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE: Pure Hindi in Devanagari script ONLY (देवनागरी). No Roman/English words in title.
LENGTH: 50-60 characters max (Devanagari chars count more — keep it short and punchy).
KEYWORD PLACEMENT: Lead with the primary keyword (deity name + topic) in the FIRST 3 words —
  YouTube reads titles left-to-right for ranking, front-loaded keywords rank higher.
STRUCTURE: [Primary Keyword: Deity + Topic] + [Emotional Hook / Curiosity Gap] + [2-3 Hashtags]

HASHTAGS IN TITLE — always 2-3 hashtags at the END of the title:
  1. #Shorts — MANDATORY first (triggers YouTube Shorts discovery algorithm)
  2. #[Deity hashtag] — MANDATORY, match the deity of this video:
       Shiva → #Mahadev   |  Krishna → #Krishna  |  Ganesha → #Ganesha
       Hanuman → #Hanuman |  Durga → #Durga       |  Lakshmi → #Lakshmi
       Ram → #JaiShriRam  |  Vishnu → #Vishnu     |  Saraswati → #Saraswati
  3. #[Topic hashtag] — OPTIONAL, only add if space allows (title stays ≤60 chars):
       #Bhakti | #Spiritual | #Motivation | #HinduGod | #DivineBlessing

HOOK PATTERNS (pick one, place AFTER the keyword):
  "...जो आपने कभी नहीं सुना", "...एक बार ज़रूर सुनो", "...यह सुनकर रो पड़ोगे",
  "...यह जानकर हैरान हो जाओगे", "...का यह रहस्य बदल देगा ज़िंदगी"

POWER WORDS that boost CTR (use in Devanagari):
  चमत्कार, सच्चाई, अद्भुत, शक्ति, आशीर्वाद, रहस्य, विश्वास, जीवन बदल देगा

DEITY NAMES in Devanagari: शिव, कृष्ण, गणेश, दुर्गा, लक्ष्मी, विष्णु, हनुमान, राम, सरस्वती

GOOD TITLE EXAMPLES (2-3 hashtags at end):
  "शिव का यह रहस्य सुनकर रो पड़ोगे 🙏 #Shorts #Mahadev"
  "गणेश जी की शक्ति — बस एक बार यह बोलो #Shorts #Ganesha #Bhakti"
  "कृष्ण का वचन जो मुश्किलें खत्म कर देगा #Shorts #Krishna"
  "महादेव का यह सच आपकी ज़िंदगी बदल देगा ✨ #Shorts #Mahadev #Spiritual"
  "हनुमान जी की भक्ति का यह अद्भुत रहस्य #Shorts #Hanuman #Bhakti"

RULES:
- #Shorts ALWAYS comes first in the hashtag group (most important for algorithm)
- #[Deity] ALWAYS second — deity-specific hashtag gets subscriber reach
- 3rd hashtag ONLY if title stays under 60 characters after adding it
- Only 1-2 emojis max — place naturally before the hashtags
- NO all-caps, NO excessive punctuation (!!!), NO clickbait lies
- Title must MATCH the actual video content — mismatched metadata triggers algorithmic penalties
- Each title must be UNIQUE — different deity, different hook, different theme every video

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCRIPT RULES — 40-second Hinglish voiceover:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: HOOK (5s) → BODY (28s) → ENDING (7s)
Total: 90-110 words in Roman Hinglish (reads in ~40 seconds at natural pace)

HOOK (1-2 sentences — grab attention in 3 seconds):
- Bold question or surprising claim about the deity
- Example: "Kya aap jaante hain, Shiva ne ek baar poori duniya ko rok diya tha?"

BODY (3-4 short sentences — deliver value):
- Divine teaching, story, or blessing connected to real life (paisa, love, health, success)
- Max 12 words per sentence — keep it punchy
- Example: "Jab mushkilein aati hain, woh humein todti nahi — balki aur strong banati hain."

ENDING (1-2 sentences — powerful close):
- Reaffirm the blessing, then deity battle cry
- "Unka ashirwad hamesha hamare saath hai. Jai Mahadev!" / "Jai Shri Ram!" / "Jai Mata Di!"

Script language: MIXED-SCRIPT HINGLISH
- Hindi / Urdu words → write in Devanagari script (देवनागरी)
- English words that have no natural Hindi equivalent → keep in Latin/English script
- No full Roman transliteration of Hindi words (e.g. write "जानते" not "jaante")
- The TTS voice is hi-IN-SwaraNeural — it reads Devanagari natively and handles English words naturally
- Conversational, like a friend talking — natural code-mixing as real Indians speak

MIXED-SCRIPT EXAMPLE (correct format):
  "क्या आप जानते हैं — Shiva ने एक बार पूरी duniya को रोक दिया था?
   जब life में मुश्किलें आती हैं, वो हमें तोड़ती नहीं — बल्कि और strong बनाती हैं।
   उनका आशीर्वाद हमेशा हमारे साथ है। जय महादेव!"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DESCRIPTION RULES — Hindi Devanagari, YouTube SEO 2026:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE: Hindi Devanagari for body text.
CRITICAL: Every description must be UNIQUE and reflect this specific video's content.
  Repetitive, copy-paste descriptions across videos signal spam to YouTube's algorithm.

LINE 1 (before "Show more" — most important line):
  - Must contain the primary keyword: deity name + specific topic/message from THIS video
  - Make it a compelling one-sentence hook that makes viewers click "Show more"
  - Example: "भगवान शिव का वह रहस्य जो हर मुश्किल में आपकी रक्षा करता है।"

LINES 2-4 (unique body — summarise THIS video's specific message):
  - 2-3 sentences describing what THIS video teaches or reveals
  - Include the core divine message/blessing from the script
  - Relatable real-life benefit (success, peace, protection, wealth, health)

CTA LINE: "👍 लाइक करें | 🔔 सब्सक्राइब करें | ❤️ शेयर करें अपनों के साथ"

HASHTAG BLOCK — EXACTLY 3-5 hashtags (no more — excess hashtags reduce reach):
  ⚠️ The FIRST 3 hashtags appear visibly ABOVE the video title — choose them wisely.
  Order: Most specific → Most broad
  1. Deity/topic-specific: #Mahadev OR #ShriKrishna OR #JaiHanuman (match the deity)
  2. Content category: #Bhakti OR #Shorts
  3. Broad reach: #Spiritual OR #HindiShorts
  Maximum 5 hashtags total. Never repeat hashtags across videos.

Max 120 words total (description + hashtags combined).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TAGS RULES — 8-12 highly specific tags (2026 best practice):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT: In 2026, YouTube tags have minimal ranking impact. Their PRIMARY purpose is:
  1. Catching spelling variations of your deity/topic name
  2. Long-tail niche phrases that exactly match how your audience searches
  3. Episode-specific context (NOT generic keywords that apply to every video)

DO NOT use generic tags like "Motivation", "Viral", "trending", "Status" — they waste space
  and add no discoverability value.

INCLUDE:
1. Deity name variations (spelling/transliteration): e.g. "Shiva", "Shiv", "Mahadev", "Bholenath"
2. Deity + specific topic from THIS video: e.g. "Shiva blessing for success", "Mahadev protection mantra"
3. Long-tail niche phrases: e.g. "hindi bhakti shorts", "shiv bhakti status video", "hindu devotional short video"
4. Channel niche anchor: "bhakti shorts hindi", "hindu god shorts"

Tags must be strings WITHOUT # symbol — YouTube API tags field does not use #.
Generate 8-12 tags total, all specific to THIS video's deity and theme.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEARCH TERMS RULES (used to search Wikimedia, Unsplash, Pexels):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generate EXACTLY 5 search terms. Each term must be EXACTLY 2 English words.
These will be sent to real stock photo APIs — short, specific terms work best.

RULES:
- 2 words ONLY per term — APIs match better with concise phrases
- English only — Wikimedia, Unsplash and Pexels are English-indexed
- Use deity's English name (e.g. "shiva", "krishna", "hanuman") as word 1 for 3 terms
- Word 2 should show a DIFFERENT visual angle: meditation, temple, festival, portrait, devotion
- Include 1-2 generic spiritual fallbacks: "temple worship", "diwali lights", "india spiritual"

GOOD EXAMPLES:
  Shiva video   → ["shiva meditation", "shiva temple", "shiva cosmic", "temple incense", "india spiritual"]
  Krishna video → ["krishna flute", "krishna devotion", "temple worship", "india festival", "radha krishna"]
  Durga video   → ["durga goddess", "navratri festival", "temple offerings", "india devotion", "diwali lights"]
  Hanuman video → ["hanuman devotion", "hanuman temple", "india bhakti", "temple worship", "ram hanuman"]

Generate completely fresh, unique content each time — different deity, different hook, different theme.
ALL metadata (title, description, tags) must be contextually consistent with each other and the script."""


def generate_video_content() -> dict:
    """Generate complete video content using Gemini 2.5 Flash.

    Uses a history file to avoid repeating deity+theme combos and injects
    a unique session seed so the model cannot return a cached response.
    """
    history = _load_history()

    # Build the avoid-list from the last 5 entries (most recent = most important)
    avoid_list = history[-5:] if history else []
    avoid_str = "; ".join(avoid_list) if avoid_list else "none yet"

    # Unique seed — date + time + random int — forces a fresh generation every call
    session_seed = (
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"seed={random.randint(100_000, 999_999)}"
    )

    user_prompt = (
        f"Session: {session_seed}\n"
        f"Recently used deity+theme combos (DO NOT repeat any of these):\n"
        f"  {avoid_str}\n\n"
        f"Generate completely fresh content with a DIFFERENT deity and DIFFERENT theme now."
    )

    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(role="user", parts=[types.Part(text=_SYSTEM_PROMPT)]),
            types.Content(role="user", parts=[types.Part(text=user_prompt)]),
        ],
        config=types.GenerateContentConfig(
            temperature=0.95,
            max_output_tokens=8192,
        ),
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    text = response.text.strip()

    # Strip accidental markdown code fences
    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    # Find the JSON object boundaries in case there's any leading/trailing noise
    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise RuntimeError(f"No JSON object found in Gemini response:\n{text[:200]}")
    text = text[start:end]

    content = json.loads(text)

    # Normalise tags to lowercase (e.g. "Durga Protection" → "durga protection")
    content["tags"] = [t.lower() for t in content.get("tags", [])]

    # Normalise hashtags in description to lowercase (e.g. #Mahadev → #mahadev)
    content["description"] = re.sub(
        r"#([A-Za-z0-9_]+)",
        lambda m: "#" + m.group(1).lower(),
        content.get("description", ""),
    )

    # Normalise hashtags in title to lowercase (e.g. #Shorts #Mahadev → #shorts #mahadev)
    content["title"] = re.sub(
        r"#([A-Za-z0-9_]+)",
        lambda m: "#" + m.group(1).lower(),
        content.get("title", ""),
    )

    # Guarantee exactly 5 search terms (2 images each = 10 slots → first 8 used)
    terms = content.get("search_terms", [])
    while len(terms) < 5:
        terms.append("india temple")
    content["search_terms"] = terms[:5]

    # Save this generation to history so future runs avoid it
    title = content.get("title", "unknown")
    _save_to_history(history, f"{datetime.datetime.now().strftime('%Y-%m-%d')} | {title}")

    return content
