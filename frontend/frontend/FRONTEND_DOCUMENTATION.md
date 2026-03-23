## Frontend Documentation — Finance AI Podcast

### Overview

The frontend is a **React 18** single-page application (Create React App) that:

- Provides a modern UI to **generate and review daily finance podcasts**.
- Lets users **review transcripts and audio** in a guided 3-step modal.
- Maintains a **local library of published podcasts** in `localStorage`.
- Shows a **live financial news sidebar** powered by the backend `/financial-news` endpoint.

The frontend talks to the backend via Axios using a configurable `REACT_APP_API_URL`.

---

### Project Layout (frontend)

Root for the React app:

- `frontend/frontend/`

Key files:

- `src/App.js`  
  - Main application component and layout:
    - Header + branding (`Smart Finance` / `Daily Brief`).
    - Two primary tabs:
      - **Search Podcasts** — search and play previously published episodes.
      - **Create Podcast** — generate a new podcast via the backend.
    - Embedded **3-step modal** for transcript → audio → publish workflow.
    - Integrated custom audio player and news sidebar.

- `src/index.js`  
  - CRA root setup mounting `<App />` into `#root`.

- `src/api/apiClient.js`  
  - Axios client configured with:
    - `baseURL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'`.
  - Exported helpers:
    - `generatePodcast(attribution, voice, language, customPrompt)`
    - `getAgentInfo()`
    - `getAgentInstruction(date, attribution)`
    - `getFinancialNews(limit)`

- `src/components/TopicInput.jsx`  
  - Legacy-style topic input + voice selector wrapper (not used by the current `App` layout, but still available).

- `src/components/SummaryDisplay.jsx`  
  - Renders a structured market brief including:
    - `date`, `overview`, `india_analysis`, `global_analysis`, `insights`.
    - `sources_used` as expandable list.
  - Designed around the earlier JSON response shape and still useful as a reusable summary panel.

- `src/components/AudioPlayer.jsx`  
  - Simple `<audio>`-based player that builds a full audio URL by combining `REACT_APP_API_URL` and the `audio_url`/`audio_bytes` from the backend.

- `src/pages/Home.jsx`  
  - Older "page" abstraction that wires together:
    - Podcast naming.
    - Voice selection.
    - View toggling between summary and audio.
  - Superseded by the current `App` layout but kept for potential reuse.

---

### Environment Configuration

The frontend uses a `.env` file (in `frontend/frontend/`) with:

- `REACT_APP_API_URL`  
  - Example: `http://localhost:8000/api/v1`
  - This is the **base URL** for all API calls in `apiClient.js`.

Notes:

- `REACT_APP_` prefix is required for CRA to expose env vars to the browser.
- Do **not** put secrets in frontend `.env` files — they are bundled into shipped JS.

---

### API Integration

`src/api/apiClient.js` centralizes HTTP calls:

- **Base client**

  - `API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api/v1'`
  - `apiClient = axios.create({ baseURL: API_URL, headers: { 'Content-Type': 'application/json' } })`

- **`generatePodcast(attribution, voice, language, customPrompt)`**

  - Sends `POST /generate` with:

    ```json
    {
      "name": "<attribution>",
      "language": "en|hi|both",
      "voice_agent": "<optional>",
      "custom_prompt": "<optional>"
    }
    ```

  - On success:
    - Returns the backend `GenerateResponse` JSON.

  - On error:
    - Throws a **string message** derived from:
      - `error.response.data.detail`,
      - `error.response.data.error`, or
      - `error.message`.

- **`getAgentInfo()` → `GET /agent-info`**

  - Returns `{ description: string }` used in the Create tab.

- **`getAgentInstruction(date, attribution)` → `GET /agent-instruction`**

  - Returns `{ instruction: string }`.
  - Date and attribution are passed as query parameters.

- **`getFinancialNews(limit)` → `GET /financial-news?limit=<limit>`**

  - Returns `{ items: [...], count: N }`.
  - Used by the sidebar to render latest headlines.

---

### App Flow — High Level

`App.js` implements two main experiences: **Search** and **Create**.

#### 1. Search Tab

- **Search bar**
  - Simple text input filtering local podcast library by:
    - `name`
    - short `description` snippet.

- **Podcast list**
  - Drawn from `podcasts` state, persisted in `localStorage`:
    - Each entry: `{ id, name, description, date, lang, audioUrl }`.
  - Clicking an item:
    - Opens the 3-step modal directly in the **audio-ready** state to play that episode.

- **Download button**
  - Uses a helper to build the full backend URL:
    - `getBackendBaseUrl() = REACT_APP_API_URL.replace('/api/v1', '') || 'http://localhost:8000'`.
  - Then appends `podcast.audioUrl` (relative path like `/audio/...mp3`).

#### 2. Create Tab

- **Language selection**
  - Options: `"English"`, `"Hindi"`.
  - Determines:
    - `language` code sent to backend (`en` or `hi`).
    - Voice options dropdown (`ENGLISH_VOICES` vs `HINDI_VOICES`).

- **Agent description**
  - `getAgentInfo()` is called once; the description is shown read-only.

- **Agent instruction**
  - `getAgentInstruction()` is called when the Create tab becomes active.
  - Users can:
    - Accept default.
    - Modify it, then accept changes for a custom session-only prompt.
  - Logic ensures that:
    - When in **read-only** mode, we show a filtered version of the prompt (only English or only Hindi block).
    - When editing, the full prompt is shown.

- **Voice selection**
  - Uses in-component select to choose among preconfigured voices:
    - English: `sachit`.
    - Hindi: `anushka`, `karan`.

- **Generate button**
  - Calls `handleGenerate()`:
    - Opens modal in **Step 1: Transcript loading**.
    - Calls backend `/generate` with the right `language`, `voice_agent`, `name` and (optional) `custom_prompt`.
    - On success:
      - Moves to **Step 1: Transcript ready** state (`stage === "transcript_ready"`).
    - On error:
      - Shows an error message in Step 1 panel.

---

### 3-Step Modal Flow

The modal guides users through **Transcript → Audio → Publish**:

1. **Step 1 — Transcript**
   - `stage === "transcript_loading"`:
     - Shows spinner and message: "Researching & writing your financial brief..."
   - `stage === "transcript_ready"`:
     - Renders the generated script in a scrollable box.
     - Asks user to confirm if they are happy with the transcript.
     - Buttons:
       - **Discard** — closes modal.
       - **Continue to Audio** — moves to Step 2.

2. **Step 2 — Audio**
   - `stage === "audio_loading"`:
     - Shows an interim loading state for audio generation (simulated delay, since actual audio is already prepared by backend).

3. **Step 3 — Publish**
   - `stage === "audio_ready"`:
     - Shows one or two `CustomAudioPlayer` instances based on available `generatedData.audio.eng_pod_audio` / `hin_pod_audio`.
     - Offers a "Publish to Search" button:
       - Saves the podcast metadata (including `audioUrl`) into `podcasts` state and `localStorage`.

---

### Custom Audio Player

`CustomAudioPlayer` is a bespoke UI around the native `Audio` object:

- Builds `fullAudioUrl` from:

  ```js
  const backendBase = process.env.REACT_APP_API_URL
    ? process.env.REACT_APP_API_URL.replace('/api/v1', '')
    : 'http://localhost:8000';
  const fullAudioUrl = audioUrl ? `${backendBase}${audioUrl}` : null;
  ```

- Handles:
  - Play / pause toggle.
  - Progress bar with click-to-seek.
  - Time labels (`currentTime` / `duration`).
  - Animated "bars" to indicate activity.

---

### Styling

`App.js` contains a large **template string** (`const style = \`...\`;`) injected into a `<style>` tag:

- Provides full layout and theme:
  - Dark background, golden accents.
  - Responsive layout for main content and sidebar.
  - Styled tabs, buttons, cards, modal, and audio waveforms.

There is no external CSS file; styles are entirely inlined inside `App.js`.

---

### Extending the Frontend

- Add new endpoints in `apiClient.js` and call them from `App.js` or dedicated components.
- When backend responses change (e.g., new fields in `GenerateResponse`), wire them into:
  - Modal script view,
  - Custom audio player,
  - Any summary components.
- Keep `REACT_APP_API_URL` pointing at the correct backend version (dev/staging/prod) to avoid CORS and path issues.

