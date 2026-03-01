# Changelog - Finance AI Podcast Generator

## [Build 1.1.0] - 2026-02-24

### Changed
- **LLM Migration**: Switched from Anthropic Claude to **Google Gemini 1.5 Flash**.
- **Output Mode**: Audio generation is now **disabled**.
- **Observability**: Added terminal print statements in `orchestrator_service.py` to display:
    - Identified source URLs and scores.
    - Scraped data snapshots (URL, status, length).
    - Gemini analysis results (JSON format).
    - Final market brief script.

### Removed
- Removed `anthropic` and `elevenlabs` dependencies and integration code.

---

## [Build 1.0.0] - 2026-02-24

### Added
- Initial build with FastAPI backend and React frontend.
- Scraping, Filtering, and Summarization services.
