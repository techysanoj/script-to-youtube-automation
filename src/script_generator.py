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
  "tags": ["15-20 SEO tags — mix of Hindi and English"]
}}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TITLE RULES — Hindi Devanagari, YouTube Shorts SEO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE: Pure Hindi in Devanagari script ONLY (देवनागरी). No Roman/English words in title.
LENGTH: 50-60 characters max (Devanagari chars count more — keep it short and punchy).
STRUCTURE: [Emotional Hook] + [Deity Name] + [Curiosity/Benefit] + #Shorts

HOOK STARTERS (pick one, in Devanagari):
  "क्या आप जानते हैं...", "बस एक बार...", "आज से...", "यह सुनकर...", "इसे सुनो..."

POWER WORDS that boost CTR (use in Devanagari):
  चमत्कार, सच्चाई, अद्भुत, शक्ति, आशीर्वाद, रहस्य, विश्वास, जीवन बदल देगा

DEITY NAMES in Devanagari: शिव, कृष्ण, गणेश, दुर्गा, लक्ष्मी, विष्णु, हनुमान, राम, सरस्वती

GOOD TITLE EXAMPLES (follow this pattern exactly):
  "शिव का यह सच सुनकर रो पड़ोगे 🙏 #Shorts"
  "बस एक बार गणेश जी को यह बोलो — चमत्कार होगा #Shorts"
  "आज से मुश्किलें खत्म — कृष्ण का वचन #Shorts"
  "यह सुनकर आपकी ज़िंदगी बदल जाएगी | जय महादेव #Shorts"
  "हनुमान जी की यह शक्ति जानते हो? ✨ #Shorts"

RULES:
- End ALWAYS with #Shorts (this is required for YouTube Shorts algorithm)
- Only 1-2 emojis max — place naturally, not spam
- NO all-caps, NO excessive punctuation (!!!), NO clickbait lies
- Each title must be UNIQUE — different deity, different hook each video

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
DESCRIPTION RULES — Hindi Devanagari, YouTube SEO:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANGUAGE: Hindi Devanagari for body text. Hashtags in English (standard YouTube practice).
LINE 1-2: Primary keyword visible before "Show more" — must include deity name + topic in Hindi.
  Example: "भगवान शिव की यह शक्ति आपकी सभी परेशानियां दूर कर देगी।"
BODY: 3-4 lines — brief summary of video, devotional message, relatable benefit.
CTA LINE: "👍 लाइक करें | 🔔 सब्सक्राइब करें | ❤️ शेयर करें"
HASHTAG BLOCK (end of description, 10-12 hashtags):
  Always include: #Shorts #YouTubeShorts #HindiShorts
  Deity-specific: #[DeityName] e.g. #Shiva #Mahadev #MahadevStatus
  Topic: #Bhakti #Devotional #HinduGods #Spiritual #IndianMotivation
  Trending: #Motivation #Viral #Status #ShortsFeed #trending
Max 150 words total.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TAGS RULES — 15-20 tags for maximum discoverability:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Include ALL of these categories:
1. Core Shorts tags: "Shorts", "YouTubeShorts", "ShortsFeed", "ViralShorts"
2. Deity tags (English + Hindi transliteration): e.g. "Shiva", "Mahadev", "Bholenath", "Shivji"
3. Topic tags: "Bhakti", "Devotional", "HinduGods", "Spiritual", "DivineBlessing"
4. Audience tags: "IndianMotivation", "HindiShorts", "BhaktiShorts", "MotivationalVideo"
5. Trending/broad: "Motivation", "Viral", "trending", "Status", "DailyMotivation"
Tags must be strings without # symbol — YouTube API tags field does not use #.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMAGE PROMPT RULES (always in English for best results):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- Portrait 9:16, photorealistic or divine illustration
- Vary deities each video: Shiva, Vishnu, Ganesha, Durga, Lakshmi, Krishna, Rama, Hanuman, Saraswati
- Style: "divine golden light, ethereal glow, majestic, ultra-detailed, 8k, cinematic, sacred"
- Each of the {IMAGES_PER_VIDEO} prompts must show a DIFFERENT scene/angle

Generate completely fresh content each time — different deity, different hook, different theme."""


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
