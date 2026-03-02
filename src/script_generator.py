"""
Script Generator — uses Gemini 1.5 Flash (free tier) to generate:
  - Motivational voiceover script tied to a Hindu god
  - 8 AI image prompts for the visual slideshow
  - YouTube-optimised title, description, and tags
"""

import json
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, IMAGES_PER_VIDEO

_client = genai.Client(api_key=GEMINI_API_KEY)

_SYSTEM_PROMPT = f"""You are an expert Indian YouTube Shorts creator and Hindi SEO specialist \
creating viral Hindu spirituality content for Indian audiences.

Return ONLY valid JSON — no markdown fences, no extra text — in this exact structure:
{{
  "title": "Title in pure Hindi Devanagari script (SEO rules below)",
  "script": "40-second Hinglish voiceover script (rules below)",
  "image_prompts": [
    "Detailed English prompt for AI image 1 (portrait 9:16, cinematic, ultra-detailed)",
    "... ({IMAGES_PER_VIDEO} prompts total)"
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
STRUCTURE: [Primary Keyword: Deity + Topic] + [Emotional Hook / Curiosity Gap] + #Shorts

HOOK PATTERNS (pick one, place AFTER the keyword):
  "...जो आपने कभी नहीं सुना", "...एक बार ज़रूर सुनो", "...यह सुनकर रो पड़ोगे",
  "...यह जानकर हैरान हो जाओगे", "...का यह रहस्य बदल देगा ज़िंदगी"

POWER WORDS that boost CTR (use in Devanagari):
  चमत्कार, सच्चाई, अद्भुत, शक्ति, आशीर्वाद, रहस्य, विश्वास, जीवन बदल देगा

DEITY NAMES in Devanagari: शिव, कृष्ण, गणेश, दुर्गा, लक्ष्मी, विष्णु, हनुमान, राम, सरस्वती

GOOD TITLE EXAMPLES (front-loaded keyword first):
  "शिव का यह रहस्य सुनकर रो पड़ोगे 🙏 #Shorts"
  "गणेश जी की शक्ति — बस एक बार यह बोलो, चमत्कार होगा #Shorts"
  "कृष्ण का वचन जो मुश्किलें खत्म कर देगा #Shorts"
  "महादेव का यह सच आपकी ज़िंदगी बदल देगा ✨ #Shorts"
  "हनुमान जी की भक्ति का यह अद्भुत रहस्य #Shorts"

RULES:
- End ALWAYS with #Shorts (required for YouTube Shorts algorithm discovery)
- Only 1-2 emojis max — place naturally, not spam
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

Script language: HINGLISH — Roman script, Hindi-dominant, simple English words allowed.
NO Devanagari in script. NO pure English sentences. Conversational, like talking to a friend.

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
IMAGE PROMPT RULES (always in English for best results):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Portrait 9:16, photorealistic or divine illustration
- Vary deities each video: Shiva, Vishnu, Ganesha, Durga, Lakshmi, Krishna, Rama, Hanuman, Saraswati
- Style: "divine golden light, ethereal glow, majestic, ultra-detailed, 8k, cinematic, sacred"
- Each of the {IMAGES_PER_VIDEO} prompts must show a DIFFERENT scene/angle

Generate completely fresh, unique content each time — different deity, different hook, different theme.
ALL metadata (title, description, tags) must be contextually consistent with each other and the script."""


def generate_video_content() -> dict:
    """Generate complete video content using Gemini 2.0 Flash."""
    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=_SYSTEM_PROMPT,
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

    # Guarantee exactly IMAGES_PER_VIDEO prompts
    prompts = content.get("image_prompts", [])
    while len(prompts) < IMAGES_PER_VIDEO:
        prompts.append(prompts[-1] if prompts else "Lord Ganesha divine portrait, golden light, 9:16")
    content["image_prompts"] = prompts[:IMAGES_PER_VIDEO]

    return content
