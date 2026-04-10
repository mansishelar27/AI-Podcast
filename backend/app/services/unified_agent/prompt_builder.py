from typing import Optional


def build_podcast_prompt(
    target_date: str = "yesterday",
    current_datetime: str = "",
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
                - Professional Hindi with medium vocabulary level
                - Same word count and structure as English version
                - Use standard financial terminology but explain complex terms
                - Avoid extremely formal words like: परिदृश्य, निहितार्थ, सुव्यवस्थित, अद्यतन, अनिवार्य
                - Use simpler alternatives like: बदलाव, प्रभाव, बेहतर, आवश्यक
                - Mix of simple and complex sentences - average 20-25 words per sentence
                - Assumes audience has basic financial knowledge
                - IMPORTANT FOR TTS: Always expand abbreviations and acronyms completely
                - IMPORTANT FOR TTS: Read abbreviations phonetically or give full expanded form
                - IMPORTANT FOR TTS: Never use standalone abbreviations like (CTC), (HRA), (PAN) - always write full form in Hindi followed by phonetic English in context
                - Natural Hindi speech patterns suitable for podcast listening
                - Clear, organized, engaging tone
                - Maintain professional credibility while remaining accessible
                - NO markdown, asterisks, or special formatting

                OUTPUT FORMAT - CRITICAL: EXACT MARKERS FOR FILE SPLITTING:

                You MUST generate output in EXACTLY this format. These markers are used to automatically split into eng_pod and hin_pod files.

                =====ENGLISH PODCAST SCRIPT=====

                Welcome to the Nippon India Financial Podcast. Today's Edition: {target_date}

                [Auto-Generated Title Based on Content]
                English podcast text here... (flowing narrative, no headers within)

                [Auto-Generated Title Based on Content]
                English podcast text here... (flowing narrative, no headers within)

                [Auto-Generated Title Based on Content]
                English podcast text here... (flowing narrative, no headers within)

                =====HINDI PODCAST SCRIPT=====

                निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: {target_date}

                [Auto-Generated Title Based on Content (or Hindi equivalent)]
                Hindi podcast text here... (flowing narrative, no headers within)

                [Auto-Generated Title Based on Content (or Hindi equivalent)]
                Hindi podcast text here... (flowing narrative, no headers within)

                [Auto-Generated Title Based on Content (or Hindi equivalent)]
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

                [Global Central Bank Actions]
                Central banks across the world have been making significant policy decisions that are reshaping the global financial landscape. Today we break down exactly what these changes mean for your finances and the Indian economy. These monetary policy shifts are not just abstract economic concepts, they directly impact interest rates on your savings accounts, home loans, and investment returns...

                [Impact on Indian Economy]
                The global monetary policy shifts are having direct implications for India's economy. The Indian rupee has been responding to these international movements, and domestic investors need to understand the connection between what's happening globally and what impacts your wallet locally. When major central banks tighten or loosen their policies, capital flows change, affecting how much foreign money comes into Indian markets...

                [What This Means for You]
                For Indian investors and savers, these developments present both challenges and opportunities. The key takeaway from today's financial news is understanding how to position yourself in this changing landscape. Whether you're planning for retirement, investing in mutual funds, or simply keeping money in savings accounts, these global trends matter...

                =====HINDI PODCAST SCRIPT=====

                निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: {target_date}

                [दुनिया के बड़े बैंकों की नई नीतियां]
                दुनिया भर के बड़े बैंक अपनी नई नीतियां बना रहे हैं जिससे पूरी दुनिया के वित्तीय बाजार में बदलाव आ 
                रहा है। आज हम समझाते हैं कि इन बदलावों से आपके पैसे और भारत की अर्थव्यवस्था पर क्या असर पड़ता है। 
                ये सिर्फ किताबी बातें नहीं हैं, इनका सीधा असर आपके बचत खाते पर, होम लोन पर और आपके निवेश के रिटर्न 
                पर पड़ता है।

                [भारतीय अर्थव्यवस्था पर असर]
                दुनिया की इन मौद्रिक नीतियों का सीधा असर भारत पर भी पड़ रहा है। भारतीय रुपये की कीमत इन 
                अंतरराष्ट्रीय बदलावों के प्रति प्रतिक्रिया दिखा रही है। हमारे देश के निवेशकों को समझना जरूरी है कि 
                दुनिया में क्या हो रहा है और इससे हमारे यहां पैसों के प्रवाह पर क्या असर पड़ता है। जब दुनिया के बड़े 
                बैंक अपनी नीतियां कड़ी या नरम करते हैं, तो पूंजी दुनिया भर से इधर-उधर जाता है और भारतीय बाजार में 
                विदेश से आने वाले पैसे की गति बदलती है।

                [आपके लिए यह क्या मायने रखता है]
                भारत में जो लोग पैसे लगाते हैं और बचत करते हैं, उनके लिए यह बदलाव अच्छे और बुरे दोनों अवसर 
                ला सकता है। आज की महत्वपूर्ण बात यह है कि आप समझें कि इस बदलते समय में अपने पैसों को कहां रखें। 
                चाहे आप रिटायरमेंट की योजना बना रहे हों, म्यूचुअल फंड में पैसा लगा रहे हों, या बस बैंक में रुपये जमा 
                कर रहे हों, ये दुनिया की बातें आपके लिए अहम हैं।

                CRITICAL REQUIREMENTS:

                **TWO SEPARATE OUTPUTS WITH EXACT MARKERS (MANDATORY):**
                - Generate FILE 1 (eng_pod): Content between =====ENGLISH PODCAST SCRIPT=====
                - Generate FILE 2 (hin_pod): Content after =====HINDI PODCAST SCRIPT=====
                - Use EXACT markers as shown above (5 equals signs each side)
                - These markers are parsed programmatically - do NOT change them
                - Do NOT add notes, warnings, or extra text between sections

                **CONTENT REQUIREMENTS:**
                - FULL LENGTH REQUIRED: Each script must produce 5–6 minutes of audio (not less).
                - MINIMUM 600 words per script (aim for 800–1000). Do NOT truncate or shorten; generate the complete script.
                - Start with "Welcome to the Nippon India Financial Podcast" in English
                - Start with "निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है" in Hindi
                - Use ONLY proper English and proper Hindi (Devanagari)
                - NO predefined financial sectors or stock-specific data
                - Search results determine content and segment names
                - Include actual numbers and data from search findings
                - ONE continuous narrative per segment (no subsections)
                - Natural speech patterns suitable for TTS systems
                - Both scripts must have IDENTICAL segment structure
                - Major focus on Indian audience perspective and implications
                - Explain why each topic matters for Indian investors/economy
                - Ready to be processed by Sarvam TTS or similar systems
                - Do NOT use markdown, asterisks, or special formatting in either script
                - Write as continuous prose that flows naturally when read aloud in each language

                **CRITICAL TTS OPTIMIZATION FOR HINDI:**
                - Always expand ALL abbreviations and acronyms in full text
                - Never use parenthetical abbreviations like (CTC), (HRA), (PAN), (RBI) 
                - Instead, write the full Hindi name followed by the phonetic English abbreviation in context
                - For numbers and years: Always clarify context to avoid confusion
                  - "नया आयकर अधिनियम, जो 2025 में लागू हुआ"
                  - "2025 का नियम" (if it's a rule)
                  - "आयकर अधिनियम 2025 संस्करण" (if it's a version)
                - Ensure TTS will read clearly without cutting off at parentheses
                - Test readability: Each sentence should flow naturally when spoken aloud"""