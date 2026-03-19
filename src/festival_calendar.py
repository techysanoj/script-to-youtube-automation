"""Hindu Festival Calendar — 2026 & 2027

Sourced from drikpanchang.com (New Delhi, IST).
Used by script_generator.py to inject festival context when a major
Hindu festival falls within its awareness window.
"""

import datetime
from typing import Optional

# Default window: start making festival content N days before
WINDOW_DAYS_BEFORE = 7
# Default window: content still relevant N days after the festival
WINDOW_DAYS_AFTER = 1

FESTIVALS: list[dict] = [

    # ══════════════════════════════════════════════════════════════════════════
    # 2026
    # ══════════════════════════════════════════════════════════════════════════

    {
        "date": "2026-01-14",
        "name_en": "Makar Sankranti",
        "name_hi": "मकर संक्रांति",
        "deity_en": "Surya",
        "deity_hi": "सूर्य देव",
        "theme": "harvest festival, sun worship, end of winter, kite flying, tilgul sweets, sesame, new auspicious beginnings",
        "mood": "joyful, festive, renewal, auspicious",
        "script_guidance": (
            "Focus on Surya Bhagwan (Sun God) blessings for harvest, end of winter darkness, "
            "and new auspicious beginnings. Mention kite flying and tilgul tradition. "
            "Wish viewers 'मकर संक्रांति की हार्दिक शुभकामनाएं'."
        ),
        "search_terms": ["sankranti kite", "harvest festival", "india festival", "temple worship", "saffron flowers"],
        "extra_tags_youtube": ["makar sankranti", "sankranti", "happy makar sankranti", "sankranti 2026"],
        "extra_hashtags_youtube": ["#makarsankranti", "#sankranti", "#sankranti2026"],
        "extra_hashtags_facebook": ["#MakarSankranti", "#Sankranti", "#HappySankranti"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2026-01-23",
        "name_en": "Basant Panchami",
        "name_hi": "बसंत पंचमी",
        "deity_en": "Saraswati",
        "deity_hi": "माँ सरस्वती",
        "theme": "knowledge, wisdom, arts, music, spring arrival, yellow color, students blessings, education",
        "mood": "serene, joyful, devotional, spring awakening",
        "script_guidance": (
            "Focus on Maa Saraswati's blessings for students, artists, and musicians. "
            "The arrival of spring (Basant). Yellow color and its spiritual significance. "
            "Wish 'बसंत पंचमी की हार्दिक शुभकामनाएं' and 'जय माँ सरस्वती'."
        ),
        "search_terms": ["saraswati goddess", "spring flowers yellow", "india festival", "lotus flower", "temple puja"],
        "extra_tags_youtube": ["basant panchami", "saraswati puja", "vasant panchami", "saraswati vandana"],
        "extra_hashtags_youtube": ["#basantpanchami", "#saraswatipuja", "#vasantpanchami"],
        "extra_hashtags_facebook": ["#BasantPanchami", "#SaraswatiPuja", "#VasantPanchami"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2026-02-15",
        "name_en": "Mahashivratri",
        "name_hi": "महाशिवरात्रि",
        "deity_en": "Shiva",
        "deity_hi": "भगवान शिव",
        "theme": "great night of Shiva, fasting, jagran all night, bel patra, lingam puja, cosmic dance of Shiva, destruction of ego, liberation",
        "mood": "deeply spiritual, meditative, mystical, powerful, devotional",
        "script_guidance": (
            "Focus on Mahashivratri as the most sacred night for Shiva devotees. "
            "Fasting and all-night jagran. Shiva as the destroyer of ego and sins. "
            "Om Namah Shivay significance. The divine cosmic dance (Tandava). "
            "Wish 'महाशिवरात्रि की हार्दिक शुभकामनाएं' and 'हर हर महादेव'."
        ),
        "search_terms": ["shiva lingam puja", "shiva meditation night", "temple diya lamps", "shiva statue", "bel patra"],
        "extra_tags_youtube": ["mahashivratri", "maha shivratri", "shivratri 2026", "har har mahadev shivratri", "shivratri puja"],
        "extra_hashtags_youtube": ["#mahashivratri", "#shivratri", "#shivratri2026", "#harharmahadev"],
        "extra_hashtags_facebook": ["#MahaShivratri", "#Shivratri", "#Shivratri2026", "#HarHarMahadev"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2026-03-03",
        "name_en": "Holika Dahan",
        "name_hi": "होलिका दहन",
        "deity_en": "Vishnu",
        "deity_hi": "भगवान विष्णु",
        "theme": "victory of good over evil, Prahlad's devotion to Vishnu, Holika story, bonfire, protection of true devotees",
        "mood": "triumphant, devotional, protective, festive",
        "script_guidance": (
            "Focus on Prahlad's unshakeable devotion to Lord Vishnu and how Vishnu protected him. "
            "Holika Dahan as the burning of evil. Narasimha saving Prahlad. "
            "Wish 'होलिका दहन की शुभकामनाएं' and 'जय श्री हरि'."
        ),
        "search_terms": ["holika bonfire night", "holi festival india", "vishnu devotion", "india festival", "diya fire"],
        "extra_tags_youtube": ["holika dahan", "holi festival", "holika dahan 2026", "holi 2026"],
        "extra_hashtags_youtube": ["#holikadahan", "#holikadahan2026", "#holi2026"],
        "extra_hashtags_facebook": ["#HolikaDahan", "#HolikaDahan2026", "#Holi2026"],
        "window_before": 4,
        "window_after": 0,
    },
    {
        "date": "2026-03-04",
        "name_en": "Holi",
        "name_hi": "होली",
        "deity_en": "Krishna",
        "deity_hi": "भगवान श्रीकृष्ण",
        "theme": "festival of colors, Radha Krishna love, Braj Holi, spring celebration, joy, unity, forgiveness, gulal colors",
        "mood": "joyful, celebratory, loving, colorful, vibrant",
        "script_guidance": (
            "Focus on Holi as Krishna's festival of colors and love. Radha-Krishna Holi in Braj. "
            "Spiritual meaning of colors — red (love), yellow (prosperity), green (new beginnings). "
            "The joy of celebrating with loved ones. "
            "Wish viewers 'होली की हार्दिक शुभकामनाएं' and 'राधे राधे'."
        ),
        "search_terms": ["holi colors festival", "radha krishna holi", "india holi celebration", "gulal powder", "spring festival"],
        "extra_tags_youtube": ["holi", "happy holi", "holi 2026", "radha krishna holi", "braj holi", "holi festival"],
        "extra_hashtags_youtube": ["#holi", "#holi2026", "#happyholi", "#radhakrishna"],
        "extra_hashtags_facebook": ["#Holi", "#Holi2026", "#HappyHoli", "#RadhaKrishna"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-03-19",
        "name_en": "Chaitra Navratri",
        "name_hi": "चैत्र नवरात्रि",
        "deity_en": "Durga",
        "deity_hi": "माँ दुर्गा",
        "theme": "nine nights of Durga, nine divine forms, fasting, aarti, jagran, Shakti worship, garba dance, Hindu new year",
        "mood": "powerful, devotional, energetic, auspicious",
        "script_guidance": (
            "Focus on Chaitra Navratri as the nine-night celebration of Maa Durga's power. "
            "The nine forms of the goddess (Navadurga). Fasting, aarti, and jagran. "
            "Divine feminine energy (Shakti) that removes all obstacles. "
            "Wish 'नवरात्रि की हार्दिक शुभकामनाएं' and 'जय माता दी'."
        ),
        "search_terms": ["navratri durga puja", "maa durga goddess", "india navratri", "temple aarti", "garba dance"],
        "extra_tags_youtube": ["navratri", "chaitra navratri", "navratri 2026", "maa durga navratri", "jai mata di"],
        "extra_hashtags_youtube": ["#navratri", "#navratri2026", "#chaitranavratri", "#jaematadi"],
        "extra_hashtags_facebook": ["#Navratri", "#Navratri2026", "#ChaitraNavratri", "#JaiMataDi"],
        "window_before": 7,
        "window_after": 9,  # entire 9-day festival
    },
    {
        "date": "2026-03-26",
        "name_en": "Ram Navami",
        "name_hi": "राम नवमी",
        "deity_en": "Ram",
        "deity_hi": "भगवान श्री राम",
        "theme": "birthday of Lord Ram, Ramayana, Maryada Purushottam, ideal king, dharma, Ram Rajya, devotion",
        "mood": "devotional, pure, righteous, celebratory",
        "script_guidance": (
            "Focus on Ram Navami as Lord Ram's birthday. Ram as Maryada Purushottam — "
            "ideal son, husband, and king. The power of Ram's name. Ayodhya celebration. "
            "Wish 'राम नवमी की हार्दिक शुभकामनाएं' and 'जय श्री राम'."
        ),
        "search_terms": ["ram navami temple", "lord rama devotion", "ram temple ayodhya", "india festival", "aarti fire"],
        "extra_tags_youtube": ["ram navami", "ram navami 2026", "jai shri ram navami", "shri ram birthday"],
        "extra_hashtags_youtube": ["#ramnavami", "#ramnavami2026", "#jaishriram"],
        "extra_hashtags_facebook": ["#RamNavami", "#RamNavami2026", "#JaiShriRam"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2026-04-02",
        "name_en": "Hanuman Jayanti",
        "name_hi": "हनुमान जयंती",
        "deity_en": "Hanuman",
        "deity_hi": "भगवान हनुमान",
        "theme": "birthday of Hanuman, strength from devotion, Hanuman Chalisa, Ram bhakti, courage, protection, Bajrangbali",
        "mood": "powerful, devotional, energetic, courageous",
        "script_guidance": (
            "Focus on Hanuman Jayanti as the birthday of Ram's greatest devotee. "
            "Hanuman's superhuman strength born purely from devotion. Hanuman Chalisa's power. "
            "Bajrangbali as the protector of devotees. "
            "Wish 'हनुमान जयंती की हार्दिक शुभकामनाएं' and 'जय बजरंगबली'."
        ),
        "search_terms": ["hanuman temple prayer", "hanuman statue india", "india festival", "temple aarti", "devotion worship"],
        "extra_tags_youtube": ["hanuman jayanti", "hanuman jayanti 2026", "jai bajrangbali", "hanuman chalisa jayanti"],
        "extra_hashtags_youtube": ["#hanumanjayanti", "#hanumanjayanti2026", "#jaibajrangbali"],
        "extra_hashtags_facebook": ["#HanumanJayanti", "#HanumanJayanti2026", "#JaiBajrangBali"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2026-04-19",
        "name_en": "Akshaya Tritiya",
        "name_hi": "अक्षय तृतीया",
        "deity_en": "Lakshmi",
        "deity_hi": "माँ लक्ष्मी",
        "theme": "most auspicious day, inexhaustible merit, wealth, gold buying, prosperity, Lakshmi blessings, new beginnings",
        "mood": "auspicious, prosperous, celebratory, hopeful",
        "script_guidance": (
            "Focus on Akshaya Tritiya — 'Akshaya' means inexhaustible. "
            "Any good deed multiplies infinitely on this day. Maa Lakshmi's blessing for wealth. "
            "Gold and silver buying tradition for perpetual prosperity. "
            "Wish 'अक्षय तृतीया की हार्दिक शुभकामनाएं'."
        ),
        "search_terms": ["lakshmi goddess", "gold diwali lamps", "temple offerings", "lotus flower", "india festival"],
        "extra_tags_youtube": ["akshaya tritiya", "akshaya tritiya 2026", "akha teej", "akshaya tritiya wishes"],
        "extra_hashtags_youtube": ["#akshayatritiya", "#akshayatritiya2026", "#akhateej"],
        "extra_hashtags_facebook": ["#AkshayaTritiya", "#AkshayaTritiya2026", "#AkhaTeeJ"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-07-16",
        "name_en": "Rath Yatra",
        "name_hi": "रथ यात्रा",
        "deity_en": "Vishnu",
        "deity_hi": "भगवान जगन्नाथ",
        "theme": "chariot procession of Jagannath, Puri Odisha, moksha from pulling the chariot, Lord of the Universe",
        "mood": "joyful, devotional, communal, grand, celebratory",
        "script_guidance": (
            "Focus on Jagannath Rath Yatra — Vishnu as Jagannath (Lord of the Universe). "
            "The massive chariot procession in Puri. Moksha for those who see or pull the chariot. "
            "Wish 'रथ यात्रा की हार्दिक शुभकामनाएं' and 'जय जगन्नाथ'."
        ),
        "search_terms": ["jagannath temple puri", "india festival crowd", "chariot procession", "vishnu temple", "india devotion"],
        "extra_tags_youtube": ["rath yatra", "jagannath rath yatra", "rath yatra 2026", "jai jagannath"],
        "extra_hashtags_youtube": ["#rathyatra", "#rathyatra2026", "#jaijagannath"],
        "extra_hashtags_facebook": ["#RathYatra", "#RathYatra2026", "#JaiJagannath"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-07-29",
        "name_en": "Guru Purnima",
        "name_hi": "गुरु पूर्णिमा",
        "deity_en": "Vishnu",
        "deity_hi": "गुरु परम्परा",
        "theme": "honoring the Guru, Maharshi Vyasa, teacher-disciple tradition, gratitude, Guru's grace for liberation, darkness to light",
        "mood": "reverent, grateful, devotional, enlightened",
        "script_guidance": (
            "Focus on Guru Purnima as the day to honor the eternal Guru tradition. "
            "The Guru takes us from darkness to light. Maharshi Vyasa who compiled the Vedas. "
            "'गुरु ब्रह्मा, गुरु विष्णु, गुरु देवो महेश्वर'. "
            "Wish 'गुरु पूर्णिमा की हार्दिक शुभकामनाएं'."
        ),
        "search_terms": ["guru disciple india", "india spiritual teacher", "meditation lotus", "temple puja", "saffron flowers"],
        "extra_tags_youtube": ["guru purnima", "guru purnima 2026", "guru vandana", "guru purnima wishes"],
        "extra_hashtags_youtube": ["#gurupurnima", "#gurupurnima2026", "#guruvandana"],
        "extra_hashtags_facebook": ["#GuruPurnima", "#GuruPurnima2026", "#GuruVandana"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-08-17",
        "name_en": "Nag Panchami",
        "name_hi": "नाग पंचमी",
        "deity_en": "Shiva",
        "deity_hi": "नाग देवता",
        "theme": "serpent worship, Shiva and Vasuki, protection from all dangers, milk offerings, Nag Devata blessings",
        "mood": "respectful, protective, traditional, devotional",
        "script_guidance": (
            "Focus on Nag Panchami — worship of serpent gods connected to Lord Shiva (Vasuki around Shiva's neck). "
            "Protection from all dangers and fears. Milk offered to snakes. "
            "Wish 'नाग पंचमी की हार्दिक शुभकामनाएं' and 'हर हर महादेव'."
        ),
        "search_terms": ["shiva meditation", "india festival temple", "temple offering", "shiva statue", "india devotion"],
        "extra_tags_youtube": ["nag panchami", "nag panchami 2026", "nag devata", "nag panchami puja"],
        "extra_hashtags_youtube": ["#nagpanchami", "#nagpanchami2026", "#nagdevata"],
        "extra_hashtags_facebook": ["#NagPanchami", "#NagPanchami2026", "#NagDevata"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-09-04",
        "name_en": "Krishna Janmashtami",
        "name_hi": "कृष्ण जन्माष्टमी",
        "deity_en": "Krishna",
        "deity_hi": "भगवान श्रीकृष्ण",
        "theme": "Krishna's midnight birth, Mathura celebration, Dahi Handi, flute music, Radha Krishna love, Bhagavad Gita wisdom",
        "mood": "joyful, devotional, celebratory, midnight magical",
        "script_guidance": (
            "Focus on Krishna Janmashtami — Krishna's miraculous midnight birth in prison. "
            "Vasudeva crossing the Yamuna. Krishna's flute music and Radha's divine love. "
            "The Bhagavad Gita's eternal wisdom. Dahi Handi celebration. "
            "Wish 'जन्माष्टमी की हार्दिक शुभकामनाएं' and 'राधे राधे'."
        ),
        "search_terms": ["krishna flute devotion", "mathura temple krishna", "india festival night", "radha krishna love", "krishna statue"],
        "extra_tags_youtube": ["janmashtami", "krishna janmashtami", "janmashtami 2026", "happy janmashtami", "krishna birthday"],
        "extra_hashtags_youtube": ["#janmashtami", "#janmashtami2026", "#happyjanmashtami", "#radhekrishna"],
        "extra_hashtags_facebook": ["#Janmashtami", "#Janmashtami2026", "#HappyJanmashtami", "#RadheKrishna"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2026-09-14",
        "name_en": "Ganesh Chaturthi",
        "name_hi": "गणेश चतुर्थी",
        "deity_en": "Ganesha",
        "deity_hi": "भगवान गणेश",
        "theme": "Ganesha's birthday, 10-day festival, modak, obstacle removal, new beginnings, Ganpati Bappa Morya, prosperity",
        "mood": "joyful, festive, celebratory, devotional",
        "script_guidance": (
            "Focus on Ganesh Chaturthi as the beloved Ganapati's birthday. "
            "10-day celebration across India, especially Mumbai. Modak, aarti, immersion. "
            "Ganesha removes all obstacles and blesses new beginnings. "
            "Wish 'गणेश चतुर्थी की हार्दिक शुभकामनाएं' and 'गणपति बप्पा मोरया'."
        ),
        "search_terms": ["ganesha festival india", "ganesh idol celebration", "ganpati puja", "india festival crowd", "modak sweets"],
        "extra_tags_youtube": ["ganesh chaturthi", "ganesh chaturthi 2026", "ganapati bappa morya", "happy ganesh chaturthi"],
        "extra_hashtags_youtube": ["#ganeshchaturthi", "#ganeshchaturthi2026", "#ganpatibappamorya"],
        "extra_hashtags_facebook": ["#GaneshChaturthi", "#GaneshChaturthi2026", "#GanpatiBappaMorya"],
        "window_before": 7,
        "window_after": 3,
    },
    {
        "date": "2026-10-11",
        "name_en": "Sharad Navratri",
        "name_hi": "शारदीय नवरात्रि",
        "deity_en": "Durga",
        "deity_hi": "माँ दुर्गा",
        "theme": "nine forms of Durga, garba dandiya dance, fasting, Shakti worship, leading to Dussehra, Ram's victory over Ravana",
        "mood": "powerful, festive, devotional, energetic, celebratory",
        "script_guidance": (
            "Focus on Sharad Navratri — the biggest Navratri of the year. "
            "Nine nights of Maa Durga's nine forms. Garba and Dandiya dance all night. "
            "Culminates in Vijayadashami (Dussehra) — Ram's victory over Ravana. "
            "Wish 'नवरात्रि की हार्दिक शुभकामनाएं' and 'जय माता दी'."
        ),
        "search_terms": ["navratri garba dance", "maa durga goddess", "india navratri festival", "temple aarti diya", "dandiya celebration"],
        "extra_tags_youtube": ["navratri", "sharad navratri", "navratri 2026", "navratri garba", "jai mata di"],
        "extra_hashtags_youtube": ["#navratri", "#sharadnavratri", "#navratri2026", "#jaematadi", "#garba"],
        "extra_hashtags_facebook": ["#Navratri", "#SharadNavratri", "#Navratri2026", "#JaiMataDi", "#Garba"],
        "window_before": 7,
        "window_after": 9,
    },
    {
        "date": "2026-10-20",
        "name_en": "Dussehra",
        "name_hi": "दशहरा",
        "deity_en": "Ram",
        "deity_hi": "भगवान श्री राम",
        "theme": "Ram's victory over Ravana, Dharma over Adharma, truth over lies, Ravana Dahan, burn the Ravana within us",
        "mood": "triumphant, righteous, celebratory, victorious",
        "script_guidance": (
            "Focus on Dussehra as the eternal victory of Dharma over Adharma. "
            "Ram defeated Ravana — truth defeated ego. "
            "The message to burn the Ravana inside us (ego, anger, greed). "
            "Wish 'दशहरा की हार्दिक शुभकामनाएं' and 'जय श्री राम'."
        ),
        "search_terms": ["dussehra india festival", "ram temple celebration", "india festival crowd", "jai shri ram", "victory celebration"],
        "extra_tags_youtube": ["dussehra", "vijayadashami", "dussehra 2026", "jai shri ram dussehra", "ravana dahan"],
        "extra_hashtags_youtube": ["#dussehra", "#vijayadashami", "#dussehra2026", "#jaishriram"],
        "extra_hashtags_facebook": ["#Dussehra", "#Vijayadashami", "#Dussehra2026", "#JaiShriRam"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-10-29",
        "name_en": "Karva Chauth",
        "name_hi": "करवा चौथ",
        "deity_en": "Shiva",
        "deity_hi": "भगवान शिव और माँ पार्वती",
        "theme": "wife's devotion for husband's long life, Shiva-Parvati love, moon sighting ritual, marital bond, karva puja",
        "mood": "romantic, devotional, loving, traditional, tender",
        "script_guidance": (
            "Focus on Karva Chauth as the celebration of marital love and devotion. "
            "Shiva-Parvati as the ideal couple. Fasting all day until the moon rises. "
            "The spiritual power of a wife's love and prayer. "
            "Wish 'करवा चौथ की हार्दिक शुभकामनाएं'."
        ),
        "search_terms": ["karva chauth moon", "parvati shiva love", "india women festival", "diya lamp night", "india devotion"],
        "extra_tags_youtube": ["karva chauth", "karva chauth 2026", "karva chauth wishes", "karwa chauth"],
        "extra_hashtags_youtube": ["#karvachauth", "#karvachauth2026", "#karvachauthwishes"],
        "extra_hashtags_facebook": ["#KarvaChauth", "#KarvaChauth2026", "#KarwaChauthWishes"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-11-06",
        "name_en": "Dhanteras",
        "name_hi": "धनतेरस",
        "deity_en": "Lakshmi",
        "deity_hi": "माँ लक्ष्मी",
        "theme": "wealth and prosperity, gold and silver buying, Dhanvantari god of medicine, Lakshmi puja, beginning of Diwali",
        "mood": "auspicious, prosperous, celebratory, festive",
        "script_guidance": (
            "Focus on Dhanteras — the start of the Diwali festival. "
            "Dhanvantari emerging from the ocean with divine medicine. "
            "Maa Lakshmi's blessings for wealth and health. Gold buying for eternal prosperity. "
            "Wish 'धनतेरस की हार्दिक शुभकामनाएं'."
        ),
        "search_terms": ["dhanteras lakshmi puja", "diwali gold lamps", "lakshmi goddess", "diya lamp rangoli", "india diwali"],
        "extra_tags_youtube": ["dhanteras", "dhanteras 2026", "happy dhanteras", "dhanteras puja", "dhanteras wishes"],
        "extra_hashtags_youtube": ["#dhanteras", "#dhanteras2026", "#happydhanteras"],
        "extra_hashtags_facebook": ["#Dhanteras", "#Dhanteras2026", "#HappyDhanteras"],
        "window_before": 5,
        "window_after": 0,
    },
    {
        "date": "2026-11-08",
        "name_en": "Diwali",
        "name_hi": "दीपावली",
        "deity_en": "Lakshmi",
        "deity_hi": "माँ लक्ष्मी",
        "theme": "festival of lights, Lakshmi puja, Ram's return to Ayodhya, diyas and fireworks, light over darkness, wealth blessings",
        "mood": "joyful, magical, celebratory, auspicious, warm",
        "script_guidance": (
            "Focus on Diwali as the greatest festival of lights. "
            "Maa Lakshmi enters homes filled with light and happiness. "
            "Ram's return to Ayodhya after 14 years — the victory of light over darkness. "
            "Diyas symbolize knowledge destroying ignorance. "
            "Wish 'दीपावली की हार्दिक शुभकामनाएं' and 'शुभ दीपावली'."
        ),
        "search_terms": ["diwali diyas lights", "lakshmi puja diwali", "india diwali festival", "diya rangoli colorful", "diwali celebration"],
        "extra_tags_youtube": ["diwali", "diwali 2026", "happy diwali", "deepawali", "lakshmi puja diwali", "shubh diwali"],
        "extra_hashtags_youtube": ["#diwali", "#diwali2026", "#happydiwali", "#deepawali", "#shubhdiwali"],
        "extra_hashtags_facebook": ["#Diwali", "#Diwali2026", "#HappyDiwali", "#Deepawali"],
        "window_before": 7,
        "window_after": 2,
    },
    {
        "date": "2026-11-11",
        "name_en": "Bhai Dooj",
        "name_hi": "भाई दूज",
        "deity_en": "Vishnu",
        "deity_hi": "भाई-बहन का पवित्र बंधन",
        "theme": "sibling love, brother-sister bond, Yama-Yamuna story, tilak ceremony, sister's prayer for brother's long life",
        "mood": "warm, loving, familial, traditional, joyful",
        "script_guidance": (
            "Focus on Bhai Dooj as the divine celebration of sibling love. "
            "The Yama-Yamuna story — Yamuna's prayer for her brother Yama. "
            "Sister's tilak for brother's long and healthy life. "
            "Wish 'भाई दूज की हार्दिक शुभकामनाएं'."
        ),
        "search_terms": ["sibling festival india", "india family festival", "diwali lamps", "india celebration", "saffron flowers"],
        "extra_tags_youtube": ["bhai dooj", "bhai dooj 2026", "bhai dooj wishes", "bhai dooj tilak"],
        "extra_hashtags_youtube": ["#bhaidooj", "#bhaidooj2026", "#bhaidoojwishes"],
        "extra_hashtags_facebook": ["#BhaiDooj", "#BhaiDooj2026", "#BhaiDoojWishes"],
        "window_before": 3,
        "window_after": 1,
    },
    {
        "date": "2026-11-24",
        "name_en": "Dev Deepawali",
        "name_hi": "देव दीपावली",
        "deity_en": "Vishnu",
        "deity_hi": "समस्त देव",
        "theme": "Diwali of the Gods, Kartik Purnima, Varanasi Ganga aarti, millions of diyas on Ghats, all Devas descend",
        "mood": "magical, divine, spiritual, grand, luminous",
        "script_guidance": (
            "Focus on Dev Deepawali — when the Gods themselves celebrate Diwali. "
            "The entire Ganga Ghat in Varanasi lit with millions of diyas. "
            "Kartik Purnima — Lord Vishnu and all Devas descend to bathe in the Ganga. "
            "Wish 'देव दीपावली की हार्दिक शुभकामनाएं'."
        ),
        "search_terms": ["ganga aarti varanasi", "india diwali lamps", "india festival night", "ghat diya lights", "india devotion"],
        "extra_tags_youtube": ["dev deepawali", "dev diwali", "dev deepawali 2026", "kartik purnima", "varanasi dev deepawali"],
        "extra_hashtags_youtube": ["#devdeepa​wali", "#devdiwali", "#kartikpurnima", "#devdeepa​wali2026"],
        "extra_hashtags_facebook": ["#DevDeepa​wali", "#DevDiwali", "#KartikPurnima", "#DevDeepa​wali2026"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2026-12-14",
        "name_en": "Vivah Panchami",
        "name_hi": "विवाह पंचमी",
        "deity_en": "Ram",
        "deity_hi": "भगवान श्री राम और माँ सीता",
        "theme": "Ram and Sita's sacred wedding anniversary, Ramayana, ideal marriage, divine love, Sita Ram devotion",
        "mood": "devotional, romantic, auspicious, celebratory",
        "script_guidance": (
            "Focus on Vivah Panchami as the sacred wedding anniversary of Lord Ram and Maa Sita. "
            "Ram-Sita as the ideal couple — pure love and unwavering devotion. "
            "Ramayana's teaching about love and sacrifice. "
            "Wish 'विवाह पंचमी की हार्दिक शुभकामनाएं' and 'जय सियाराम'."
        ),
        "search_terms": ["ram temple ayodhya", "india festival temple", "lotus flower devotion", "temple aarti", "india devotion"],
        "extra_tags_youtube": ["vivah panchami", "vivah panchami 2026", "jai siya ram", "ram sita vivah", "sita ram bhakti"],
        "extra_hashtags_youtube": ["#vivahpanchami", "#vivahpanchami2026", "#jaishriram", "#ramsita"],
        "extra_hashtags_facebook": ["#VivahPanchami", "#VivahPanchami2026", "#JaiSiyaRam", "#RamSita"],
        "window_before": 5,
        "window_after": 1,
    },

    # ══════════════════════════════════════════════════════════════════════════
    # 2027
    # ══════════════════════════════════════════════════════════════════════════

    {
        "date": "2027-01-15",
        "name_en": "Makar Sankranti",
        "name_hi": "मकर संक्रांति",
        "deity_en": "Surya",
        "deity_hi": "सूर्य देव",
        "theme": "harvest festival, sun worship, end of winter, kite flying, tilgul sweets, sesame, new auspicious beginnings",
        "mood": "joyful, festive, renewal, auspicious",
        "script_guidance": "Focus on Surya Bhagwan's blessings, harvest season, end of winter darkness. Wish 'मकर संक्रांति की हार्दिक शुभकामनाएं'.",
        "search_terms": ["sankranti kite", "harvest festival", "india festival", "temple worship", "saffron flowers"],
        "extra_tags_youtube": ["makar sankranti", "sankranti", "happy makar sankranti", "sankranti 2027"],
        "extra_hashtags_youtube": ["#makarsankranti", "#sankranti", "#sankranti2027"],
        "extra_hashtags_facebook": ["#MakarSankranti", "#Sankranti", "#HappySankranti"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2027-02-11",
        "name_en": "Basant Panchami",
        "name_hi": "बसंत पंचमी",
        "deity_en": "Saraswati",
        "deity_hi": "माँ सरस्वती",
        "theme": "knowledge, wisdom, arts, music, spring arrival, yellow color, students and education blessings",
        "mood": "serene, joyful, devotional, spring awakening",
        "script_guidance": "Focus on Maa Saraswati's blessings for students and artists. Spring arrival. Wish 'बसंत पंचमी की हार्दिक शुभकामनाएं'.",
        "search_terms": ["saraswati goddess", "spring flowers yellow", "india festival", "lotus flower", "temple puja"],
        "extra_tags_youtube": ["basant panchami", "saraswati puja", "vasant panchami 2027"],
        "extra_hashtags_youtube": ["#basantpanchami", "#saraswatipuja", "#vasantpanchami2027"],
        "extra_hashtags_facebook": ["#BasantPanchami", "#SaraswatiPuja", "#VasantPanchami2027"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2027-03-06",
        "name_en": "Mahashivratri",
        "name_hi": "महाशिवरात्रि",
        "deity_en": "Shiva",
        "deity_hi": "भगवान शिव",
        "theme": "great night of Shiva, fasting, jagran, bel patra, lingam puja, cosmic Tandava, destruction of ego, liberation",
        "mood": "deeply spiritual, meditative, mystical, powerful, devotional",
        "script_guidance": "Focus on the sacred night of Shiva. Fasting, jagran, Om Namah Shivay. Wish 'महाशिवरात्रि की हार्दिक शुभकामनाएं' and 'हर हर महादेव'.",
        "search_terms": ["shiva lingam puja", "shiva meditation night", "temple diya lamps", "shiva statue", "india devotion"],
        "extra_tags_youtube": ["mahashivratri", "maha shivratri", "shivratri 2027", "har har mahadev shivratri"],
        "extra_hashtags_youtube": ["#mahashivratri", "#shivratri", "#shivratri2027", "#harharmahadev"],
        "extra_hashtags_facebook": ["#MahaShivratri", "#Shivratri", "#Shivratri2027", "#HarHarMahadev"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2027-03-22",
        "name_en": "Holi",
        "name_hi": "होली",
        "deity_en": "Krishna",
        "deity_hi": "भगवान श्रीकृष्ण",
        "theme": "festival of colors, Radha Krishna love, Braj Holi, spring celebration, joy, unity, forgiveness, gulal",
        "mood": "joyful, celebratory, loving, colorful, vibrant",
        "script_guidance": "Focus on Holi as Krishna's festival of colors. Radha-Krishna Holi in Braj. Wish 'होली की हार्दिक शुभकामनाएं' and 'राधे राधे'.",
        "search_terms": ["holi colors festival", "radha krishna holi", "india holi celebration", "gulal powder", "spring festival"],
        "extra_tags_youtube": ["holi", "happy holi", "holi 2027", "radha krishna holi", "braj holi"],
        "extra_hashtags_youtube": ["#holi", "#holi2027", "#happyholi", "#radhakrishna"],
        "extra_hashtags_facebook": ["#Holi", "#Holi2027", "#HappyHoli", "#RadhaKrishna"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-04-07",
        "name_en": "Chaitra Navratri",
        "name_hi": "चैत्र नवरात्रि",
        "deity_en": "Durga",
        "deity_hi": "माँ दुर्गा",
        "theme": "nine nights of Durga, nine divine forms, fasting, aarti, jagran, Shakti worship, Hindu new year",
        "mood": "powerful, devotional, energetic, auspicious",
        "script_guidance": "Focus on nine-night Maa Durga celebration. Navadurga forms. Wish 'नवरात्रि की हार्दिक शुभकामनाएं' and 'जय माता दी'.",
        "search_terms": ["navratri durga puja", "maa durga goddess", "india navratri", "temple aarti", "garba dance"],
        "extra_tags_youtube": ["navratri", "chaitra navratri 2027", "maa durga navratri", "jai mata di"],
        "extra_hashtags_youtube": ["#navratri", "#navratri2027", "#chaitranavratri", "#jaematadi"],
        "extra_hashtags_facebook": ["#Navratri", "#Navratri2027", "#ChaitraNavratri", "#JaiMataDi"],
        "window_before": 7,
        "window_after": 9,
    },
    {
        "date": "2027-04-15",
        "name_en": "Ram Navami",
        "name_hi": "राम नवमी",
        "deity_en": "Ram",
        "deity_hi": "भगवान श्री राम",
        "theme": "birthday of Lord Ram, Ramayana, Maryada Purushottam, ideal king, dharma, Ram Rajya",
        "mood": "devotional, pure, righteous, celebratory",
        "script_guidance": "Focus on Ram Navami as Lord Ram's birthday. Ram as ideal son, husband, king. Wish 'राम नवमी की हार्दिक शुभकामनाएं' and 'जय श्री राम'.",
        "search_terms": ["ram navami temple", "lord rama devotion", "ram temple ayodhya", "india festival", "aarti fire"],
        "extra_tags_youtube": ["ram navami", "ram navami 2027", "jai shri ram navami"],
        "extra_hashtags_youtube": ["#ramnavami", "#ramnavami2027", "#jaishriram"],
        "extra_hashtags_facebook": ["#RamNavami", "#RamNavami2027", "#JaiShriRam"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2027-04-20",
        "name_en": "Hanuman Jayanti",
        "name_hi": "हनुमान जयंती",
        "deity_en": "Hanuman",
        "deity_hi": "भगवान हनुमान",
        "theme": "birthday of Hanuman, strength from devotion, Hanuman Chalisa, Ram bhakti, courage, protection",
        "mood": "powerful, devotional, energetic, courageous",
        "script_guidance": "Focus on Hanuman Jayanti. Hanuman's devotion-born strength. Hanuman Chalisa power. Wish 'हनुमान जयंती की हार्दिक शुभकामनाएं' and 'जय बजरंगबली'.",
        "search_terms": ["hanuman temple prayer", "hanuman statue india", "india festival", "temple aarti", "devotion worship"],
        "extra_tags_youtube": ["hanuman jayanti", "hanuman jayanti 2027", "jai bajrangbali"],
        "extra_hashtags_youtube": ["#hanumanjayanti", "#hanumanjayanti2027", "#jaibajrangbali"],
        "extra_hashtags_facebook": ["#HanumanJayanti", "#HanumanJayanti2027", "#JaiBajrangBali"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2027-05-09",
        "name_en": "Akshaya Tritiya",
        "name_hi": "अक्षय तृतीया",
        "deity_en": "Lakshmi",
        "deity_hi": "माँ लक्ष्मी",
        "theme": "most auspicious day, inexhaustible merit, wealth, gold buying, prosperity, Lakshmi blessings",
        "mood": "auspicious, prosperous, celebratory, hopeful",
        "script_guidance": "Focus on Akshaya Tritiya — inexhaustible merit day. Maa Lakshmi's blessing for wealth. Wish 'अक्षय तृतीया की हार्दिक शुभकामनाएं'.",
        "search_terms": ["lakshmi goddess", "gold diwali lamps", "temple offerings", "lotus flower", "india festival"],
        "extra_tags_youtube": ["akshaya tritiya", "akshaya tritiya 2027", "akha teej 2027"],
        "extra_hashtags_youtube": ["#akshayatritiya", "#akshayatritiya2027", "#akhateej"],
        "extra_hashtags_facebook": ["#AkshayaTritiya", "#AkshayaTritiya2027", "#AkhaTeeJ"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-07-05",
        "name_en": "Rath Yatra",
        "name_hi": "रथ यात्रा",
        "deity_en": "Vishnu",
        "deity_hi": "भगवान जगन्नाथ",
        "theme": "chariot procession of Jagannath, Puri Odisha, moksha, Lord of the Universe",
        "mood": "joyful, devotional, communal, grand",
        "script_guidance": "Focus on Jagannath Rath Yatra chariot procession. Moksha for devotees. Wish 'रथ यात्रा की हार्दिक शुभकामनाएं' and 'जय जगन्नाथ'.",
        "search_terms": ["jagannath temple puri", "india festival crowd", "vishnu temple", "india devotion", "chariot procession"],
        "extra_tags_youtube": ["rath yatra", "jagannath rath yatra", "rath yatra 2027", "jai jagannath"],
        "extra_hashtags_youtube": ["#rathyatra", "#rathyatra2027", "#jaijagannath"],
        "extra_hashtags_facebook": ["#RathYatra", "#RathYatra2027", "#JaiJagannath"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-07-18",
        "name_en": "Guru Purnima",
        "name_hi": "गुरु पूर्णिमा",
        "deity_en": "Vishnu",
        "deity_hi": "गुरु परम्परा",
        "theme": "honoring the Guru, Maharshi Vyasa, teacher-disciple tradition, gratitude, Guru's grace",
        "mood": "reverent, grateful, devotional, enlightened",
        "script_guidance": "Focus on Guru Purnima honoring the Guru tradition. Darkness to light. Wish 'गुरु पूर्णिमा की हार्दिक शुभकामनाएं'.",
        "search_terms": ["guru disciple india", "india spiritual teacher", "meditation lotus", "temple puja", "saffron flowers"],
        "extra_tags_youtube": ["guru purnima", "guru purnima 2027", "guru vandana"],
        "extra_hashtags_youtube": ["#gurupurnima", "#gurupurnima2027", "#guruvandana"],
        "extra_hashtags_facebook": ["#GuruPurnima", "#GuruPurnima2027", "#GuruVandana"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-08-06",
        "name_en": "Nag Panchami",
        "name_hi": "नाग पंचमी",
        "deity_en": "Shiva",
        "deity_hi": "नाग देवता",
        "theme": "serpent worship, Shiva and Vasuki, protection from dangers, milk offerings",
        "mood": "respectful, protective, traditional, devotional",
        "script_guidance": "Focus on Nag Panchami serpent worship connected to Shiva. Wish 'नाग पंचमी की हार्दिक शुभकामनाएं'.",
        "search_terms": ["shiva meditation", "india festival temple", "temple offering", "shiva statue", "india devotion"],
        "extra_tags_youtube": ["nag panchami", "nag panchami 2027", "nag devata"],
        "extra_hashtags_youtube": ["#nagpanchami", "#nagpanchami2027", "#nagdevata"],
        "extra_hashtags_facebook": ["#NagPanchami", "#NagPanchami2027", "#NagDevata"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-08-25",
        "name_en": "Krishna Janmashtami",
        "name_hi": "कृष्ण जन्माष्टमी",
        "deity_en": "Krishna",
        "deity_hi": "भगवान श्रीकृष्ण",
        "theme": "Krishna's midnight birth, Mathura, Dahi Handi, Radha Krishna love, Bhagavad Gita wisdom",
        "mood": "joyful, devotional, celebratory, midnight magical",
        "script_guidance": "Focus on Krishna's miraculous midnight birth. Radha-Krishna love. Bhagavad Gita wisdom. Wish 'जन्माष्टमी की हार्दिक शुभकामनाएं' and 'राधे राधे'.",
        "search_terms": ["krishna flute devotion", "mathura temple krishna", "india festival night", "radha krishna love", "krishna statue"],
        "extra_tags_youtube": ["janmashtami", "krishna janmashtami", "janmashtami 2027", "happy janmashtami"],
        "extra_hashtags_youtube": ["#janmashtami", "#janmashtami2027", "#happyjanmashtami", "#radhekrishna"],
        "extra_hashtags_facebook": ["#Janmashtami", "#Janmashtami2027", "#HappyJanmashtami", "#RadheKrishna"],
        "window_before": 7,
        "window_after": 1,
    },
    {
        "date": "2027-09-04",
        "name_en": "Ganesh Chaturthi",
        "name_hi": "गणेश चतुर्थी",
        "deity_en": "Ganesha",
        "deity_hi": "भगवान गणेश",
        "theme": "Ganesha's birthday, 10-day festival, modak, obstacle removal, new beginnings, Ganpati Bappa Morya",
        "mood": "joyful, festive, celebratory, devotional",
        "script_guidance": "Focus on Ganapati's birthday. 10-day celebration. Obstacle removal blessings. Wish 'गणेश चतुर्थी की हार्दिक शुभकामनाएं' and 'गणपति बप्पा मोरया'.",
        "search_terms": ["ganesha festival india", "ganesh idol celebration", "ganpati puja", "india festival crowd", "modak sweets"],
        "extra_tags_youtube": ["ganesh chaturthi", "ganesh chaturthi 2027", "ganapati bappa morya"],
        "extra_hashtags_youtube": ["#ganeshchaturthi", "#ganeshchaturthi2027", "#ganpatibappamorya"],
        "extra_hashtags_facebook": ["#GaneshChaturthi", "#GaneshChaturthi2027", "#GanpatiBappaMorya"],
        "window_before": 7,
        "window_after": 3,
    },
    {
        "date": "2027-09-30",
        "name_en": "Sharad Navratri",
        "name_hi": "शारदीय नवरात्रि",
        "deity_en": "Durga",
        "deity_hi": "माँ दुर्गा",
        "theme": "nine forms of Durga, garba dandiya, fasting, Shakti worship, leading to Dussehra",
        "mood": "powerful, festive, devotional, energetic",
        "script_guidance": "Focus on Sharad Navratri nine-night Durga celebration. Garba and Dandiya. Wish 'नवरात्रि की हार्दिक शुभकामनाएं' and 'जय माता दी'.",
        "search_terms": ["navratri garba dance", "maa durga goddess", "india navratri festival", "temple aarti diya", "dandiya celebration"],
        "extra_tags_youtube": ["navratri", "sharad navratri", "navratri 2027", "navratri garba", "jai mata di"],
        "extra_hashtags_youtube": ["#navratri", "#sharadnavratri", "#navratri2027", "#jaematadi"],
        "extra_hashtags_facebook": ["#Navratri", "#SharadNavratri", "#Navratri2027", "#JaiMataDi"],
        "window_before": 7,
        "window_after": 9,
    },
    {
        "date": "2027-10-09",
        "name_en": "Dussehra",
        "name_hi": "दशहरा",
        "deity_en": "Ram",
        "deity_hi": "भगवान श्री राम",
        "theme": "Ram's victory over Ravana, Dharma over Adharma, truth over lies, Ravana Dahan, burn ego within",
        "mood": "triumphant, righteous, celebratory, victorious",
        "script_guidance": "Focus on Dussehra — eternal victory of Dharma over Adharma. Burn the Ravana inside us. Wish 'दशहरा की हार्दिक शुभकामनाएं' and 'जय श्री राम'.",
        "search_terms": ["dussehra india festival", "ram temple celebration", "india festival crowd", "victory celebration", "india devotion"],
        "extra_tags_youtube": ["dussehra", "vijayadashami", "dussehra 2027", "jai shri ram dussehra"],
        "extra_hashtags_youtube": ["#dussehra", "#vijayadashami", "#dussehra2027", "#jaishriram"],
        "extra_hashtags_facebook": ["#Dussehra", "#Vijayadashami", "#Dussehra2027", "#JaiShriRam"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-10-18",
        "name_en": "Karva Chauth",
        "name_hi": "करवा चौथ",
        "deity_en": "Shiva",
        "deity_hi": "भगवान शिव और माँ पार्वती",
        "theme": "wife's devotion for husband's long life, Shiva-Parvati love, moon sighting ritual, marital bond",
        "mood": "romantic, devotional, loving, traditional",
        "script_guidance": "Focus on Karva Chauth marital love and Shiva-Parvati devotion. Wish 'करवा चौथ की हार्दिक शुभकामनाएं'.",
        "search_terms": ["karva chauth moon", "parvati shiva love", "india women festival", "diya lamp night", "india devotion"],
        "extra_tags_youtube": ["karva chauth", "karva chauth 2027", "karwa chauth 2027"],
        "extra_hashtags_youtube": ["#karvachauth", "#karvachauth2027", "#karvachauthwishes"],
        "extra_hashtags_facebook": ["#KarvaChauth", "#KarvaChauth2027", "#KarwaChauthWishes"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-10-27",
        "name_en": "Dhanteras",
        "name_hi": "धनतेरस",
        "deity_en": "Lakshmi",
        "deity_hi": "माँ लक्ष्मी",
        "theme": "wealth and prosperity, gold buying, Dhanvantari, Lakshmi puja, beginning of Diwali",
        "mood": "auspicious, prosperous, celebratory, festive",
        "script_guidance": "Focus on Dhanteras Diwali start. Lakshmi's wealth blessings. Dhanvantari health blessings. Wish 'धनतेरस की हार्दिक शुभकामनाएं'.",
        "search_terms": ["dhanteras lakshmi puja", "diwali gold lamps", "lakshmi goddess", "diya lamp rangoli", "india diwali"],
        "extra_tags_youtube": ["dhanteras", "dhanteras 2027", "happy dhanteras"],
        "extra_hashtags_youtube": ["#dhanteras", "#dhanteras2027", "#happydhanteras"],
        "extra_hashtags_facebook": ["#Dhanteras", "#Dhanteras2027", "#HappyDhanteras"],
        "window_before": 5,
        "window_after": 0,
    },
    {
        "date": "2027-10-29",
        "name_en": "Diwali",
        "name_hi": "दीपावली",
        "deity_en": "Lakshmi",
        "deity_hi": "माँ लक्ष्मी",
        "theme": "festival of lights, Lakshmi puja, Ram's return, diyas and fireworks, light over darkness, wealth blessings",
        "mood": "joyful, magical, celebratory, auspicious, warm",
        "script_guidance": "Focus on Diwali festival of lights. Maa Lakshmi's blessings. Light over darkness. Wish 'दीपावली की हार्दिक शुभकामनाएं' and 'शुभ दीपावली'.",
        "search_terms": ["diwali diyas lights", "lakshmi puja diwali", "india diwali festival", "diya rangoli colorful", "diwali celebration"],
        "extra_tags_youtube": ["diwali", "diwali 2027", "happy diwali", "deepawali 2027"],
        "extra_hashtags_youtube": ["#diwali", "#diwali2027", "#happydiwali", "#deepawali"],
        "extra_hashtags_facebook": ["#Diwali", "#Diwali2027", "#HappyDiwali", "#Deepawali"],
        "window_before": 7,
        "window_after": 2,
    },
    {
        "date": "2027-10-31",
        "name_en": "Bhai Dooj",
        "name_hi": "भाई दूज",
        "deity_en": "Vishnu",
        "deity_hi": "भाई-बहन का पवित्र बंधन",
        "theme": "sibling love, brother-sister bond, Yama-Yamuna story, tilak ceremony",
        "mood": "warm, loving, familial, traditional, joyful",
        "script_guidance": "Focus on Bhai Dooj sibling bond. Sister's tilak for brother. Wish 'भाई दूज की हार्दिक शुभकामनाएं'.",
        "search_terms": ["sibling festival india", "india family festival", "diwali lamps", "india celebration", "saffron flowers"],
        "extra_tags_youtube": ["bhai dooj", "bhai dooj 2027", "bhai dooj wishes"],
        "extra_hashtags_youtube": ["#bhaidooj", "#bhaidooj2027", "#bhaidoojwishes"],
        "extra_hashtags_facebook": ["#BhaiDooj", "#BhaiDooj2027", "#BhaiDoojWishes"],
        "window_before": 3,
        "window_after": 1,
    },
    {
        "date": "2027-11-13",
        "name_en": "Dev Deepawali",
        "name_hi": "देव दीपावली",
        "deity_en": "Vishnu",
        "deity_hi": "समस्त देव",
        "theme": "Diwali of the Gods, Kartik Purnima, Varanasi Ganga aarti, millions of diyas, all Devas descend",
        "mood": "magical, divine, spiritual, grand, luminous",
        "script_guidance": "Focus on Dev Deepawali — Gods celebrate Diwali. Varanasi Ganga Ghat lit with millions of diyas. Wish 'देव दीपावली की हार्दिक शुभकामनाएं'.",
        "search_terms": ["ganga aarti varanasi", "india diwali lamps", "india festival night", "ghat diya lights", "india devotion"],
        "extra_tags_youtube": ["dev deepawali", "dev diwali", "dev deepawali 2027", "kartik purnima"],
        "extra_hashtags_youtube": ["#devdeepa​wali", "#devdiwali", "#kartikpurnima", "#devdeepa​wali2027"],
        "extra_hashtags_facebook": ["#DevDeepa​wali", "#DevDiwali", "#KartikPurnima"],
        "window_before": 5,
        "window_after": 1,
    },
    {
        "date": "2027-12-03",
        "name_en": "Vivah Panchami",
        "name_hi": "विवाह पंचमी",
        "deity_en": "Ram",
        "deity_hi": "भगवान श्री राम और माँ सीता",
        "theme": "Ram-Sita sacred wedding anniversary, Ramayana, ideal marriage, divine love, Sita Ram devotion",
        "mood": "devotional, romantic, auspicious, celebratory",
        "script_guidance": "Focus on Ram-Sita wedding anniversary. Divine love and devotion. Wish 'विवाह पंचमी की हार्दिक शुभकामनाएं' and 'जय सियाराम'.",
        "search_terms": ["ram temple ayodhya", "india festival temple", "lotus flower devotion", "temple aarti", "india devotion"],
        "extra_tags_youtube": ["vivah panchami", "vivah panchami 2027", "jai siya ram"],
        "extra_hashtags_youtube": ["#vivahpanchami", "#vivahpanchami2027", "#jaishriram"],
        "extra_hashtags_facebook": ["#VivahPanchami", "#VivahPanchami2027", "#JaiSiyaRam"],
        "window_before": 5,
        "window_after": 1,
    },
]


def get_upcoming_festival(
    today: Optional[datetime.date] = None,
) -> Optional[dict]:
    """Return the most relevant festival within its awareness window.

    Checks today's date against each festival's window_before / window_after
    range. If multiple festivals overlap, the one closest to its actual date
    (smallest absolute days_until) is returned.

    Returns None when no festival is active or approaching.
    """
    if today is None:
        today = datetime.date.today()

    candidates = []
    for fest in FESTIVALS:
        fest_date = datetime.date.fromisoformat(fest["date"])
        days_until = (fest_date - today).days
        window_before = fest.get("window_before", WINDOW_DAYS_BEFORE)
        window_after = fest.get("window_after", WINDOW_DAYS_AFTER)

        if -window_after <= days_until <= window_before:
            candidates.append(
                {
                    **fest,
                    "days_until": days_until,
                    "festival_date_str": fest_date.strftime("%B %d, %Y"),
                }
            )

    if not candidates:
        return None

    # Prefer closest to the actual day (on-day > day-before > 2-days-before …)
    candidates.sort(key=lambda f: abs(f["days_until"]))
    return candidates[0]


def build_festival_injection(festival: dict, platform: str = "youtube") -> str:
    """Build the festival awareness block injected into the Gemini user prompt."""
    days = festival["days_until"]
    if days > 0:
        timing = f"in {days} day{'s' if days > 1 else ''}"
    elif days == 0:
        timing = "TODAY"
    else:
        timing = f"{abs(days)} day{'s' if abs(days) > 1 else ''} ago (still relevant)"

    hashtag_key = (
        "extra_hashtags_youtube" if platform == "youtube" else "extra_hashtags_facebook"
    )
    extra_hashtags = " ".join(festival.get(hashtag_key, []))
    search_terms_str = str(festival["search_terms"])

    return (
        f"🎉 FESTIVAL ALERT — MANDATORY:\n"
        f"{'━'*50}\n"
        f"Festival: {festival['name_en']} ({festival['name_hi']}) — {timing} on {festival['festival_date_str']}\n"
        f"MANDATORY deity: {festival['deity_en']} ({festival['deity_hi']})\n"
        f"This video MUST be about {festival['name_hi']}.\n\n"
        f"Theme: {festival['theme']}\n"
        f"Mood: {festival['mood']}\n"
        f"Script guidance: {festival['script_guidance']}\n\n"
        f"SEARCH TERMS — use these instead of generic ones:\n"
        f"  {search_terms_str}\n\n"
        f"TITLE: Must prominently feature the festival name ({festival['name_hi']}).\n"
        f"DESCRIPTION: First line must reference this festival with greetings.\n"
        f"EXTRA HASHTAGS — add to description hashtag block:\n"
        f"  {extra_hashtags}\n"
        f"{'━'*50}\n"
    )
