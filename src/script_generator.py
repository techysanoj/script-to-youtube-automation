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

# ── Content history — separate files so YouTube and Facebook never share topics ──
_YOUTUBE_HISTORY_FILE = Path(__file__).parent.parent / "content_history_youtube.json"
_FACEBOOK_HISTORY_FILE = Path(__file__).parent.parent / "content_history_facebook.json"
_MAX_HISTORY = 15   # remember last 15 videos per platform


def _load_history(history_file: Path) -> list[str]:
    if history_file.exists():
        try:
            return json.loads(history_file.read_text(encoding="utf-8"))
        except Exception:
            return []
    return []


def _save_to_history(history: list[str], entry: str, history_file: Path) -> None:
    history.append(entry)
    history_file.write_text(
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
Structure: HOOK (2s) → BODY (31s) → ENDING (7s)
Total: 90-110 words in Roman Hinglish (reads in ~40 seconds at natural pace)

HOOK — THE SINGLE MOST IMPORTANT LINE (viewer decides in 1.3 seconds):
The hook is EXACTLY 1 sentence. Max 10 words. It must land in the FIRST breath.
NO warmup phrases. NO "क्या आप जानते हैं", NO "आज हम बात करेंगे" — these waste the
first second. START with the most emotionally charged word in the entire script.

The FIRST word must be the deity name OR the most shocking/emotional word.

Use ONE of these 4 proven formulas — keep it under 10 words:

  SHOCKING TRUTH (state something counter-intuitive immediately):
    "[Deity] कहते हैं — जो टूट जाता है, वही सबसे तेज़ चमकता है।"
    "जो सबसे ज़्यादा तकलीफ में है — [Deity] उसके सबसे करीब हैं।"
    "हार वो नहीं जो गिरे — हार वो है जो उठा नहीं।"

  OPEN LOOP (create a gap only the body can close):
    "[Deity] का वो एक राज़ — जो 99% लोग नहीं जानते।"
    "एक बात जो [Deity] ने कही थी — आज तक किसी ने नहीं सुनी।"

  BOLD PROMISE (specific, immediate benefit):
    "यह 40 seconds सुन लो — [Deity] की कृपा खुद महसूस होगी।"
    "[Deity] का यह वचन सुन लो — मुश्किल रात आसान हो जाएगी।"

  DIRECT CALL-OUT (speak directly to the viewer's pain):
    "अगर life में सब कुछ गलत लग रहा है — यह सुनो।"
    "थक गए हो? रुको — [Deity] का एक message है तुम्हारे लिए।"

HOOK RULES:
- FIRST word = deity name OR most powerful emotional word — no exceptions
- Max 1 sentence, max 10 words — reads in under 2 seconds
- NEVER warm up — no "क्या आप जानते हैं", no "आज हम", no "दोस्तों"
- End on a curiosity gap OR a direct emotional promise — never a full resolution
- The hook alone should make someone stop scrolling mid-swipe

BODY (3-4 short sentences — deliver on the hook's promise):
- Divine teaching, story, or blessing connected to real life (paisa, love, health, success)
- Max 12 words per sentence — keep it punchy
- Build the message progressively — each sentence escalates toward the payoff
- Example: "जब life में अँधेरा हो, [deity] कहते हैं — रुको मत। वो तूफ़ान नहीं, एक test है। और हर test के बाद एक नई शुरुआत होती है।"

ENDING (2-3 sentences — powerful close + CTA):
- First: deliver the final payoff / blessing — make it feel like a divine gift
- Then: deity battle cry ("जय महादेव!" / "जय श्री राम!" / "जय माता दी!" etc.)
- ALWAYS end with this CTA line (word-for-word):
  "Video पसंद आई तो Like करो, Share करो अपनों के साथ, और Subscribe करना मत भूलना। 🙏"

Script language: MIXED-SCRIPT HINGLISH
- Hindi / Urdu words → write in Devanagari script (देवनागरी)
- English words that have no natural Hindi equivalent → keep in Latin/English script
- No full Roman transliteration of Hindi words (e.g. write "जानते" not "jaante")
- The TTS voice is hi-IN-SwaraNeural — it reads Devanagari natively and handles English words naturally
- Conversational, like a friend talking — natural code-mixing as real Indians speak

MIXED-SCRIPT EXAMPLE (correct format):
  "क्या आप जानते हैं — Shiva का वो एक secret जो आपकी पूरी life बदल सकता है? अंत तक सुनो।
   जब life में सब कुछ टूटता लगे, Shiva कहते हैं — यही वो moment है जब असली शक्ति जन्म लेती है।
   मुश्किलें आपको तोड़ने नहीं, बल्कि और strong बनाने आती हैं।
   उनका आशीर्वाद हमेशा हमारे साथ है। जय महादेव!
   Video पसंद आई तो Like करो, Share करो अपनों के साथ, और Subscribe करना मत भूलना। 🙏"

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

HASHTAG BLOCK — EXACTLY 4-5 hashtags on the last line (no more — excess reduces reach):
  ⚠️ The FIRST 3 hashtags appear visibly ABOVE the video title on YouTube — choose carefully.
  ALWAYS pick from the curated trending list below — these are the top-performing
  Bhakti/Hindu hashtags driving reach on YouTube Shorts India right now.

  MANDATORY — always include these 2:
    #shorts        — triggers YouTube Shorts discovery (MUST be first)
    #bhakti        — top-performing devotional hashtag, highest reach in this niche

  DEITY HASHTAG — pick the ONE that matches this video's deity:
    Shiva/Mahadev  → #mahadev
    Krishna        → #krishna
    Ram            → #jaishriram
    Hanuman        → #hanuman
    Durga          → #maadurga
    Ganesha        → #ganesh
    Lakshmi        → #mahalakshmi
    Saraswati      → #saraswati
    Vishnu         → #vishnu

  OPTIONAL 4th/5th hashtag — pick 1-2 based on content theme (only if space allows):
    #sanatandharma  — philosophy/values content (fast-growing, high engagement)
    #hindudharma    — dharmic teaching content
    #spirituality   — broad spiritual theme
    #mantra         — if content references a mantra
    #bhajan         — if content references a bhajan/song
    #divineblessing — blessing/protection theme
    #hindushorts    — Hindi Shorts niche reach
    #motivation     — motivational message (use only if the script is motivational)

  ORDER: #shorts first, then deity hashtag, then #bhakti, then optional ones
  EXAMPLE: "#shorts #mahadev #bhakti #sanatandharma"

Max 120 words total (description + hashtags combined).

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TAGS RULES — 8-12 highly specific tags (2026 best practice):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT: Tags have minimal ranking impact in 2026. Their purpose is spelling variations
  and long-tail niche phrases. ALWAYS pick from the proven list below — no random generic words.

DO NOT use: "Motivation", "Viral", "trending", "Status", "HinduGods" — generic = wasted slots.

PICK 10-12 tags from this high-performing Bhakti tag bank, choosing the most relevant ones
for THIS video's deity and theme:

  DEITY VARIATIONS (include 3-4 for your deity):
    Shiva  → "shiva", "shiv", "mahadev", "bholenath", "har har mahadev", "lord shiva"
    Krishna → "krishna", "shri krishna", "radhe krishna", "hare krishna", "lord krishna"
    Ram    → "ram", "shri ram", "jai shri ram", "ramji", "lord ram", "ramayana"
    Hanuman → "hanuman", "bajrangbali", "hanuman chalisa", "jai hanuman", "lord hanuman"
    Durga  → "durga", "maa durga", "navratri", "jai mata di", "sherawali mata"
    Ganesha → "ganesh", "ganesha", "ganpati", "jai ganesh", "lord ganesha"
    Lakshmi → "lakshmi", "maa lakshmi", "mahalakshmi", "laxmi", "goddess lakshmi"
    Saraswati → "saraswati", "maa saraswati", "goddess saraswati", "vasant panchami"
    Vishnu → "vishnu", "lord vishnu", "narayan", "jai vishnu", "vaishnav"

  NICHE TAGS (include 3-4 that fit this video):
    "bhakti shorts"           — top-performing niche tag
    "bhakti status video"     — high search volume
    "hindi bhakti shorts"     — language+niche combo
    "hindu devotional shorts" — broad niche
    "sanatan dharma shorts"   — philosophy niche (growing fast)
    "spiritual hindi shorts"  — spiritual niche
    "hindu god shorts"        — deity content niche
    "bhajan status"           — if bhajan-related content
    "mantra shorts"           — if mantra-related content
    "hindu motivation"        — motivational bhakti content

  ALWAYS INCLUDE:
    "shorts"                  — platform tag (required)
    "bhakti"                  — top content category tag

Tags must be strings WITHOUT # symbol. Generate 10-12 tags total.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEARCH TERMS RULES (used to search Wikimedia, Unsplash, Pexels):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generate EXACTLY 5 search terms. Each term must be EXACTLY 2 English words.
These will be sent to real stock photo APIs — short, specific terms work best.

STRICT CONTENT RULES — MANDATORY:
⚠️ ALL search terms must return ONLY Hindu / Indian spiritual imagery.
FORBIDDEN — NEVER use any of these words or concepts in search terms:
  mosque, masjid, minar, minaret, islam, islamic, muslim, quran, namaz, prayer mat,
  crescent, hijab, burqa, arabic, arab, middle east, church, cross, cathedral, bible,
  christian, jesus, mary, pope, synagogue, jewish, jewish, halal, eid, ramadan.
If a term could accidentally return mosque/Islamic imagery (e.g. "india architecture"),
  replace it with a safer Hindu-specific term (e.g. "temple gopuram").

RULES:
- 2 words ONLY per term — APIs match better with concise phrases
- English only — Wikimedia, Unsplash and Pexels are English-indexed
- Use deity's English name (e.g. "shiva", "krishna", "hanuman") as word 1 for 3 terms
- Word 2 should show a DIFFERENT visual angle: meditation, temple, festival, portrait, devotion
- Include 1-2 SAFE Hindu spiritual fallbacks: "temple gopuram", "diwali lamps", "hindu festival",
  "incense smoke", "lotus flower", "india rangoli", "saffron flowers", "om symbol"
- NEVER use generic "india" alone or "india architecture" — too likely to surface mixed results

GOOD EXAMPLES:
  Shiva video   → ["shiva meditation", "shiva temple", "shiva statue", "temple gopuram", "diwali lamps"]
  Krishna video → ["krishna flute", "krishna devotion", "temple worship", "india festival", "lotus flower"]
  Durga video   → ["durga goddess", "navratri festival", "temple offerings", "india devotion", "diwali lamps"]
  Hanuman video → ["hanuman devotion", "hanuman temple", "hindu bhakti", "temple gopuram", "saffron flowers"]
  Ganesh video  → ["ganesha statue", "ganesh festival", "temple offering", "incense smoke", "om symbol"]

Generate completely fresh, unique content each time — different deity, different hook, different theme.
ALL metadata (title, description, tags) must be contextually consistent with each other and the script."""


def generate_video_content() -> dict:
    """Generate complete video content using Gemini 2.5 Flash.

    Uses a history file to avoid repeating deity+theme combos and injects
    a unique session seed so the model cannot return a cached response.
    """
    history = _load_history(_YOUTUBE_HISTORY_FILE)

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
    _save_to_history(history, f"{datetime.datetime.now().strftime('%Y-%m-%d')} | {title}", _YOUTUBE_HISTORY_FILE)

    return content


# ══════════════════════════════════════════════════════════════════════════════
# FACEBOOK-SPECIFIC CONTENT GENERATION
# ══════════════════════════════════════════════════════════════════════════════

_FB_SYSTEM_PROMPT = """You are an expert Indian Facebook Reels creator and social media growth specialist \
creating viral Hindu spirituality content for Indian Facebook audiences (ages 25-55).

Facebook is DIFFERENT from YouTube — apply Facebook-specific rules strictly.

Return ONLY valid JSON — no markdown fences, no extra text — in this exact structure:
{
  "title": "Internal tracking title — bilingual Hindi+English (rules below)",
  "script": "40-second Hinglish voiceover script (same rules as always)",
  "search_terms": [
    "deity scene1",
    "deity scene2",
    "deity scene3",
    "temple word1",
    "india word2"
  ],
  "description": "Facebook Reels caption (rules below — this IS the post text)",
  "tags": ["Facebook tags list — rules below"]
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TITLE RULES — internal label, bilingual:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
This title is for internal tracking only (not shown as a YouTube-style title on Facebook).
FORMAT: Short bilingual line — Hindi deity name + English topic hook
LENGTH: 60 characters max
EXAMPLES:
  "महादेव | Shiva's Secret That Changes Everything"
  "जय श्री राम | Ram's Blessing for Hard Times"
  "गणेश जी | Ganesha's Power — Listen Once"
  "दुर्गा माँ | Durga's Protection Mantra for Success"
NO hashtags in the title field — hashtags go in description only.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SCRIPT RULES — 40-second Hinglish voiceover (same as always):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Structure: HOOK (2s) → BODY (31s) → ENDING (7s)
Total: 90-110 words — mixed script Hinglish (Devanagari for Hindi words, Latin for English words).
HOOK — CRITICAL (viewer decides in 1.3 seconds — make it count):
Exactly 1 sentence, max 10 words. Start with the deity name OR the most emotionally charged word.
NO warmup phrases — go straight to the punch.
  Shocking truth: "[Deity] कहते हैं — जो टूट जाता है, वही सबसे तेज़ चमकता है।"
  Open loop:      "[Deity] का वो एक राज़ — जो 99% लोग नहीं जानते।"
  Direct call-out: "थक गए हो? [Deity] का एक message है तुम्हारे लिए।"
NEVER reveal the answer in the hook — create curiosity that only watching till end resolves.

BODY: 3-4 short punchy sentences — divine teaching tied to real life (money, health, love, success).
Build progressively — each sentence escalates toward the final payoff.

ENDING: Powerful close + deity battle cry ("जय महादेव!" / "जय श्री राम!" / "जय माता दी!")
ALWAYS finish with this CTA line (word-for-word):
  "Video पसंद आई तो Like करो, Share करो अपनों के साथ, और Subscribe करना मत भूलना। 🙏"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FACEBOOK CAPTION RULES — this is the full post text shown in the feed:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CRITICAL: The first 125 characters appear BEFORE the "See more" button.
  → Make line 1 the strongest hook. Viewer decides to watch in 2 seconds.

STRUCTURE (follow this exactly):
  Line 1 — HOOK (≤125 chars): 1-2 emojis + Hindi/bilingual emotional hook about this deity+topic
  Line 2-3 — BODY: 2 short sentences summarising the divine message of THIS video
  Line 4 — CTA: "👍 Like | ❤️ Share | 🔔 Follow करें और रोज़ नई भक्ति देखें"
  Line 5 — HASHTAGS: 5-8 tags on one line (rules below)

FACEBOOK CAPTION LANGUAGE:
  Natural bilingual mix — how real Indians write on Facebook.
  Hindi words in Devanagari, English words in Latin script.
  Example: "🙏 महादेव की यह शक्ति जानकर आप हैरान हो जाएंगे!
  जब life में सब कुछ गलत हो रहा हो, तब Shiva का यह message याद रखो।
  इस video को share करो — किसी की life बदल सकती है।
  👍 Like | ❤️ Share | 🔔 Follow करें और रोज़ नई भक्ति देखें
  #JaiMahadev #Bhakti #HinduDharma #Reels #Viral"

CAPTION LENGTH: 300-450 characters total — short captions get more shares on Facebook.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FACEBOOK HASHTAG RULES — 5-8 tags ONLY (fewer = more reach on Facebook):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT: Facebook's algorithm in 2026 PENALISES posts with 10+ hashtags.
  Use EXACTLY 5-8 hashtags — quality over quantity.
  Place ALL hashtags at the END of the caption on the last line.

MANDATORY (always include these 3):
  #Reels — triggers Facebook Reels distribution algorithm
  #Viral — boosts reach in the "trending" feed
  One deity tag — pick the EXACT one matching this video's deity (see list below)

DEITY HASHTAGS — pick ONE that matches:
  Shiva/Mahadev  → #JaiMahadev
  Krishna        → #JaiShriKrishna
  Ram            → #JaiShriRam
  Hanuman        → #JaiHanuman
  Durga          → #JaiMaaDurga
  Lakshmi        → #JaiMaaLakshmi
  Ganesha        → #JaiGanesha
  Saraswati      → #JaiMaaSaraswati
  Vishnu         → #JaiVishnu

TRENDING TOPIC HASHTAGS — pick 2-3 from this list based on video content:
  #Bhakti        — devotional content (highest reach for this niche)
  #HinduDharma   — Hindu philosophy/values
  #Spiritual     — broad spiritual audience
  #DivineBlessing — blessing/protection theme
  #Motivation    — motivational message
  #IndianCulture — cultural content
  #BhaktiSadhna  — dedicated devotees
  #HindiReels    — Hindi-speaking audience reach

AUDIENCE HASHTAG — include exactly ONE:
  #India  OR  #BharatMata  OR  #HindiContent

GOOD EXAMPLES (5-8 tags only):
  "#JaiMahadev #Bhakti #HinduDharma #Reels #Viral #India"                    (6 tags — Shiva)
  "#JaiShriRam #Bhakti #DivineBlessing #Reels #Viral #HindiReels"            (6 tags — Ram)
  "#JaiHanuman #Motivation #HinduDharma #Reels #Viral #BhaktiSadhna #India"  (7 tags — Hanuman)

NEVER use: #Shorts (YouTube-only), #HinduGod, #Status, #trending (generic, penalised)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TAGS FIELD RULES (API tags array — different from caption hashtags):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
The "tags" JSON field is for internal metadata only — NOT shown publicly on Facebook.
Generate 6-10 descriptive strings without # symbol, specific to this video's deity and theme.
Examples: ["mahadev blessing", "shiva motivation hindi", "hindu devotional reel", "bhakti content india"]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SEARCH TERMS RULES (for stock image APIs — same as always):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generate EXACTLY 5 search terms. Each term must be EXACTLY 2 English words.
Use deity's English name for 3 terms with different visual angles (meditation, temple, festival).

STRICT CONTENT RULES — MANDATORY:
⚠️ ALL search terms must return ONLY Hindu / Indian spiritual imagery.
FORBIDDEN — NEVER use any of these words in search terms:
  mosque, masjid, minar, minaret, islam, islamic, muslim, quran, namaz, crescent,
  hijab, burqa, arabic, arab, middle east, church, cross, cathedral, christian,
  jesus, mary, synagogue, jewish, halal, eid, ramadan.
Use SAFE Hindu-specific fallbacks only: "temple gopuram", "diwali lamps", "hindu festival",
  "incense smoke", "lotus flower", "india rangoli", "saffron flowers", "om symbol".
NEVER use generic "india architecture" — replace with "temple gopuram" or "hindu mandir".

Generate completely fresh, unique content each time — different deity, different hook, different theme.
ALL metadata must be contextually consistent with the script."""


def generate_facebook_video_content() -> dict:
    """Generate Facebook-optimised video content using Gemini 2.5 Flash.

    Uses a separate history file from YouTube so both platforms get unique content.
    Returns the same dict structure so the pipeline works without changes.
    """
    history = _load_history(_FACEBOOK_HISTORY_FILE)

    avoid_list = history[-5:] if history else []
    avoid_str = "; ".join(avoid_list) if avoid_list else "none yet"

    session_seed = (
        f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | "
        f"seed={random.randint(100_000, 999_999)}"
    )

    user_prompt = (
        f"Session: {session_seed}\n"
        f"Recently used deity+theme combos (DO NOT repeat any of these):\n"
        f"  {avoid_str}\n\n"
        f"Generate completely fresh Facebook Reels content with a DIFFERENT deity and DIFFERENT theme now."
    )

    response = _client.models.generate_content(
        model="gemini-2.5-flash",
        contents=[
            types.Content(role="user", parts=[types.Part(text=_FB_SYSTEM_PROMPT)]),
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

    if "```" in text:
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
    text = text.strip()

    start = text.find("{")
    end = text.rfind("}") + 1
    if start == -1 or end == 0:
        raise RuntimeError(f"No JSON object found in Gemini response:\n{text[:200]}")
    text = text[start:end]

    content = json.loads(text)

    content["tags"] = [t.lower() for t in content.get("tags", [])]

    # Guarantee exactly 5 search terms
    terms = content.get("search_terms", [])
    while len(terms) < 5:
        terms.append("india temple")
    content["search_terms"] = terms[:5]

    # Save to Facebook-only history
    title = content.get("title", "unknown")
    _save_to_history(history, f"{datetime.datetime.now().strftime('%Y-%m-%d')} | {title}", _FACEBOOK_HISTORY_FILE)

    return content
