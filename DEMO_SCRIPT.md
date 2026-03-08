# 🎯 Smart Finance AI Podcast — Demonstration Script

**Purpose:** Guide for presenting the project to your supervisor/sir.  
**Duration:** 8–12 minutes  
**Audience:** Technical evaluator (sir/professor)

---

## 📋 BEFORE THE DEMO (Checklist — 5 minutes before)

- [ ] **Start backend:** `cd AI-Podcast/backend` → `uvicorn app.main:app --reload --port 8000`
- [ ] **Start frontend:** `cd AI-Podcast/frontend/frontend` → `npm start`
- [ ] Open `http://localhost:3000` in browser
- [ ] Ensure internet is working (needed for Google Gemini, Sarvam TTS, Cloudinary)
- [ ] Close unnecessary tabs/apps to avoid lag
- [ ] Optional: Have Cloudinary dashboard open to show uploaded files

---

## 🎤 DEMO FLOW (Step-by-Step)

### **1. INTRODUCTION (1 min)**

**What to say:**
> "This is the Smart Finance AI Podcast — an automated system that generates daily financial briefings as audio podcasts. It uses AI to research latest market news, creates scripts in English and Hindi, converts them to speech, and lets users discover and play podcasts shared by everyone."

**What to show:** Homepage with header "Smart Finance" and "Daily Brief" tag.

---

### **2. SEARCH TAB — Shared Podcast Library (1.5 min)**

**What to say:**
> "The app has two main sections: Search Podcasts and Create Podcast. Let me start with Search."

**Actions:**
1. Click **"🔍 Search Podcasts"** tab
2. Show the list of published podcasts (if any)
3. Use the search bar to filter by name or keyword
4. Click a podcast card to play it

**What to highlight:**
> "All published podcasts are shared. If I publish something, anyone visiting the site can see and play it. The audio is stored on Cloudinary’s CDN, so it’s accessible from anywhere."

**Optional:** Show Cloudinary Media Library — Assets → podcasts folder with MP3 files.

---

### **3. CREATE TAB — Agent Description & Instruction (1 min)**

**What to say:**
> "Now let’s create a new podcast. The system uses a Finance Research Agent powered by Google Gemini."

**Actions:**
1. Click **"✦ Create Podcast"** tab
2. Point out **Agent description**: "Financial market analysis and podcast script generation"
3. Point out **Agent instruction**: Long prompt that defines what the agent researches and how it writes the script

**What to highlight:**
> "The agent uses Google Search to find the latest financial news, then generates separate English and Hindi scripts. We can modify the instruction for custom behavior, or accept the default."

---

### **4. CREATE PODCAST — Full Flow (4–5 min)**

**What to say:**
> "I’ll generate a podcast. We choose the language — English or Hindi — and optionally the voice. Then we click Generate."

**Actions:**
1. Select **Language**: English or Hindi (e.g. Hindi)
2. Select **Voice**: e.g. Anushka (Female/Hi) or Karan (Male/Hi)
3. Click **"✦ Generate Podcast"**
4. Modal opens → **Step 1: Generating Transcript**

**What to say (during loading, ~2–3 min):**
> "The backend is now:
> 1. Calling the Google Gemini agent to search for yesterday’s financial news
> 2. Writing English and Hindi scripts
> 3. Converting scripts to speech via Sarvam AI TTS
> 4. Uploading the MP3 to Cloudinary
> This usually takes 2–3 minutes."

**After Step 1 completes:**
5. Show **Review Transcript** — scroll through the generated script
6. Click **"✓ Continue to Audio"**
7. **Step 2:** Short loading → **Step 3: Your Podcast is Ready**
8. **Play the audio** using the waveform player
9. Click **"🚀 Publish to Search"**

**What to say:**
> "The podcast is now published. It appears in the Search tab and anyone can listen to it. The MP3 is on Cloudinary, so it’s globally accessible."

---

### **5. NEWS SIDEBAR (30 sec)**

**What to say:**
> "On the right, we have live financial news from RSS feeds — Economic Times, MoneyControl, Business Standard — so users stay updated while using the app."

**Action:** Scroll or point to the news column.

---

### **6. TECHNICAL SUMMARY (1–2 min)**

**What to say (if asked about tech):**

| Component | Technology |
|-----------|------------|
| Backend | Python, FastAPI |
| Frontend | React 18 |
| AI / Script Generation | Google Gemini 2.x, Google ADK, google_search tool |
| Text-to-Speech | Sarvam AI (Hindi & English) |
| Audio Storage | Cloudinary (public CDN) |
| Published List | JSON file on backend (shared across users) |

**Architecture:**
> "User request → FastAPI backend → Orchestrator coordinates Agent (Gemini) + Sarvam TTS + Cloudinary upload → Returns scripts + Cloudinary URL → Frontend displays and plays audio."

---

## 🔧 IF SOMETHING GOES WRONG

| Issue | Quick fix |
|-------|-----------|
| "Cannot reach backend" | Start backend: `uvicorn app.main:app --reload --port 8000` |
| "Network/DNS error" | Check internet; try Google DNS (8.8.8.8) |
| "Session already exists" | Refresh page; fixed with unique session IDs |
| Long loading | Normal for first request; Gemini + TTS take 2–3 min |
| No audio | Check Sarvam API key; Cloudinary upload may fall back to local path |

---

## ✅ KEY POINTS TO EMPHASIZE

1. **End-to-end automation:** Topic → Research → Script → Audio → Publish
2. **Bilingual:** English and Hindi scripts and audio
3. **Shared library:** Published podcasts visible to everyone
4. **Cloud storage:** Audio on Cloudinary, not just local
5. **AI-driven:** Gemini for research + scripting, Sarvam for TTS

---

## 📝 CLOSING

> "That’s the Smart Finance AI Podcast. It automates research and podcast creation for daily financial briefs, supports Hindi and English, and shares published episodes via Cloudinary. Happy to take any questions."

---

*Good luck with your demonstration!*
