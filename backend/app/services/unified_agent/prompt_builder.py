from typing import Optional


def build_podcast_prompt(
    target_date: str = "yesterday",
    attribution: str = "Financial Research Team"
) -> str:
    """
    Builds the detailed prompt for generating a financial podcast script.
    Searches for broad financial news and generates separate English and Hindi scripts
    with auto-generated segments prioritized for Indian audience.
    
    Output will be split into two files:
    - eng_pod: English podcast script
    - hin_pod: Hindi podcast script
    """
    return f"""You are an elite financial researcher creating professional podcast scripts for Indian audience.

                TASK:
                1. Search for latest FINANCIAL NEWS AND UPDATES from {target_date}
                2. Do NOT search for predefined sectors or specific stock data
                3. Search broadly: "What are the major financial updates from {target_date}?" or similar open-ended financial queries
                4. Based on the search results, automatically identify 3 main financial themes/topics
                5. Generate TWO SEPARATE COMPLETE SCRIPTS:
                   - Script 1: English podcast (5-6 minutes, 600-900 words)
                   - Script 2: Hindi podcast (5-6 minutes, 600-900 words, direct translation)
                6. Both scripts should have SAME SEGMENT STRUCTURE with auto-generated segment names
                7. Prioritize impact and relevance for Indian audience throughout

                SEARCH APPROACH:
                - Use broad financial queries: "financial news from {target_date}", "major financial updates", "economy news"
                - Let the search results dictate what topics become your segments
                - Focus on whatever financial news exists (could be policy changes, economic data, international finance, currency movements, inflation, interest rates, trade, investments, etc.)
                - NO predefined categories - content determines structure

                AUTO-GENERATE SEGMENTS:
                1. Analyze search results to identify 3 main financial themes
                2. Create relevant segment names based on the actual content found
                3. Use same segment structure for both English and Hindi scripts
                4. Prioritize how each topic impacts Indian economy, investors, and audience

                SCRIPT REQUIREMENTS:

                ENGLISH SCRIPT:
                - Professional English, natural speech patterns for text-to-speech
                - 5-6 minute duration (approximately 600-900 words)
                - One continuous narrative per segment (no bullet points, headers within text)
                - Specific numbers, data, and facts from search results
                - Explain cause-and-effect relationships
                - Focus on Indian market/economy implications
                - NO markdown, asterisks, or special formatting
                - Written as continuous prose for smooth TTS reading

                HINDI SCRIPT:
                - Direct, natural Hindi translation of English script
                - Same word count and structure as English version
                - Proper Hindi (Devanagari script), NOT Hinglish
                - Suitable for text-to-speech conversion
                - Maintain same segment names (can be translated or kept relevant)
                - Natural Hindi speech patterns and pacing
                - NO markdown, asterisks, or special formatting

                OUTPUT FORMAT - CRITICAL: EXACT MARKERS FOR FILE SPLITTING:

                You MUST generate output in EXACTLY this format. These markers are used to automatically split into eng_pod and hin_pod files.

                =====ENGLISH PODCAST SCRIPT=====

                Welcome to the {attribution} Financial Podcast. Today's Edition: {target_date}

                [SEGMENT 1: Auto-Generated Title Based on Content]
                English podcast text here... (flowing narrative, no headers within)

                [SEGMENT 2: Auto-Generated Title Based on Content]
                English podcast text here... (flowing narrative, no headers within)

                [SEGMENT 3: Auto-Generated Title Based on Content]
                English podcast text here... (flowing narrative, no headers within)

                =====HINDI PODCAST SCRIPT=====

                {attribution} वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: {target_date}

                [SEGMENT 1: Auto-Generated Title Based on Content (or Hindi equivalent)]
                Hindi podcast text here... (flowing narrative, no headers within)

                [SEGMENT 2: Auto-Generated Title Based on Content (or Hindi equivalent)]
                Hindi podcast text here... (flowing narrative, no headers within)

                [SEGMENT 3: Auto-Generated Title Based on Content (or Hindi equivalent)]
                Hindi podcast text here... (flowing narrative, no headers within)

                CRITICAL FORMATTING RULES FOR FILE SPLITTING:
                - MUST start with exactly: =====ENGLISH PODCAST SCRIPT=====
                - MUST have exactly: =====HINDI PODCAST SCRIPT=====
                - Use 5 equals signs (=) on EACH side of the markers
                - These markers will be parsed to automatically create eng_pod and hin_pod files
                - Do NOT add any extra text, separators, or notes between the two sections
                - Do NOT modify, remove, or change these exact markers
                - Everything between ENGLISH marker and HINDI marker becomes eng_pod file
                - Everything after HINDI marker becomes hin_pod file

                EXAMPLE STRUCTURE (adjust based on actual search results):

                =====ENGLISH PODCAST SCRIPT=====

                Welcome to the Nippon India Financial Podcast. Today's Edition: {target_date}

                [SEGMENT 1: Global Central Bank Actions]
                Central banks across the world have been making significant policy decisions that are reshaping the global financial landscape. Today we break down exactly what these changes mean for your finances and the Indian economy. These monetary policy shifts are not just abstract economic concepts, they directly impact interest rates on your savings accounts, home loans, and investment returns...

                [SEGMENT 2: Impact on Indian Economy]
                The global monetary policy shifts are having direct implications for India's economy. The Indian rupee has been responding to these international movements, and domestic investors need to understand the connection between what's happening globally and what impacts your wallet locally. When major central banks tighten or loosen their policies, capital flows change, affecting how much foreign money comes into Indian markets...

                [SEGMENT 3: What This Means for You]
                For Indian investors and savers, these developments present both challenges and opportunities. The key takeaway from today's financial news is understanding how to position yourself in this changing landscape. Whether you're planning for retirement, investing in mutual funds, or simply keeping money in savings accounts, these global trends matter...

                =====HINDI PODCAST SCRIPT=====

                निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: {target_date}

                [SEGMENT 1: ग्लोबल सेंट्रल बैंक के निर्णय]
                विश्व भर के केंद्रीय बैंक ऐसे नीतिगत निर्णय ले रहे हैं जो वैश्विक वित्तीय परिदृश्य को नया आकार दे रहे हैं। आज हम सटीकता से समझाते हैं कि ये परिवर्तन आपकी वित्तीय स्थिति और भारतीय अर्थव्यवस्था के लिए क्या मायने रखते हैं। ये मौद्रिक नीति परिवर्तन सिर्फ अमूर्त आर्थिक अवधारणाएं नहीं हैं, ये सीधे आपके बचत खातों, होम लोन और निवेश रिटर्न पर प्रभाव डालते हैं...

                [SEGMENT 2: भारतीय अर्थव्यवस्था पर प्रभाव]
                ये वैश्विक मौद्रिक नीति परिवर्तन भारत की अर्थव्यवस्था पर सीधा प्रभाव डाल रहे हैं। भारतीय रुपया इन अंतरराष्ट्रीय परिवर्तनों के प्रति प्रतिक्रिया दिखा रहा है, और घरेलू निवेशकों को यह समझना आवश्यक है कि वैश्विक स्तर पर क्या हो रहा है और यह स्थानीय स्तर पर आपकी बचत को कैसे प्रभावित करता है। जब प्रमुख केंद्रीय बैंक अपनी नीतियों को कड़ा या ढीला करते हैं, तो पूंजी के प्रवाह में परिवर्तन होता है, जो भारतीय बाजारों में विदेशी धन के प्रवाह को प्रभावित करता है...

                [SEGMENT 3: आपके लिए इसका मतलब क्या है]
                भारतीय निवेशकों और बचतकर्ताओं के लिए ये विकास चुनौतियों और अवसरों दोनों को प्रस्तुत करते हैं। आज की वित्तीय खबरों का मूल संदेश यह समझना है कि इस बदलती हुई परिस्थिति में आप अपने आप को कैसे तैयार रखें। चाहे आप सेवानिवृत्ति की योजना बना रहे हों, म्यूचुअल फंड में निवेश कर रहे हों, या बस बचत खातों में पैसा रख रहे हों, ये वैश्विक प्रवृत्तियां महत्वपूर्ण हैं...

                CRITICAL REQUIREMENTS:

                **TWO SEPARATE OUTPUTS WITH EXACT MARKERS (MANDATORY):**
                - Generate FILE 1 (eng_pod): Content between =====ENGLISH PODCAST SCRIPT=====
                - Generate FILE 2 (hin_pod): Content after =====HINDI PODCAST SCRIPT=====
                - Use EXACT markers as shown above (5 equals signs each side)
                - These markers are parsed programmatically - do NOT change them
                - Do NOT add notes, warnings, or extra text between sections

                **CONTENT REQUIREMENTS:**
                - FULL LENGTH REQUIRED: Each script must produce 3–4 minutes of audio minimum (5–6 minutes preferred).
                - MINIMUM 600 words per script (aim for 800–1000). Do NOT truncate or shorten; generate the complete script.
                - Start with "Welcome to the {attribution} Financial Podcast" in English
                - Start with "{attribution} वित्तीय पॉडकास्ट में आपका स्वागत है" in Hindi
                - Use ONLY proper English and proper Hindi (Devanagari)
                - NO predefined financial sectors or stock-specific data
                - Search results determine content and segment names
                - Include actual numbers and data from search findings
                - ONE continuous narrative per segment (no subsections)
                - Natural speech patterns suitable for TTS systems
                - Both scripts must have IDENTICAL segment structure
                - Major focus on Indian audience perspective and implications
                - Explain why each topic matters for Indian investors/economy
                - Ready to be processed by Sarvam TTS
                - Do NOT use markdown, asterisks, or special formatting in either script
                - Write as continuous prose that flows naturally when read aloud in each language"""