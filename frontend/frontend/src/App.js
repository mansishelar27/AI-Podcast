import React, { useState, useEffect, useRef } from "react";
import { generatePodcast, getAgentInfo, getAgentInstruction, getFinancialNews, getPodcasts, publishPodcast } from './api/apiClient';

// Language options: only English and Hindi
const LANGUAGE_OPTIONS = ["English", "Hindi"];

// English voices — Deepgram Aura TTS (free tier)
const ENGLISH_VOICES = [
  { id: "aura-arcas-en",   label: "Arcas (Male · American)" },
  { id: "aura-asteria-en", label: "Asteria (Female · American)" },
  { id: "aura-zeus-en",    label: "Zeus (Male · American · Deep)" },
  { id: "aura-luna-en",    label: "Luna (Female · American · Warm)" },
  { id: "aura-helios-en",  label: "Helios (Male · British)" },
];
// Hindi voices — Sarvam bulbul:v2 TTS
const HINDI_VOICES = [
  { id: "anushka", label: "Anushka (Female · Hindi)" },
  { id: "karan",   label: "Karan (Male · Hindi)" },
];

function getVoicesForLanguage(lang) {
  return lang === "English" ? ENGLISH_VOICES : lang === "Hindi" ? HINDI_VOICES : [];
}

const style = `
  /* ── Base ── */
  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
  html { scroll-behavior: smooth; }

  body {
    background: #F5F5F5;
    color: #1A1A1A;
    font-family: 'Segoe UI', 'Inter', system-ui, -apple-system, sans-serif;
    min-height: 100vh;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }

  .app {
    min-height: 100vh;
    background: #F5F5F5;
    padding-bottom: 48px;
  }

  /* ── Header ── */
  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1280px;
    margin: 0 auto;
    padding: 0 24px;
    height: 64px;
    background: #FFFFFF;
    border-bottom: 1px solid #E0E0E0;
    position: sticky;
    top: 0;
    z-index: 50;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
  }

  .logo { display: flex; align-items: center; gap: 10px; }

  .logo-icon {
    width: 36px; height: 36px;
    background: #0F6CBD;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 17px;
  }

  .logo-text {
    font-size: 17px;
    font-weight: 700;
    color: #1A1A1A;
    letter-spacing: -0.3px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
  }

  .logo-text span { color: #0F6CBD; }

  .header-tag {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    color: #0F6CBD;
    background: #EFF6FC;
    border: 1px solid #B4D6F0;
    padding: 5px 12px;
    border-radius: 9999px;
  }

  /* ── Layout ── */
  .main-wrapper {
    display: flex;
    gap: 24px;
    max-width: 1280px;
    margin: 0 auto;
    padding: 28px 24px 0;
    align-items: flex-start;
  }

  .main { flex: 1; min-width: 0; }

  /* ── News Sidebar ── */
  .news-column {
    width: 280px;
    flex-shrink: 0;
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 18px 16px;
    position: sticky;
    top: 80px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
    overflow: hidden;
  }

  .news-list {
    display: flex;
    flex-direction: column;
    max-height: 74vh;
    overflow-y: auto;
    padding-right: 2px;
  }

  .news-list::-webkit-scrollbar { width: 3px; }
  .news-list::-webkit-scrollbar-track { background: transparent; }
  .news-list::-webkit-scrollbar-thumb { background: #E0E0E0; border-radius: 3px; }

  .news-item {
    padding: 10px 0;
    border-bottom: 1px solid #F0F0F0;
    transition: background 200ms ease-in-out;
  }

  .news-item:last-child { border-bottom: none; }

  .news-item a {
    color: #1A1A1A;
    text-decoration: none;
    font-size: 12px;
    font-weight: 500;
    line-height: 1.45;
    display: block;
    transition: color 200ms ease-in-out;
  }

  .news-item a:hover { color: #0F6CBD; }

  .news-item-source {
    font-size: 10px;
    color: #707070;
    margin-top: 4px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    font-weight: 600;
  }

  .news-loading, .news-error {
    font-size: 12px;
    color: #707070;
    padding: 16px 0;
    text-align: center;
  }

  .news-error { color: #C50F1F; }

  @media (max-width: 900px) {
    .main-wrapper { flex-direction: column; gap: 20px; padding: 20px 16px 0; }
    .news-column { width: 100%; position: static; }
    .news-list { max-height: 280px; }
    header { padding: 0 16px; }
  }

  /* ── Tabs ── */
  .tabs {
    display: flex;
    border-bottom: 2px solid #E0E0E0;
    margin-bottom: 24px;
    background: transparent;
  }

  .tab {
    padding: 11px 20px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -2px;
    background: transparent;
    color: #707070;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 400;
    cursor: pointer;
    transition: all 200ms ease-in-out;
    display: flex; align-items: center; gap: 7px;
  }

  .tab.active {
    color: #0F6CBD;
    font-weight: 600;
    border-bottom-color: #0F6CBD;
    background: transparent;
  }

  .tab:not(.active):hover { color: #1A1A1A; background: rgba(0,0,0,0.03); }

  /* ── Search bar ── */
  .search-wrap { position: relative; margin-bottom: 18px; }

  .search-input {
    width: 100%;
    padding: 8px 14px 8px 38px;
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    color: #1A1A1A;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    outline: none;
    height: 36px;
    transition: border-color 200ms ease-in-out, box-shadow 200ms ease-in-out;
  }

  .search-input:focus {
    border-color: #0F6CBD;
    box-shadow: 0 0 0 2px rgba(15,108,189,0.15);
  }

  .search-input::placeholder { color: #ABABAB; }

  .search-icon {
    position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
    color: #ABABAB; font-size: 14px;
  }

  /* ── Section label ── */
  .section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #707070;
    margin-bottom: 12px;
  }

  /* ── Podcast list ── */
  .podcast-list { display: flex; flex-direction: column; gap: 8px; }

  .podcast-card {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 14px 16px;
    display: flex;
    align-items: center;
    gap: 14px;
    cursor: pointer;
    transition: box-shadow 200ms ease-in-out, transform 200ms ease-in-out, border-color 200ms ease-in-out;
  }

  .podcast-card:hover {
    border-color: #B4D6F0;
    transform: translateY(-1px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.08), 0 2px 6px rgba(0,0,0,0.05);
  }

  .play-btn {
    width: 50px; height: 50px; flex-shrink: 0;
    background: linear-gradient(145deg, #0F6CBD, #0E4F86);
    border: none;
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; color: #FFFFFF;
    transition: all 200ms ease-in-out;
    cursor: pointer;
    box-shadow: 0 3px 10px rgba(15,108,189,0.32);
    position: relative;
    overflow: hidden;
  }

  .play-btn::after {
    content: '';
    position: absolute;
    inset: 0;
    background: linear-gradient(145deg, rgba(255,255,255,0.15) 0%, transparent 60%);
    pointer-events: none;
  }

  .podcast-card:hover .play-btn {
    background: linear-gradient(145deg, #115EA3, #0D4070);
    box-shadow: 0 5px 16px rgba(15,108,189,0.44);
    transform: scale(1.06);
  }

  .podcast-info { flex: 1; min-width: 0; }

  .podcast-header { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; flex-wrap: wrap; }

  .podcast-name { font-weight: 600; font-size: 14px; color: #1A1A1A; }

  .podcast-lang {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 9999px;
    background: #EFF6FC;
    color: #0F6CBD;
    border: 1px solid #B4D6F0;
  }

  .podcast-desc {
    font-size: 12px;
    color: #707070;
    line-height: 1.4;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .podcast-meta { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

  .duration { font-size: 12px; color: #707070; font-weight: 500; }

  .download-btn {
    width: 30px; height: 30px;
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    color: #707070; font-size: 12px;
    cursor: pointer;
    transition: all 200ms ease-in-out;
    text-decoration: none;
  }

  .download-btn:hover { background: #EFF6FC; color: #0F6CBD; border-color: #B4D6F0; }

  /* ── Create Form ── */
  .create-form {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 28px 24px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.06), 0 1px 3px rgba(0,0,0,0.04);
    overflow: hidden;
  }

  .form-group {
    margin-bottom: 14px;
    background: #FFFFFF;
    border: 1.5px solid #E8E8E8;
    border-radius: 8px;
    padding: 14px 16px;
    transition: border-color 200ms ease-in-out, box-shadow 200ms ease-in-out;
  }

  .form-group:focus-within {
    border-color: #B4D6F0;
    box-shadow: 0 0 0 3px rgba(15,108,189,0.06);
  }

  .form-label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    color: #424242;
    margin-bottom: 7px;
  }

  .form-input, .form-select {
    width: 100%;
    padding: 7px 11px;
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    color: #1A1A1A;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    outline: none;
    height: 32px;
    transition: border-color 200ms ease-in-out, box-shadow 200ms ease-in-out;
    appearance: none;
  }

  .form-input:focus, .form-select:focus {
    border-color: #0F6CBD;
    box-shadow: 0 0 0 2px rgba(15,108,189,0.15);
  }

  .form-input::placeholder { color: #ABABAB; }
  .form-select option { background: #FFFFFF; color: #1A1A1A; }

  .agent-description-box {
    width: 100%;
    padding: 10px 12px;
    background: #FAFAFA;
    border: 1px dashed #E0E0E0;
    border-radius: 4px;
    color: #707070;
    font-size: 13px;
    line-height: 1.6;
  }

  .agent-instruction-box {
    width: 100%;
    min-height: 130px;
    padding: 10px 12px;
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 4px;
    color: #424242;
    font-size: 12px;
    line-height: 1.65;
    resize: vertical;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    outline: none;
    transition: border-color 200ms ease-in-out, box-shadow 200ms ease-in-out;
  }

  .agent-instruction-box:read-only { background: #FAFAFA; border-style: dashed; cursor: default; }

  .agent-instruction-box:focus {
    border-color: #0F6CBD;
    box-shadow: 0 0 0 2px rgba(15,108,189,0.15);
  }

  .instruction-actions { display: flex; gap: 8px; margin-top: 8px; flex-wrap: wrap; }

  .instruction-btn {
    padding: 6px 14px;
    border-radius: 4px;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    border: 1px solid transparent;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    transition: all 200ms ease-in-out;
  }

  .instruction-btn-accept { background: #F1FAF1; color: #107C10; border-color: #9DC89D; }
  .instruction-btn-accept:hover { background: #E0F2E0; }
  .instruction-btn-modify { background: #EFF6FC; color: #0F6CBD; border-color: #B4D6F0; }
  .instruction-btn-modify:hover { background: #DCEEF8; }
  .instruction-btn-reset { background: #FFFFFF; color: #424242; border-color: #E0E0E0; }
  .instruction-btn-reset:hover { background: #F5F5F5; }

  .instruction-custom-badge { font-size: 11px; color: #107C10; margin-top: 7px; font-weight: 600; }

  .select-wrap { position: relative; }

  .select-arrow {
    position: absolute; right: 11px; top: 50%; transform: translateY(-50%);
    color: #707070; pointer-events: none; font-size: 11px;
  }

  .lang-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }
  .lang-grid-two { grid-template-columns: 1fr 1fr; }

  .lang-option {
    padding: 11px 14px;
    background: #FFFFFF;
    border: 1.5px solid #E0E0E0;
    border-radius: 6px;
    cursor: pointer;
    text-align: center;
    font-size: 14px;
    font-weight: 500;
    color: #424242;
    transition: all 200ms ease-in-out;
  }

  .lang-option.selected { background: #EFF6FC; border-color: #0F6CBD; color: #0F6CBD; font-weight: 600; }
  .lang-option:hover:not(.selected) { background: #F5F5F5; border-color: #ABABAB; }

  .submit-btn {
    width: 100%;
    padding: 10px 20px;
    margin-top: 8px;
    background: #0F6CBD;
    border: none;
    border-radius: 6px;
    color: #FFFFFF;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    height: 40px;
    transition: all 200ms ease-in-out;
  }

  .submit-btn:hover { background: #115EA3; box-shadow: 0 2px 4px rgba(0,0,0,0.12); transform: translateY(-1px); }
  .submit-btn:active { background: #0E4F86; transform: translateY(0); }
  .submit-btn:disabled { background: #ABABAB; cursor: not-allowed; transform: none; box-shadow: none; }

  /* ── Modal ── */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(0,0,0,0.40);
    backdrop-filter: blur(4px);
    display: flex; align-items: center; justify-content: center;
    z-index: 100;
    padding: 24px;
    animation: fadeIn 200ms ease;
  }

  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  .modal {
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 12px;
    padding: 28px;
    max-width: 560px;
    width: 100%;
    max-height: 85vh;
    overflow-y: auto;
    box-shadow: 0 14px 28px rgba(0,0,0,0.14), 0 6px 12px rgba(0,0,0,0.07);
    animation: modalIn 300ms cubic-bezier(0.34, 1.56, 0.64, 1);
  }

  .modal::-webkit-scrollbar { width: 4px; }
  .modal::-webkit-scrollbar-track { background: transparent; }
  .modal::-webkit-scrollbar-thumb { background: #E0E0E0; border-radius: 4px; }

  @keyframes modalIn {
    from { opacity: 0; transform: scale(0.96) translateY(8px); }
    to { opacity: 1; transform: scale(1) translateY(0); }
  }

  .modal-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #0F6CBD;
    background: #EFF6FC;
    border: 1px solid #B4D6F0;
    border-radius: 9999px;
    padding: 4px 12px;
    display: inline-block;
    margin-bottom: 12px;
  }

  .modal-title {
    font-size: 22px;
    font-weight: 700;
    color: #1A1A1A;
    margin-bottom: 20px;
    line-height: 1.25;
    letter-spacing: -0.3px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
  }

  /* Modal inner tabs */
  .modal-tabs {
    display: flex;
    border-bottom: 1px solid #E0E0E0;
    margin-bottom: 14px;
  }

  .modal-tab {
    padding: 8px 14px;
    border: none;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
    background: transparent;
    color: #707070;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 400;
    cursor: pointer;
    display: flex; align-items: center; gap: 6px;
    transition: all 200ms ease-in-out;
    border-radius: 0;
  }

  .modal-tab.active { color: #0F6CBD; font-weight: 600; border-bottom-color: #0F6CBD; }
  .modal-tab:not(.active):hover { color: #1A1A1A; background: #FAFAFA; }

  .script-box {
    background: #FAFAFA;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    padding: 14px;
    font-size: 13px;
    line-height: 1.75;
    color: #424242;
    margin-bottom: 18px;
    min-height: 130px;
    max-height: 240px;
    overflow-y: auto;
    white-space: pre-wrap;
    font-family: 'Segoe UI', 'Inter', sans-serif;
  }

  .script-box::-webkit-scrollbar { width: 3px; }
  .script-box::-webkit-scrollbar-track { background: transparent; }
  .script-box::-webkit-scrollbar-thumb { background: #E0E0E0; border-radius: 3px; }

  .review-tabs { display: flex; gap: 6px; margin-bottom: 12px; }

  .review-tab {
    padding: 6px 13px;
    border-radius: 4px;
    border: 1px solid #E0E0E0;
    background: #FFFFFF;
    color: #424242;
    font-size: 13px;
    cursor: pointer;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-weight: 500;
    transition: all 200ms ease-in-out;
  }

  .review-tab:hover { background: #F5F5F5; }

  .review-tab.active { background: #EFF6FC; border-color: #0F6CBD; color: #0F6CBD; font-weight: 600; }

  .sources-box {
    background: #FAFAFA;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    padding: 14px;
    margin-bottom: 18px;
    max-height: 260px;
    overflow-y: auto;
  }

  .sources-list { list-style: none; margin: 0; padding: 0; }

  .sources-list li {
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid #F0F0F0;
  }

  .sources-list li:last-child { margin-bottom: 0; padding-bottom: 0; border-bottom: none; }

  .source-link { color: #0F6CBD; font-size: 12px; word-break: break-all; text-decoration: none; }
  .source-link:hover { text-decoration: underline; }
  .sources-empty { color: #707070; font-size: 13px; margin: 0; }

  /* ── Audio Player ── */
  .audio-section { margin-bottom: 18px; }

  .audio-waveform {
    background: #FAFAFA;
    border: 1px solid #E0E0E0;
    border-radius: 8px;
    padding: 18px;
    margin-bottom: 0;
  }

  .audio-top { display: flex; align-items: center; gap: 14px; margin-bottom: 14px; }

  .audio-play-btn {
    width: 42px; height: 42px; flex-shrink: 0;
    background: #0F6CBD;
    border: none;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 15px; color: #FFFFFF;
    cursor: pointer;
    box-shadow: 0 2px 4px rgba(15,108,189,0.25);
    transition: all 200ms ease-in-out;
  }

  .audio-play-btn:hover { background: #115EA3; transform: scale(1.05); box-shadow: 0 4px 8px rgba(15,108,189,0.35); }

  .audio-info { flex: 1; min-width: 0; }
  .audio-title { font-size: 14px; font-weight: 600; color: #1A1A1A; margin-bottom: 2px; }
  .audio-meta { font-size: 12px; color: #707070; }

  .audio-duration { font-size: 13px; font-weight: 600; color: #424242; font-variant-numeric: tabular-nums; }

  /* Progress bar */
  .progress-wrap {
    position: relative;
    height: 4px;
    background: #E0E0E0;
    border-radius: 9999px;
    margin-bottom: 7px;
    cursor: pointer;
  }

  .progress-fill {
    height: 100%;
    background: #0F6CBD;
    border-radius: 9999px;
    position: relative;
    transition: width 0.1s;
  }

  .progress-thumb {
    position: absolute;
    right: -5px; top: 50%;
    transform: translateY(-50%);
    width: 11px; height: 11px;
    background: #0F6CBD;
    border-radius: 50%;
    box-shadow: 0 0 0 2px #FFFFFF, 0 0 0 3px #0F6CBD;
  }

  .progress-times {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #ABABAB;
    font-variant-numeric: tabular-nums;
  }

  /* Waveform bars */
  .bars-wrap { display: flex; align-items: flex-end; gap: 2px; height: 26px; margin-top: 11px; }

  .bar { flex: 1; background: #E0E0E0; border-radius: 2px; transition: height 0.1s; }

  .bar.active { background: #0F6CBD; animation: pulse-bar 0.8s ease-in-out infinite alternate; }

  @keyframes pulse-bar { from { opacity: 0.45; } to { opacity: 1; } }

  .audio-generating {
    display: flex; align-items: center; gap: 10px;
    color: #0F6CBD; font-size: 14px;
    padding: 28px 0; justify-content: center;
  }

  /* ── Step Indicator ── */
  .step-indicator { display: flex; align-items: center; margin-bottom: 22px; }

  .step {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 12px;
    font-weight: 600;
    color: #ABABAB;
    transition: color 200ms ease-in-out;
  }

  .step.active { color: #0F6CBD; }
  .step.done { color: #107C10; }

  .step-dot {
    width: 24px; height: 24px;
    border-radius: 50%;
    border: 2px solid #E0E0E0;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700;
    background: #FFFFFF; color: #ABABAB;
    flex-shrink: 0;
    transition: all 200ms ease-in-out;
  }

  .step.active .step-dot { border-color: #0F6CBD; background: #EFF6FC; color: #0F6CBD; }
  .step.done .step-dot { border-color: #107C10; background: #F1FAF1; color: #107C10; }

  .step-line {
    flex: 1;
    height: 1px;
    background: #E0E0E0;
    margin: 0 10px;
    border-radius: 1px;
    transition: background 300ms ease-in-out;
  }

  .step-line.done { background: #107C10; opacity: 0.5; }

  /* ── Approve Banner ── */
  .approve-banner {
    background: #F1FAF1;
    border: 1px solid #9DC89D;
    border-radius: 6px;
    padding: 12px 16px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
  }

  .approve-icon { font-size: 18px; }
  .approve-text { flex: 1; }
  .approve-title { font-size: 13px; font-weight: 600; color: #1A1A1A; margin-bottom: 2px; }
  .approve-sub { font-size: 12px; color: #707070; line-height: 1.4; }

  .modal-actions { display: flex; gap: 10px; }

  .btn-secondary {
    flex: 1;
    padding: 8px 16px;
    background: #FFFFFF;
    border: 1px solid #E0E0E0;
    border-radius: 6px;
    color: #424242;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    height: 36px;
    transition: all 200ms ease-in-out;
  }

  .btn-secondary:hover { background: #F5F5F5; border-color: #ABABAB; }

  .btn-primary {
    flex: 2;
    padding: 8px 16px;
    background: #0F6CBD;
    border: none;
    border-radius: 6px;
    color: #FFFFFF;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 7px;
    height: 36px;
    transition: all 200ms ease-in-out;
  }

  .btn-primary:hover { background: #115EA3; transform: translateY(-1px); box-shadow: 0 2px 4px rgba(0,0,0,0.12); }

  /* ── Spinner & States ── */
  .generating { display: flex; align-items: center; gap: 10px; color: #0F6CBD; font-size: 14px; }

  .spinner {
    width: 16px; height: 16px;
    border: 2px solid #E0E0E0;
    border-top-color: #0F6CBD;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
    flex-shrink: 0;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .empty-state {
    text-align: center;
    padding: 48px 24px;
    color: #707070;
    font-size: 14px;
    line-height: 1.6;
    border-radius: 8px;
    background: #FAFAFA;
    border: 1px dashed #E0E0E0;
  }

  .empty-icon { font-size: 34px; margin-bottom: 12px; opacity: 0.5; }

  .error-text {
    color: #C50F1F;
    font-size: 13px;
    margin-top: 14px;
    text-align: center;
    line-height: 1.5;
    background: #FEF0F1;
    padding: 12px 16px;
    border-radius: 6px;
    border: 1px solid #F4ABAB;
  }

  /* ── Form Hero Banner ── */
  .form-hero-banner {
    background: linear-gradient(135deg, #0F6CBD 0%, #115EA3 55%, #0E4F86 100%);
    border-radius: 6px 6px 0 0;
    margin: -28px -24px 22px;
    padding: 26px 24px 22px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    position: relative;
    overflow: hidden;
    min-height: 110px;
  }

  .form-hero-banner::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 88% 20%, rgba(255,255,255,0.13) 0%, transparent 42%),
      radial-gradient(circle at 10% 85%, rgba(255,255,255,0.07) 0%, transparent 35%);
    pointer-events: none;
  }

  .form-hero-banner::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 1px;
    background: rgba(255,255,255,0.18);
  }

  .form-hero-content { position: relative; z-index: 1; flex: 1; }

  .form-hero-eyebrow {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.72);
    margin-bottom: 6px;
  }

  .form-hero-title {
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    margin-bottom: 6px;
    letter-spacing: -0.3px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
  }

  .form-hero-subtitle {
    font-size: 13px;
    color: rgba(255,255,255,0.76);
    line-height: 1.5;
  }

  .form-hero-art {
    position: relative;
    z-index: 1;
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0.92;
  }

  /* ── News Sidebar Header ── */
  .news-column-header {
    background: linear-gradient(135deg, #0F6CBD 0%, #0E4F86 100%);
    margin: -18px -16px 16px;
    padding: 16px;
    border-radius: 7px 7px 0 0;
    position: relative;
    overflow: hidden;
  }

  .news-column-header::before {
    content: '';
    position: absolute;
    inset: 0;
    background: radial-gradient(circle at 90% 30%, rgba(255,255,255,0.14) 0%, transparent 50%);
    pointer-events: none;
  }

  .news-column-header-row {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    gap: 8px;
    position: relative;
    z-index: 1;
  }

  .news-column-header-title {
    font-size: 14px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.2px;
    margin-bottom: 3px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    line-height: 1.3;
  }

  .news-column-header-sub {
    font-size: 10px;
    color: rgba(255,255,255,0.72);
    text-transform: uppercase;
    letter-spacing: 0.8px;
    font-weight: 600;
  }

  .news-live-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.28);
    border-radius: 9999px;
    padding: 3px 9px;
    font-size: 10px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: 0.6px;
    text-transform: uppercase;
    white-space: nowrap;
    flex-shrink: 0;
  }

  .news-live-dot {
    width: 6px; height: 6px;
    background: #4ADE80;
    border-radius: 50%;
    box-shadow: 0 0 6px rgba(74,222,128,0.7);
    animation: pulseDot 1.6s ease-in-out infinite;
  }

  @keyframes pulseDot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.55; transform: scale(0.75); }
  }

  /* ── Search Tab Hero ── */
  .search-hero {
    background: linear-gradient(135deg, #0F6CBD 0%, #0E4F86 100%);
    border-radius: 8px;
    padding: 20px 22px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 16px;
    position: relative;
    overflow: hidden;
  }

  .search-hero::before {
    content: '';
    position: absolute;
    inset: 0;
    background:
      radial-gradient(circle at 82% 40%, rgba(255,255,255,0.11) 0%, transparent 46%),
      radial-gradient(circle at 12% 80%, rgba(255,255,255,0.06) 0%, transparent 35%);
    pointer-events: none;
  }

  .search-hero-content { position: relative; z-index: 1; }

  .search-hero-eyebrow {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: rgba(255,255,255,0.72);
    margin-bottom: 4px;
  }

  .search-hero-title {
    font-size: 18px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.2px;
    font-family: 'Segoe UI', 'Inter', sans-serif;
    margin-bottom: 4px;
  }

  .search-hero-sub {
    font-size: 12px;
    color: rgba(255,255,255,0.72);
  }

  .search-hero-art {
    position: relative;
    z-index: 1;
    opacity: 0.88;
    flex-shrink: 0;
  }

  /* ── Podcast card left accent ── */
  .podcast-card {
    border-left: 3px solid #0F6CBD !important;
  }

  /* ── Footer / submit area ── */
  .form-footer {
    border-top: 1px solid #F0F0F0;
    margin: 6px -24px -28px;
    padding: 18px 24px;
    background: #FAFAFA;
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .form-footer .submit-btn {
    flex: 1;
    margin-top: 0;
  }

  .form-footer-hint {
    font-size: 11px;
    color: #ABABAB;
    text-align: center;
    margin-top: 10px;
    line-height: 1.4;
  }

  /* ── Focus accessibility ── */
  :focus-visible {
    outline: 2px solid #0F6CBD;
    outline-offset: 2px;
  }
`;

const BAR_HEIGHTS = [30, 55, 40, 70, 50, 85, 45, 60, 35, 75, 55, 40, 65, 80, 45, 55, 70, 35, 60, 50, 75, 40, 65, 30, 80, 55, 45, 70, 50, 60];

function CustomAudioPlayer({ voice, name, audioUrl }) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const audioRef = useRef(null);

    const fullAudioUrl = resolveAudioUrl(audioUrl);

  useEffect(() => {
    if (fullAudioUrl) {
      audioRef.current = new Audio(fullAudioUrl);
      
      const setAudioData = () => {
        setDuration(audioRef.current.duration);
      };
      
      const setAudioTime = () => {
        setCurrentTime(audioRef.current.currentTime);
        setProgress((audioRef.current.currentTime / audioRef.current.duration) * 100);
      };
      
      audioRef.current.addEventListener('loadedmetadata', setAudioData);
      audioRef.current.addEventListener('timeupdate', setAudioTime);
      audioRef.current.addEventListener('ended', () => setIsPlaying(false));
      
      return () => {
        if (audioRef.current) {
          audioRef.current.pause();
          audioRef.current.removeEventListener('loadedmetadata', setAudioData);
          audioRef.current.removeEventListener('timeupdate', setAudioTime);
          audioRef.current.removeAttribute('src');
          audioRef.current.load();
        }
      };
    }
  }, [fullAudioUrl]);

  const togglePlay = () => {
    if (!audioRef.current) return;
    if (isPlaying) {
      audioRef.current.pause();
    } else {
      audioRef.current.play();
    }
    setIsPlaying(!isPlaying);
  };

  const handleSeek = (e) => {
    if (!audioRef.current) return;
    const rect = e.currentTarget.getBoundingClientRect();
    const pos = (e.clientX - rect.left) / rect.width;
    audioRef.current.currentTime = pos * audioRef.current.duration;
    setProgress(pos * 100);
  };

  const fmt = s => {
    if (isNaN(s)) return "0:00";
    return `${Math.floor(s/60)}:${String(Math.floor(s%60)).padStart(2,'0')}`;
  };

  return (
    <div className="audio-waveform">
      <div className="audio-top">
        <button className="audio-play-btn" onClick={togglePlay}>
          {isPlaying ? "⏸" : "▶"}
        </button>
        <div className="audio-info">
          <div className="audio-title">{name}'s Daily Brief</div>
          <div className="audio-meta">{voice} · Podcast</div>
        </div>
        <div className="audio-duration">{fmt(currentTime)} / {fmt(duration)}</div>
      </div>

      <div className="progress-wrap" onClick={handleSeek}>
        <div className="progress-fill" style={{ width: `${progress}%` }}>
          <div className="progress-thumb"></div>
        </div>
      </div>
      <div className="progress-times"><span>{fmt(currentTime)}</span><span>{fmt(duration)}</span></div>

      <div className="bars-wrap">
        {BAR_HEIGHTS.map((h, i) => (
          <div key={i} className={`bar ${isPlaying && i <= (progress / 100 * BAR_HEIGHTS.length) ? 'active' : ''}`}
            style={{ height: `${(progress / 100) * BAR_HEIGHTS.length > i ? h : h * 0.3}%`, animationDelay: `${i * 0.05}s` }} />
        ))}
      </div>
    </div>
  );
}

// Global Audio URL configuration helper
const getBackendBaseUrl = () => {
    return process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL.replace('/api/v1', '') : 'http://localhost:8000';
};

// Resolve audio URL: Cloudinary (full https) use as-is; relative path → backend base + path
const resolveAudioUrl = (audioUrl) => {
    if (!audioUrl) return null;
    if (audioUrl.startsWith('http://') || audioUrl.startsWith('https://')) return audioUrl;
    return getBackendBaseUrl() + (audioUrl.startsWith('/') ? '' : '/') + audioUrl;
};

export default function App() {
  const [activeTab, setActiveTab] = useState("search");
  const [searchQuery, setSearchQuery] = useState("");
  const [name, setName] = useState("Smart Finance Agent");
  const [agentDescription, setAgentDescription] = useState("");
  const [defaultInstruction, setDefaultInstruction] = useState("");
  const [currentInstruction, setCurrentInstruction] = useState("");
  const [acceptedInstruction, setAcceptedInstruction] = useState(null);
  const [instructionModified, setInstructionModified] = useState(false);
  const [instructionEditMode, setInstructionEditMode] = useState(false);
  const instructionModifiedRef = useRef(false);
  const instructionEditModeRef = useRef(false);
  const acceptedInstructionRef = useRef(null);
  instructionModifiedRef.current = instructionModified;
  instructionEditModeRef.current = instructionEditMode;
  acceptedInstructionRef.current = acceptedInstruction;
  const [language, setLanguage] = useState("English");
  const [voice, setVoice] = useState("aura-arcas-en");
  const currentVoices = getVoicesForLanguage(language);
  // When language changes, reset voice to first option for that language
  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    const voices = getVoicesForLanguage(newLang);
    setVoice(voices[0]?.id ?? "aura-arcas-en");
  };
  const [showModal, setShowModal] = useState(false);
  const [stage, setStage] = useState("transcript_loading");
  
  // State for fetched generated podcast
  const [generatedData, setGeneratedData] = useState(null);
  const [script, setScript] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  // Published podcasts (shared list from backend; all users see the same)
  const [podcasts, setPodcasts] = useState([]);
  const [podcastsLoading, setPodcastsLoading] = useState(false);
  const [podcastsError, setPodcastsError] = useState(null);

  const [financialNews, setFinancialNews] = useState([]);
  const [newsLoading, setNewsLoading] = useState(true);
  const [newsError, setNewsError] = useState(null);

  const fetchPodcasts = async () => {
    setPodcastsLoading(true);
    setPodcastsError(null);
    try {
      const data = await getPodcasts();
      setPodcasts(data?.items || []);
    } catch (e) {
      console.error("Failed to load podcasts", e);
      setPodcastsError("Could not load podcasts.");
      setPodcasts([]);
    } finally {
      setPodcastsLoading(false);
    }
  };

  useEffect(() => {
    fetchPodcasts();
  }, []);

  useEffect(() => {
    const fetchNews = async () => {
      setNewsLoading(true);
      setNewsError(null);
      try {
        const data = await getFinancialNews(25);
        setFinancialNews(data?.items || []);
      } catch (e) {
        console.error("Failed to load financial news", e);
        setNewsError("Could not load news.");
        setFinancialNews([]);
      } finally {
        setNewsLoading(false);
      }
    };

    fetchNews();
    const interval = setInterval(fetchNews, 5 * 60 * 1000); // refresh every 5 minutes
    return () => clearInterval(interval);
  }, []);

  // Fetch agent description once so we can show it in the Create tab
  useEffect(() => {
    (async () => {
      try {
        const info = await getAgentInfo();
        if (info?.description) setAgentDescription(info.description);
      } catch (e) {
        console.error("Failed to load agent info", e);
      }
    })();
  }, []);

  // Fetch default agent instruction when Create tab is shown (from prompt_builder)
  useEffect(() => {
    if (activeTab !== "create") return;
    const attribution = name?.trim() || "Smart Finance Agent";
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const dateStr = yesterday.toISOString().slice(0, 10);
    (async () => {
      try {
        const data = await getAgentInstruction(dateStr, attribution);
        if (data?.instruction) {
          setDefaultInstruction(data.instruction);
          if (!instructionModifiedRef.current && !instructionEditModeRef.current && acceptedInstructionRef.current == null)
            setCurrentInstruction(data.instruction);
        }
      } catch (e) {
        console.error("Failed to load agent instruction", e);
      }
    })();
  }, [activeTab, name]);

  const filtered = podcasts.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleGenerate = async () => {
    const langCode = language === "Hindi" ? "hi" : "en";
    const voiceCode = voice; // already stored as id (sachit, anushka, karan)
    const attribution = name && name.trim() ? name.trim() : "Smart Finance Agent";

    setShowModal(true);
    setStage("transcript_loading");
    setScript("");
    setErrorMsg("");
    setGeneratedData(null);

    const customPrompt = instructionEditMode
      ? (currentInstruction.trim() || null)
      : (instructionModified && acceptedInstruction ? acceptedInstruction.trim() : null);

    try {
      const data = await generatePodcast(attribution, voiceCode, langCode, customPrompt);
      if (data?.status === "error") {
        setErrorMsg(data.error || "Generation failed");
        setStage("transcript_loading");
        return;
      }
      setGeneratedData(data);
      
      const displayScript = langCode === 'hi' ? data.scripts?.hin_pod : 
                           (langCode === 'en' ? data.scripts?.eng_pod : 
                           (data.scripts?.eng_pod || "") + "\n\n" + (data.scripts?.hin_pod || ""));
                           
      setScript(displayScript || "Transcript generated successfully.");
      setStage("transcript_ready");
    } catch (err) {
      console.error(err);
      const msg = typeof err === "string" ? err : (err?.message || err?.toString?.() || "Failed to generate podcast");
      setErrorMsg(msg);
      setStage("transcript_loading"); // Keeps it on step 1 with error
    }
  };

  const getInstructionDisplay = () => {
    const base =
      (acceptedInstruction != null && acceptedInstruction !== "" ? acceptedInstruction : currentInstruction) || "";
    if (instructionEditMode) {
      // When editing, always show full prompt so advanced users can modify all behavior.
      return base;
    }
    const englishHeader = "ENGLISH SCRIPT:";
    const hindiHeader = "HINDI SCRIPT:";
    const englishIdx = base.indexOf(englishHeader);
    const hindiIdx = base.indexOf(hindiHeader);
    if (englishIdx === -1 || hindiIdx === -1) {
      // If markers aren't found, fall back to full prompt.
      return base;
    }
    const commonPart = base.slice(0, Math.min(englishIdx, hindiIdx));
    if (language === "Hindi") {
      return commonPart + base.slice(hindiIdx);
    }
    // Default: English
    return commonPart + base.slice(englishIdx, hindiIdx);
  };

  const handleApproveTranscript = () => {
    setStage("audio_loading");
    // Since backend already generated the audio, we just mock the audio generation time
    // to give user the perception of the 2-step process.
    setTimeout(() => {
      setStage("audio_ready");
    }, 1500);
  };

  const handlePublish = async () => {
    if (!generatedData) {
      setShowModal(false);
      return;
    }
    const audioUrl =
      generatedData.audio?.eng_pod_audio ||
      generatedData.audio?.hin_pod_audio ||
      null;
    if (!audioUrl) {
      setShowModal(false);
      setActiveTab("search");
      return;
    }
    const now = new Date();
    const hour = now.getHours();
    const minutes = now.getMinutes();
    const sessionLabel = (hour < 15 || (hour === 15 && minutes < 30))
      ? "Opening Bell"
      : "Closing Bell";
    const dateLabel = now.toLocaleDateString("en-IN", {
      year: "numeric",
      month: "short",
      day: "2-digit",
    });
    const displayName = `${sessionLabel} - ${dateLabel}`;
    const payload = {
      name: displayName,
      description: (script || "").substring(0, 200) + (script?.length > 200 ? "..." : ""),
      date: dateLabel,
      lang: language,
      audioUrl,
    };
    try {
      const created = await publishPodcast(payload);
      setPodcasts((prev) => [created, ...prev]);
    } catch (e) {
      console.error("Failed to publish podcast", e);
    }
    setShowModal(false);
    setActiveTab("search");
    setName("");
    setStage("transcript_loading");
  };

  const playSavedPodcast = (podcast) => {
      if (podcast.audioUrl) {
          setName(podcast.name || "Smart Finance Agent");
          setLanguage(podcast.lang);
          setGeneratedData({ audio: { eng_pod_audio: podcast.audioUrl } }); // mock format to play
          setStage("audio_ready");
          setShowModal(true);
      }
  };

  return (
    <>
      <style>{style}</style>
      <div className="app">
        <header>
          <div className="logo">
            <div className="logo-icon">📈</div>
            <div className="logo-text">Smart <span>Finance</span></div>
          </div>
          <div className="header-tag">Daily Brief</div>
        </header>

        <div className="main-wrapper">
          <div className="main">
          {/* Tabs */}
          <div className="tabs">
            <button className={`tab ${activeTab === "search" ? "active" : ""}`} onClick={() => setActiveTab("search")}>
              🔍 Search Podcasts
            </button>
            <button className={`tab ${activeTab === "create" ? "active" : ""}`} onClick={() => setActiveTab("create")}>
              ✦ Create Podcast
            </button>
          </div>

          {/* Search Tab */}
          {activeTab === "search" && (
            <>
              {/* Search Hero */}
              <div className="search-hero">
                <div className="search-hero-content">
                  <div className="search-hero-eyebrow">Finance AI Podcast</div>
                  <div className="search-hero-title">Your Financial Briefs</div>
                  <div className="search-hero-sub">Listen to AI-generated market podcasts</div>
                </div>
                <div className="search-hero-art">
                  <svg width="74" height="54" viewBox="0 0 74 54" fill="none" xmlns="http://www.w3.org/2000/svg">
                    {/* Chart bars */}
                    <rect x="2" y="36" width="10" height="16" rx="2" fill="rgba(255,255,255,0.28)"/>
                    <rect x="16" y="22" width="10" height="30" rx="2" fill="rgba(255,255,255,0.46)"/>
                    <rect x="30" y="30" width="10" height="22" rx="2" fill="rgba(255,255,255,0.34)"/>
                    <rect x="44" y="10" width="10" height="42" rx="2" fill="rgba(255,255,255,0.70)"/>
                    <rect x="58" y="18" width="10" height="34" rx="2" fill="rgba(255,255,255,0.52)"/>
                    {/* Trend line */}
                    <polyline points="7,32 21,18 35,26 49,8 63,16" stroke="rgba(255,255,255,0.95)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" fill="none"/>
                    {/* Trend dots */}
                    <circle cx="7" cy="32" r="3" fill="white" opacity="0.85"/>
                    <circle cx="49" cy="8" r="3.5" fill="white" opacity="0.95"/>
                    <circle cx="63" cy="16" r="3" fill="white" opacity="0.85"/>
                  </svg>
                </div>
              </div>

              <div className="search-wrap">
                <span className="search-icon">🔍</span>
                <input
                  className="search-input"
                  placeholder="Search by name or keyword..."
                  value={searchQuery}
                  onChange={e => setSearchQuery(e.target.value)}
                />
              </div>

              <div className="section-label">
                {searchQuery ? `${filtered.length} result${filtered.length !== 1 ? "s" : ""} found` : "Recent Podcasts"}
              </div>

              {podcastsLoading && <div className="news-loading">Loading podcasts…</div>}
              {podcastsError && <div className="news-error">{podcastsError}</div>}

              <div className="podcast-list">
                {!podcastsLoading && !podcastsError && filtered.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">🎙</div>
                    {searchQuery ? `No podcasts found for "${searchQuery}"` : "No podcasts yet. Create one to see it here."}
                  </div>
                ) : !podcastsLoading && filtered.map(p => (
                  <div className="podcast-card" key={p.id} onClick={() => playSavedPodcast(p)}>
                    <div className="play-btn">
                      <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
                        <path d="M7 5.5L13 9L7 12.5V5.5Z" fill="white"/>
                      </svg>
                    </div>
                    <div className="podcast-info">
                      <div className="podcast-header">
                        <span className="podcast-name">{p.name}</span>
                        <span className="podcast-lang">{p.lang}</span>
                      </div>
                      <div className="podcast-desc">{p.description}</div>
                    </div>
                    <div className="podcast-meta">
                      <span className="duration">Podcast</span>
                      <a 
                        className="download-btn" 
                        title="Download"
                        href={resolveAudioUrl(p.audioUrl) || "#"}
                        download
                        onClick={(e) => e.stopPropagation()}
                      >⬇</a>
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}

          {/* Create Tab */}
          {activeTab === "create" && (
            <div className="create-form">

              {/* ── Hero Banner ── */}
              <div className="form-hero-banner">
                <div className="form-hero-content">
                  <div className="form-hero-eyebrow">AI Podcast Studio</div>
                  <div className="form-hero-title">New Podcast</div>
                  <div className="form-hero-subtitle">Generate your daily financial brief in seconds using AI.</div>
                </div>
                <div className="form-hero-art">
                  <svg width="90" height="90" viewBox="0 0 90 90" fill="none" xmlns="http://www.w3.org/2000/svg">
                    {/* Mic body */}
                    <rect x="32" y="8" width="26" height="38" rx="13" fill="rgba(255,255,255,0.92)"/>
                    {/* Mic grille lines */}
                    <line x1="32" y1="26" x2="58" y2="26" stroke="rgba(15,108,189,0.28)" strokeWidth="1.5"/>
                    <line x1="32" y1="33" x2="58" y2="33" stroke="rgba(15,108,189,0.28)" strokeWidth="1.5"/>
                    <line x1="32" y1="40" x2="58" y2="40" stroke="rgba(15,108,189,0.28)" strokeWidth="1.5"/>
                    {/* Mic stand arc */}
                    <path d="M22 44C22 57.255 32.745 68 46 68C59.255 68 70 57.255 70 44" stroke="rgba(255,255,255,0.88)" strokeWidth="3.5" strokeLinecap="round" fill="none"/>
                    {/* Vertical pole */}
                    <line x1="46" y1="68" x2="46" y2="78" stroke="rgba(255,255,255,0.88)" strokeWidth="3.5" strokeLinecap="round"/>
                    {/* Base */}
                    <line x1="34" y1="78" x2="58" y2="78" stroke="rgba(255,255,255,0.88)" strokeWidth="3.5" strokeLinecap="round"/>
                    {/* Sound wave left */}
                    <path d="M14 36C11.5 40 11.5 50 14 54" stroke="rgba(255,255,255,0.52)" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
                    <path d="M7 30C3 37 3 53 7 60" stroke="rgba(255,255,255,0.26)" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
                    {/* Sound wave right */}
                    <path d="M76 36C78.5 40 78.5 50 76 54" stroke="rgba(255,255,255,0.52)" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
                    <path d="M83 30C87 37 87 53 83 60" stroke="rgba(255,255,255,0.26)" strokeWidth="2.5" strokeLinecap="round" fill="none"/>
                  </svg>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Language</label>
                <div className="lang-grid lang-grid-two">
                  {LANGUAGE_OPTIONS.map(l => (
                    <div
                      key={l}
                      className={`lang-option ${language === l ? "selected" : ""}`}
                      onClick={() => handleLanguageChange(l)}
                    >
                      {l === "Hindi" ? "🇮🇳 Hindi" : "🌐 English"}
                    </div>
                  ))}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Agent description</label>
                <div className="agent-description-box">
                  {agentDescription || "Financial market analysis and podcast script generation"}
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Agent instruction</label>
                <textarea
                  className="agent-instruction-box"
                  value={getInstructionDisplay()}
                  onChange={e => setCurrentInstruction(e.target.value)}
                  readOnly={!instructionEditMode}
                  placeholder="Loading default prompt from server..."
                  spellCheck={false}
                  rows={10}
                />
                {instructionModified && !instructionEditMode && (
                  <div className="instruction-custom-badge">Custom instruction (used when you click Generate Podcast)</div>
                )}
                <div className="instruction-actions">
                  {!instructionEditMode ? (
                    <>
                      <button
                        type="button"
                        className="instruction-btn instruction-btn-accept"
                        onClick={() => {
                          setCurrentInstruction(defaultInstruction);
                          setAcceptedInstruction(null);
                          setInstructionModified(false);
                        }}
                      >
                        Accept default
                      </button>
                      <button
                        type="button"
                        className="instruction-btn instruction-btn-modify"
                        onClick={() => {
                          setCurrentInstruction(acceptedInstruction != null && acceptedInstruction !== "" ? acceptedInstruction : currentInstruction);
                          setInstructionEditMode(true);
                        }}
                      >
                        Modify
                      </button>
                    </>
                  ) : (
                    <>
                      <button
                        type="button"
                        className="instruction-btn instruction-btn-reset"
                        onClick={() => {
                          setCurrentInstruction(defaultInstruction);
                          setAcceptedInstruction(null);
                          setInstructionModified(false);
                          setInstructionEditMode(false);
                        }}
                      >
                        Reset to default
                      </button>
                      <button
                        type="button"
                        className="instruction-btn instruction-btn-accept"
                        onClick={() => {
                          setAcceptedInstruction(currentInstruction);
                          setInstructionModified(true);
                          setInstructionEditMode(false);
                        }}
                      >
                        Accept changes
                      </button>
                    </>
                  )}
                </div>
              </div>

              {currentVoices.length > 0 && (
                <div className="form-group">
                  <label className="form-label">
                    {language === "English" ? "English voice (Deepgram Aura)" : "Hindi voice (Sarvam)"}
                  </label>
                  <div className="select-wrap">
                    <select className="form-select" value={voice} onChange={e => setVoice(e.target.value)}>
                      {currentVoices.map(v => (
                        <option key={v.id} value={v.id}>{v.label}</option>
                      ))}
                    </select>
                    <span className="select-arrow">▾</span>
                  </div>
                </div>
              )}

              <div className="form-footer">
                <button className="submit-btn" onClick={handleGenerate} disabled={stage === "transcript_loading" && showModal}>
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{flexShrink:0}}>
                    <circle cx="8" cy="8" r="7" stroke="rgba(255,255,255,0.6)" strokeWidth="1.5"/>
                    <path d="M6 5.5L11 8L6 10.5V5.5Z" fill="white"/>
                  </svg>
                  Generate Podcast
                </button>
              </div>

            </div>
          )}
          </div>

          <aside className="news-column">
            <div className="news-column-header">
              <div className="news-column-header-row">
                <div>
                  <div className="news-column-header-title">Market &amp; Financial News</div>
                  <div className="news-column-header-sub">Stocks, economy &amp; major updates</div>
                </div>
                <div className="news-live-badge">
                  <div className="news-live-dot"></div>
                  Live
                </div>
              </div>
            </div>
            {newsLoading && <div className="news-loading">Loading…</div>}
            {newsError && <div className="news-error">{newsError}</div>}
            {!newsLoading && !newsError && financialNews.length > 0 && (
              <div className="news-list">
                {financialNews.map((item, i) => (
                  <div key={i} className="news-item">
                    <a href={item.link || '#'} target="_blank" rel="noopener noreferrer" title={item.snippet || item.title}>
                      {item.title}
                    </a>
                    {item.source && <div className="news-item-source">{item.source}</div>}
                  </div>
                ))}
              </div>
            )}
            {!newsLoading && !newsError && financialNews.length === 0 && (
              <div className="news-loading">No headlines right now.</div>
            )}
          </aside>
        </div>

        {/* Modal */}
        {showModal && (
          <div className="modal-overlay" onClick={e => e.target === e.currentTarget && setShowModal(false)}>
            <div className="modal">

              {/* Step indicator */}
              <div className="step-indicator">
                <div className={`step ${stage === "transcript_loading" ? "active" : "done"}`}>
                  <div className="step-dot">{stage === "transcript_loading" ? "1" : "✓"}</div>
                  Transcript
                </div>
                <div className={`step-line ${["audio_loading","audio_ready"].includes(stage) ? "done" : ""}`} />
                <div className={`step ${stage === "audio_loading" ? "active" : stage === "audio_ready" ? "done" : "step"}`}
                  style={ stage === "transcript_loading" || stage === "transcript_ready" ? { color: "#3a3830" } : {} }>
                  <div className="step-dot">{stage === "audio_ready" ? "✓" : "2"}</div>
                  Audio
                </div>
                <div className={`step-line ${stage === "audio_ready" ? "done" : ""}`} />
                <div className={`step ${stage === "audio_ready" ? "active" : ""}`}
                  style={ stage !== "audio_ready" ? { color: "#3a3830" } : {} }>
                  <div className="step-dot">3</div>
                  Publish
                </div>
              </div>

              {/* ── STAGE 1: Transcript loading ── */}
              {stage === "transcript_loading" && (
                <>
                  <div className="modal-tag">Step 1 of 3</div>
                  <div className="modal-title">Generating Transcript</div>
                  {errorMsg ? (
                      <div className="error-text">
                          <p>⚠️ {errorMsg}</p>
                          <div className="modal-actions" style={{ marginTop: 20 }}>
                              <button className="btn-secondary" onClick={() => setShowModal(false)}>Close</button>
                          </div>
                      </div>
                  ) : (
                      <div className="script-box">
                        <div className="generating">
                          <div className="spinner"></div>
                          Researching & writing your financial brief... (This may take 2-3 minutes)
                        </div>
                      </div>
                  )}
                </>
              )}

              {/* ── STAGE 2: Transcript ready — approve or discard ── */}
              {stage === "transcript_ready" && (
                <>
                  <div className="modal-tag">Step 1 of 3 — Review</div>
                  <div className="modal-title">Review Transcript</div>
                  <div className="script-box">{script}</div>
                  <div className="approve-banner">
                    <div className="approve-icon">👀</div>
                    <div className="approve-text">
                      <div className="approve-title">Happy with the transcript?</div>
                      <div className="approve-sub">Approve it to hear the generated audio podcast.</div>
                    </div>
                  </div>
                  <div className="modal-actions">
                    <button className="btn-secondary" onClick={() => setShowModal(false)}>✕ Discard</button>
                    <button className="btn-primary" onClick={handleApproveTranscript}>
                      <span>✓</span> Continue to Audio
                    </button>
                  </div>
                </>
              )}

              {/* ── STAGE 3: Audio loading ── */}
              {stage === "audio_loading" && (
                <>
                  <div className="modal-tag">Step 2 of 3</div>
                  <div className="modal-title">Loading Audio</div>
                  <div className="audio-waveform" style={{ marginBottom: 20 }}>
                    <div className="audio-generating">
                      <div className="spinner"></div>
                      Preparing your podcast audio...
                    </div>
                  </div>
                </>
              )}

              {/* ── STAGE 4: Audio ready — listen & publish ── */}
              {stage === "audio_ready" && (
                <>
                  <div className="modal-tag">Step 3 of 3 — Ready!</div>
                  <div className="modal-title">Your Podcast is Ready 🎉</div>
                  
                  {/* Since generatedData could have multiple audios (eng_pod_audio, hin_pod_audio) we play the chosen language or fallback. */}
                  {generatedData?.audio?.eng_pod_audio && (
                      <CustomAudioPlayer 
                          voice="English" 
                          name={name} 
                          audioUrl={generatedData.audio.eng_pod_audio} 
                      />
                  )}
                  {generatedData?.audio?.hin_pod_audio && (
                      <CustomAudioPlayer 
                          voice="Hindi" 
                          name={name} 
                          audioUrl={generatedData.audio.hin_pod_audio} 
                      />
                  )}
                  
                  <div style={{ marginTop: 16 }}>
                    <div className="approve-banner">
                      <div className="approve-icon">🎙</div>
                      <div className="approve-text">
                        <div className="approve-title">Sounds good?</div>
                        <div className="approve-sub">Publish it so others can find it in Search.</div>
                      </div>
                    </div>
                    <div className="modal-actions">
                      <button className="btn-secondary" onClick={() => setShowModal(false)}>✕ Close</button>
                      <button className="btn-primary" onClick={handlePublish}>
                        <span>🚀</span> Publish to Search
                      </button>
                    </div>
                  </div>
                </>
              )}

            </div>
          </div>
        )}
      </div>
    </>
  );
}
