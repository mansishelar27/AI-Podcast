from typing import Optional


def build_podcast_prompt(
    target_date: str = "yesterday",
    current_datetime: str = "",
    attribution: str = "Financial Research Team"
) -> str:
    """
    Builds the detailed prompt for generating financial podcast scripts.
    Searches for financial news from both time windows and generates separate 
    English and Hindi scripts with auto-generated segments for Indian audience.
    
    Output will be split into two files:
    - eng_pod: English podcast script
    - hin_pod: Hindi podcast script
    """
    return f"""You are an elite financial researcher creating professional podcast scripts for Indian audience.

INPUTS (use as provided):
- target_date: {target_date}
- current_datetime: {current_datetime}

TASK:
1. Search for financial news from BOTH time windows: {target_date} AND {current_datetime}
2. Do NOT search for predefined sectors or specific stock data
3. Search broadly: "financial news {target_date}", "latest financial developments {current_datetime}"
4. Internally organize into Dataset A ({target_date}) and Dataset B ({current_datetime})
5. Identify 3 main financial themes showing progression from {target_date} to {current_datetime}
6. Generate TWO SEPARATE COMPLETE SCRIPTS:
   - Script 1: English podcast (5-6 minutes, 600-900 words)
   - Script 2: Hindi podcast (5-6 minutes, 600-900 words, direct translation)
7. Both scripts must have SAME SEGMENT STRUCTURE with auto-generated segment names
8. Prioritize impact and relevance for Indian audience throughout

SEARCH APPROACH:
- Use broad financial queries for both dates
- Focus areas: policy, interest rates, inflation, currency, trade, investments, macroeconomic data
- Let search results dictate segment topics
- NO predefined categories - content determines structure

AUTO-GENERATE SEGMENTS:
1. Analyze search results to identify 3 main financial themes
2. Create relevant segment names based on actual content found
3. Each segment shows timeline: what happened on {target_date} → how it evolved by {current_datetime}
4. Prioritize how each topic impacts Indian economy, investors, and audience

SCRIPT STRUCTURE - Each segment must include:
1. Introduce the topic
2. Explain initial development from {target_date}
3. Describe latest updates from {current_datetime}
4. Explain cause-and-effect and why situation changed
5. Clarify Indian market implications

ENGLISH SCRIPT:
- Professional English, natural speech patterns for text-to-speech
- 5-6 minute duration (600-900 words minimum)
- One continuous narrative per segment (no bullet points, headers within text)
- Timeline storytelling: "Yesterday... and today...", "On {target_date}... by {current_datetime}..."
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
- Timeline language: "कल... और आज...", "{target_date} को... {current_datetime} तक..."
- CRITICAL FOR TTS: Always expand abbreviations completely
  - Never use (RBI), (CTC), (PAN), (HRA) etc.
  - Write full form: "भारतीय रिज़र्व बैंक जिसे आरबीआई कहते हैं"
  - For numbers/years: "नया आयकर अधिनियम, जो 2025 में लागू हुआ"
- Natural Hindi speech patterns suitable for podcast listening
- Clear, organized, engaging tone
- NO markdown, asterisks, or special formatting

OUTPUT FORMAT - CRITICAL: EXACT MARKERS FOR FILE SPLITTING:

=====ENGLISH PODCAST SCRIPT=====

Welcome to the Nippon India Financial Podcast. Today's Edition: {current_datetime}

[Auto-Generated Title Based on Content]
English podcast text here... (flowing narrative showing progression from {target_date} to {current_datetime})

[Auto-Generated Title Based on Content]
English podcast text here... (flowing narrative showing progression from {target_date} to {current_datetime})

[Auto-Generated Title Based on Content]
English podcast text here... (flowing narrative showing progression from {target_date} to {current_datetime})

=====HINDI PODCAST SCRIPT=====

निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: {current_datetime}

[Auto-Generated Title Based on Content - Hindi equivalent]
Hindi podcast text here... (flowing narrative showing same timeline progression)

[Auto-Generated Title Based on Content - Hindi equivalent]
Hindi podcast text here... (flowing narrative showing same timeline progression)

[Auto-Generated Title Based on Content - Hindi equivalent]
Hindi podcast text here... (flowing narrative showing same timeline progression)

CRITICAL FORMATTING RULES FOR FILE SPLITTING:
- MUST start with exactly: =====ENGLISH PODCAST SCRIPT=====
- MUST have exactly: =====HINDI PODCAST SCRIPT=====
- Use 5 equals signs (=) on EACH side of the markers
- These markers will be parsed to automatically create eng_pod and hin_pod files
- Do NOT add any extra text, separators, or notes between the two sections
- Everything between ENGLISH marker and HINDI marker becomes eng_pod file
- Everything after HINDI marker becomes hin_pod file

EXAMPLE STRUCTURE (adjust based on actual search results):

=====ENGLISH PODCAST SCRIPT=====

Welcome to the Nippon India Financial Podcast. Today's Edition: {current_datetime}

[Global Central Bank Actions]
Yesterday, on {target_date}, central banks across the world made significant policy decisions that began reshaping the global financial landscape. The Federal Reserve held rates steady while signaling potential cuts ahead, and the European Central Bank maintained its cautious stance on inflation. Fast forward to today, {current_datetime}, and we're seeing the ripple effects of these decisions. Markets have responded with increased volatility, and currency movements are reflecting the changing expectations. For Indian investors, this matters because when major central banks shift their policies, it directly impacts interest rates on your savings accounts, home loans, and investment returns. The Indian rupee has already shown movement in response to these global policy shifts...

[Impact on Indian Economy]
The global monetary policy shifts that started materializing on {target_date} are now having direct implications for India's economy as of {current_datetime}. Initially, we saw cautious optimism in Indian markets, but today's data shows a more complex picture. The Indian rupee, which was trading at certain levels yesterday, has adjusted as foreign institutional investors reassess their positions. Domestic investors need to understand this connection between what's happening globally and what impacts your wallet locally. When major central banks tighten or loosen their policies, capital flows change direction, affecting how much foreign money comes into Indian markets and influencing everything from stock prices to bond yields...

[What This Means for You]
For Indian investors and savers, the developments from {target_date} through {current_datetime} present both challenges and opportunities that are evolving in real-time. Yesterday's policy announcements set the stage, and today we're seeing how markets are actually responding. The key takeaway is understanding how to position yourself in this changing landscape. Whether you're planning for retirement, investing in mutual funds, or simply keeping money in savings accounts, these global trends have tangible local effects. The interest rate environment is shifting, and being aware of this timeline helps you make better financial decisions...

=====HINDI PODCAST SCRIPT=====

निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: {current_datetime}

[दुनिया के बड़े बैंकों की नई नीतियां]
कल, {target_date} को, दुनिया भर के बड़े बैंकों ने अपनी नई नीतियां बनाई जिससे पूरी दुनिया के वित्तीय बाजार में बदलाव शुरू हुआ। फ़ेडरल रिज़र्व ने अपनी ब्याज दरें स्थिर रखीं और आगे कटौती के संकेत दिए, जबकि यूरोपीय सेंट्रल बैंक ने महंगाई को लेकर अपना सतर्क रुख बनाए रखा। आज, {current_datetime} तक, हम इन फैसलों के प्रभाव देख रहे हैं। बाजारों में उतार-चढ़ाव बढ़ गया है और मुद्राओं की गति बदलती उम्मीदों को दर्शा रही है। भारतीय निवेशकों के लिए यह इसलिए अहम है क्योंकि जब दुनिया के बड़े बैंक अपनी नीतियां बदलते हैं, तो इसका सीधा असर आपके बचत खाते पर, होम लोन पर और आपके निवेश के रिटर्न पर पड़ता है। भारतीय रुपया पहले ही इन वैश्विक नीतिगत बदलावों के जवाब में हरकत दिखा चुका है...

[भारतीय अर्थव्यवस्था पर असर]
जो वैश्विक मौद्रिक नीति में बदलाव {target_date} को शुरू हुए, वे अब {current_datetime} तक भारत की अर्थव्यवस्था पर सीधा असर डाल रहे हैं। शुरुआत में, भारतीय बाजारों में सतर्क आशावाद दिखा, लेकिन आज के आंकड़े एक और जटिल तस्वीर दिखाते हैं। भारतीय रुपया, जो कल कुछ स्तरों पर था, आज समायोजित हो गया है क्योंकि विदेशी संस्थागत निवेशक अपनी स्थिति का पुनर्मूल्यांकन कर रहे हैं। हमारे देश के निवेशकों को यह समझना जरूरी है कि दुनिया में क्या हो रहा है और इससे आपकी जेब पर क्या असर पड़ता है। जब दुनिया के बड़े बैंक अपनी नीतियां कड़ी या नरम करते हैं, तो पूंजी की दिशा बदलती है, जिससे भारतीय बाजार में विदेश से आने वाले पैसे की मात्रा प्रभावित होती है और शेयर की कीमतों से लेकर बॉन्ड यील्ड तक सब कुछ बदलता है...

[आपके लिए यह क्या मायने रखता है]
भारत में निवेश करने वाले और बचत करने वाले लोगों के लिए, {target_date} से {current_datetime} तक के बदलाव ऐसे अवसर और चुनौतियां लेकर आए हैं जो वास्तविक समय में विकसित हो रही हैं। कल की नीतिगत घोषणाओं ने मंच तैयार किया, और आज हम देख रहे हैं कि बाजार वास्तव में कैसे प्रतिक्रिया दे रहे हैं। मुख्य बात यह समझना है कि इस बदलते परिवेश में आप अपने आप को कैसे स्थापित करें। चाहे आप रिटायरमेंट की योजना बना रहे हों, म्यूचुअल फंड में पैसा लगा रहे हों, या बस बैंक में रुपये जमा कर रहे हों, इन वैश्विक रुझानों का स्थानीय प्रभाव ठोस है। ब्याज दर का माहौल बदल रहा है, और इस समयरेखा के बारे में जागरूक होने से आप बेहतर वित्तीय निर्णय ले सकते हैं...

MANDATORY REQUIREMENTS:
✓ FULL LENGTH: Each script 600-900 words minimum (5-6 minutes audio)
✓ Start English with "Welcome to the Nippon India Financial Podcast. Today's Edition: {current_datetime}"
✓ Start Hindi with "निप्पॉन इंडिया वित्तीय पॉडकास्ट में आपका स्वागत है। आज का संस्करण: {current_datetime}"
✓ Use ONLY proper English and Hindi (Devanagari)
✓ Timeline narrative: show progression from {target_date} to {current_datetime}
✓ Three auto-generated themes based on search results
✓ ONE continuous narrative per segment (no subsections)
✓ Natural speech patterns suitable for TTS systems (Sarvam TTS ready)
✓ Both scripts must have IDENTICAL segment structure
✓ Major focus on Indian audience perspective and implications
✓ Include actual numbers and data from search findings
✓ Expand all abbreviations in Hindi (never use parenthetical abbreviations)
✓ No markdown, asterisks, or special formatting in either script
✓ Use exact marker format for file splitting

The podcast should feel like a cohesive financial story unfolding over time from {target_date} to {current_datetime}, not disconnected news items."""