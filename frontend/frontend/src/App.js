import React, { useState, useEffect, useRef } from "react";
import { generatePodcast, getAgentInfo, getAgentInstruction, getFinancialNews } from './api/apiClient';

// Language options: only English and Hindi
const LANGUAGE_OPTIONS = ["English", "Hindi"];

// Voices by language (Sarvam TTS)
const ENGLISH_VOICES = [
  { id: "sachit", label: "sachit (Male/En)" },
];
const HINDI_VOICES = [
  { id: "anushka", label: "Anushka (Female/Hi)" },
  { id: "karan", label: "Karan (Male/Hi)" },
];

function getVoicesForLanguage(lang) {
  return lang === "English" ? ENGLISH_VOICES : lang === "Hindi" ? HINDI_VOICES : [];
}

const style = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600;700&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  html { scroll-behavior: smooth; }

  body {
    background: #070b14;
    color: #e8e4d9;
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
    line-height: 1.5;
  }

  .app {
    min-height: 100vh;
    background: #070b14;
    background-image:
      radial-gradient(ellipse 100% 60% at 50% -15%, rgba(234,179,8,0.08) 0%, transparent 55%),
      radial-gradient(ellipse 70% 50% at 100% 50%, rgba(234,179,8,0.04) 0%, transparent 50%),
      radial-gradient(ellipse 60% 40% at 0% 80%, rgba(234,179,8,0.03) 0%, transparent 45%);
    padding-bottom: 48px;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    max-width: 1280px;
    margin: 0 auto;
    padding: 24px 24px 20px;
    border-bottom: 1px solid rgba(234,179,8,0.1);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 12px;
  }

  .logo-icon {
    width: 42px; height: 42px;
    background: linear-gradient(145deg, #eab308, #d4a006);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 20px;
    box-shadow: 0 4px 14px rgba(234,179,8,0.25);
  }

  .logo-text {
    font-family: 'DM Serif Display', serif;
    font-size: 24px;
    color: #f8f6f0;
    letter-spacing: -0.4px;
  }

  .logo-text span { color: #eab308; }

  .header-tag {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #eab308;
    background: rgba(234,179,8,0.12);
    border: 1px solid rgba(234,179,8,0.3);
    padding: 6px 14px;
    border-radius: 20px;
    box-shadow: 0 0 20px rgba(234,179,8,0.08);
  }

  .main-wrapper {
    display: flex;
    gap: 32px;
    max-width: 1280px;
    margin: 0 auto;
    padding: 32px 24px 0;
    align-items: flex-start;
  }
  .main { flex: 1; min-width: 0; max-width: 720px; }

  .news-column {
    width: 340px;
    flex-shrink: 0;
    background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 24px;
    position: sticky;
    top: 24px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.2);
  }
  .news-column-title {
    font-family: 'DM Serif Display', serif;
    font-size: 20px;
    color: #f0ece0;
    margin-bottom: 4px;
    letter-spacing: -0.3px;
  }
  .news-column-sub {
    font-size: 12px;
    color: #6a6860;
    margin-bottom: 20px;
  }
  .news-list { display: flex; flex-direction: column; gap: 12px; max-height: 70vh; overflow-y: auto; padding-right: 4px; }
  .news-list::-webkit-scrollbar { width: 5px; }
  .news-list::-webkit-scrollbar-track { background: transparent; }
  .news-list::-webkit-scrollbar-thumb { background: rgba(234,179,8,0.2); border-radius: 5px; }
  .news-item {
    padding: 14px 16px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    transition: all 0.25s ease;
  }
  .news-item:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(234,179,8,0.25);
    transform: translateX(4px);
  }
  .news-item a {
    color: #e8e4d9;
    text-decoration: none;
    font-size: 13px;
    font-weight: 500;
    line-height: 1.45;
    display: block;
  }
  .news-item a:hover { color: #eab308; }
  .news-item-source {
    font-size: 10px;
    color: #5a5850;
    margin-top: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
  }
  .news-loading, .news-error {
    font-size: 13px;
    color: #5a5850;
    padding: 20px 0;
  }
  .news-error { color: #e07a7a; }

  @media (max-width: 900px) {
    .main-wrapper { flex-direction: column; gap: 24px; padding: 24px 16px 0; }
    .news-column { width: 100%; position: static; max-height: 400px; }
    .news-list { max-height: 320px; }
    header { padding: 20px 16px 16px; }
  }

  /* Tabs */
  .tabs {
    display: flex;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 6px;
    margin-bottom: 32px;
    gap: 6px;
  }

  .tab {
    flex: 1;
    padding: 14px 24px;
    border-radius: 12px;
    border: none;
    background: transparent;
    color: #7c7a72;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.25s ease;
    display: flex; align-items: center; justify-content: center; gap: 8px;
  }

  .tab.active {
    background: linear-gradient(135deg, #eab308, #f59e0b);
    color: #0a0f1e;
    font-weight: 700;
    box-shadow: 0 4px 20px rgba(234,179,8,0.35);
  }

  .tab:not(.active):hover { color: #e8e4d9; background: rgba(255,255,255,0.06); }

  /* Search bar */
  .search-wrap {
    position: relative;
    margin-bottom: 24px;
  }

  .search-input {
    width: 100%;
    padding: 16px 20px 16px 50px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 14px;
    color: #e8e4d9;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
  }

  .search-input:focus {
    border-color: rgba(234,179,8,0.5);
    box-shadow: 0 0 0 3px rgba(234,179,8,0.08);
  }
  .search-input::placeholder { color: #4a4840; }

  .search-icon {
    position: absolute; left: 18px; top: 50%; transform: translateY(-50%);
    color: #5a5850; font-size: 17px;
  }

  /* Section label */
  .section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #5a5850;
    margin-bottom: 14px;
  }

  /* Podcast card */
  .podcast-list { display: flex; flex-direction: column; gap: 14px; }

  .podcast-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 18px;
    padding: 20px 22px;
    display: flex;
    align-items: center;
    gap: 18px;
    transition: all 0.25s ease;
    cursor: pointer;
  }

  .podcast-card:hover {
    background: rgba(255,255,255,0.06);
    border-color: rgba(234,179,8,0.22);
    transform: translateY(-2px);
    box-shadow: 0 12px 28px rgba(0,0,0,0.15);
  }

  .play-btn {
    width: 52px; height: 52px; flex-shrink: 0;
    background: linear-gradient(135deg, rgba(234,179,8,0.25), rgba(234,179,8,0.12));
    border: 1.5px solid rgba(234,179,8,0.4);
    border-radius: 14px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: #eab308;
    transition: all 0.25s;
    cursor: pointer;
  }

  .podcast-card:hover .play-btn {
    background: linear-gradient(135deg, rgba(234,179,8,0.4), rgba(234,179,8,0.25));
    box-shadow: 0 0 24px rgba(234,179,8,0.25);
  }

  .podcast-info { flex: 1; min-width: 0; }

  .podcast-header { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; flex-wrap: wrap; }

  .podcast-name {
    font-weight: 600;
    font-size: 16px;
    color: #f2eee6;
  }

  .podcast-lang {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1.2px;
    text-transform: uppercase;
    padding: 3px 10px;
    border-radius: 20px;
    background: rgba(234,179,8,0.14);
    color: #eab308;
    border: 1px solid rgba(234,179,8,0.25);
  }

  .podcast-desc {
    font-size: 13px;
    color: #6a6860;
    line-height: 1.5;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  .podcast-meta {
    display: flex;
    align-items: center;
    gap: 12px;
    flex-shrink: 0;
  }

  .duration {
    font-family: 'DM Serif Display', serif;
    font-size: 15px;
    color: #eab308;
  }

  .download-btn {
    width: 36px; height: 36px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    color: #6a6860; font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
  }

  .download-btn:hover { background: rgba(234,179,8,0.15); color: #eab308; border-color: rgba(234,179,8,0.35); }

  /* Create form */
  .create-form {
    background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.02) 100%);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 24px;
    padding: 40px 36px;
    box-shadow: 0 8px 40px rgba(0,0,0,0.15);
  }

  .form-title {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: #f8f6f0;
    margin-bottom: 8px;
    letter-spacing: -0.3px;
  }

  .form-subtitle {
    font-size: 14px;
    color: #6a6860;
    margin-bottom: 36px;
    line-height: 1.5;
  }

  .form-group { margin-bottom: 24px; }

  .form-label {
    display: block;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 1.8px;
    text-transform: uppercase;
    color: #7a7870;
    margin-bottom: 10px;
  }

  .form-input, .form-select {
    width: 100%;
    padding: 14px 18px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    color: #e8e4d9;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    appearance: none;
  }

  .form-input:focus, .form-select:focus {
    border-color: rgba(234,179,8,0.5);
    box-shadow: 0 0 0 3px rgba(234,179,8,0.1);
  }

  .form-input::placeholder { color: #4a4840; }

  .form-select option { background: #131929; }

  .agent-description-box {
    width: 100%;
    padding: 14px 18px;
    background: rgba(255,255,255,0.03);
    border: 1px dashed rgba(255,255,255,0.12);
    border-radius: 12px;
    color: #a8a49a;
    font-size: 13px;
    line-height: 1.6;
  }

  .agent-instruction-box {
    width: 100%;
    min-height: 140px;
    padding: 14px 18px;
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    color: #c2beb4;
    font-size: 12px;
    line-height: 1.65;
    resize: vertical;
    font-family: 'DM Sans', sans-serif;
  }
  .agent-instruction-box:read-only { border-style: dashed; cursor: default; }
  .agent-instruction-box:focus { outline: none; border-color: rgba(234,179,8,0.45); box-shadow: 0 0 0 3px rgba(234,179,8,0.08); }

  .instruction-actions { display: flex; gap: 12px; margin-top: 12px; flex-wrap: wrap; }
  .instruction-btn {
    padding: 10px 18px;
    border-radius: 10px;
    font-size: 13px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s;
    border: 1px solid transparent;
  }
  .instruction-btn-accept {
    background: rgba(74,138,74,0.22);
    color: #7acc7a;
    border-color: rgba(74,138,74,0.45);
  }
  .instruction-btn-accept:hover { background: rgba(74,138,74,0.32); }
  .instruction-btn-modify {
    background: rgba(234,179,8,0.14);
    color: #eab308;
    border-color: rgba(234,179,8,0.4);
  }
  .instruction-btn-modify:hover { background: rgba(234,179,8,0.22); }
  .instruction-btn-reset {
    background: rgba(255,255,255,0.06);
    color: #7a7870;
    border-color: rgba(255,255,255,0.12);
  }
  .instruction-btn-reset:hover { background: rgba(255,255,255,0.1); color: #e8e4d9; }

  .instruction-custom-badge {
    font-size: 11px;
    color: #6aaa6a;
    margin-top: 10px;
    font-weight: 600;
  }

  .select-wrap { position: relative; }
  .select-arrow {
    position: absolute; right: 16px; top: 50%; transform: translateY(-50%);
    color: #5a5850; pointer-events: none; font-size: 12px;
  }

  .lang-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; }
  .lang-grid-two { grid-template-columns: 1fr 1fr; }

  .lang-option {
    padding: 14px 18px;
    background: rgba(255,255,255,0.04);
    border: 1.5px solid rgba(255,255,255,0.08);
    border-radius: 12px;
    cursor: pointer;
    text-align: center;
    font-size: 14px;
    font-weight: 500;
    color: #7a7870;
    transition: all 0.25s ease;
  }

  .lang-option.selected {
    background: rgba(234,179,8,0.14);
    border-color: rgba(234,179,8,0.5);
    color: #eab308;
    box-shadow: 0 0 20px rgba(234,179,8,0.08);
  }

  .lang-option:hover:not(.selected) { background: rgba(255,255,255,0.07); color: #e8e4d9; }

  .submit-btn {
    width: 100%;
    padding: 16px 20px;
    margin-top: 12px;
    background: linear-gradient(135deg, #eab308, #e5a807);
    border: none;
    border-radius: 14px;
    color: #0a0f1e;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 10px;
    transition: all 0.25s ease;
    box-shadow: 0 6px 28px rgba(234,179,8,0.3);
  }

  .submit-btn:hover { box-shadow: 0 10px 36px rgba(234,179,8,0.4); transform: translateY(-2px); }
  .submit-btn:active { transform: translateY(0); }
  .submit-btn:disabled { opacity: 0.5; cursor: not-allowed; transform: none; }

  /* Script modal */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(5,8,18,0.9);
    backdrop-filter: blur(12px);
    display: flex; align-items: center; justify-content: center;
    z-index: 100;
    padding: 24px;
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  .modal {
    background: linear-gradient(180deg, #0f1628 0%, #0a0f1e 100%);
    border: 1px solid rgba(234,179,8,0.22);
    border-radius: 28px;
    padding: 40px;
    max-width: 640px;
    width: 100%;
    max-height: 85vh;
    overflow-y: auto;
    box-shadow: 0 40px 96px rgba(0,0,0,0.5), 0 0 0 1px rgba(234,179,8,0.1);
    animation: slideUp 0.3s ease;
  }

  @keyframes slideUp { from { opacity: 0; transform: translateY(24px); } to { opacity: 1; transform: translateY(0); } }

  .modal-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #eab308;
    background: rgba(234,179,8,0.12);
    border: 1px solid rgba(234,179,8,0.25);
    border-radius: 20px;
    padding: 5px 14px;
    display: inline-block;
    margin-bottom: 16px;
  }

  .modal-title {
    font-family: 'DM Serif Display', serif;
    font-size: 30px;
    color: #f8f6f0;
    margin-bottom: 24px;
    line-height: 1.25;
    letter-spacing: -0.3px;
  }

  /* Modal inner tabs */
  .modal-tabs {
    display: flex;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 10px;
    padding: 4px;
    gap: 4px;
    margin-bottom: 20px;
  }

  .modal-tab {
    flex: 1;
    padding: 9px 14px;
    border-radius: 7px;
    border: none;
    background: transparent;
    color: #5a5850;
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
    display: flex; align-items: center; justify-content: center; gap: 6px;
  }

  .modal-tab.active {
    background: rgba(234,179,8,0.15);
    color: #eab308;
    border: 1px solid rgba(234,179,8,0.3);
  }

  .modal-tab:not(.active):hover { color: #e8e4d9; background: rgba(255,255,255,0.06); }

  .script-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    font-size: 14px;
    line-height: 1.75;
    color: #c2beb4;
    margin-bottom: 24px;
    min-height: 160px;
    max-height: 280px;
    overflow-y: auto;
    white-space: pre-wrap;
  }

  .script-box::-webkit-scrollbar { width: 4px; }
  .script-box::-webkit-scrollbar-track { background: transparent; }
  .script-box::-webkit-scrollbar-thumb { background: rgba(234,179,8,0.2); border-radius: 4px; }

  .review-tabs {
    display: flex;
    gap: 8px;
    margin-bottom: 16px;
  }
  .review-tab {
    padding: 10px 18px;
    border-radius: 10px;
    border: 1px solid rgba(255,255,255,0.12);
    background: rgba(255,255,255,0.04);
    color: #c2beb4;
    font-size: 14px;
    cursor: pointer;
    transition: background 0.2s, border-color 0.2s, color 0.2s;
  }
  .review-tab:hover {
    background: rgba(255,255,255,0.08);
    color: #e8e4d9;
  }
  .review-tab.active {
    background: rgba(234,179,8,0.15);
    border-color: rgba(234,179,8,0.4);
    color: #eab308;
  }
  .sources-box {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 24px;
    max-height: 320px;
    overflow-y: auto;
  }
  .sources-list {
    list-style: none;
    margin: 0;
    padding: 0;
  }
  .sources-list li {
    margin-bottom: 12px;
    padding-bottom: 12px;
    border-bottom: 1px solid rgba(255,255,255,0.06);
  }
  .sources-list li:last-child {
    margin-bottom: 0;
    padding-bottom: 0;
    border-bottom: none;
  }
  .source-link {
    color: #eab308;
    font-size: 13px;
    word-break: break-all;
    text-decoration: none;
  }
  .source-link:hover {
    text-decoration: underline;
  }
  .sources-empty {
    color: #8a8578;
    font-size: 14px;
    margin: 0;
  }

  /* Audio player */
  .audio-section {
    margin-bottom: 24px;
  }

  .audio-waveform {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 18px;
    padding: 26px 24px 22px;
    margin-bottom: 0;
  }

  .audio-top {
    display: flex;
    align-items: center;
    gap: 16px;
    margin-bottom: 20px;
  }

  .audio-play-btn {
    width: 48px; height: 48px; flex-shrink: 0;
    background: linear-gradient(135deg, #eab308, #e5a807);
    border: none;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px; color: #0a0f1e;
    cursor: pointer;
    transition: all 0.25s;
    box-shadow: 0 6px 20px rgba(234,179,8,0.35);
  }

  .audio-play-btn:hover { transform: scale(1.06); box-shadow: 0 8px 28px rgba(234,179,8,0.45); }

  .audio-info { flex: 1; min-width: 0; }
  .audio-title { font-size: 15px; font-weight: 600; color: #f2eee6; margin-bottom: 4px; }
  .audio-meta { font-size: 12px; color: #6a6860; }

  .audio-duration {
    font-family: 'DM Serif Display', serif;
    font-size: 16px;
    color: #eab308;
  }

  /* Progress bar */
  .progress-wrap {
    position: relative;
    height: 4px;
    background: rgba(255,255,255,0.08);
    border-radius: 4px;
    margin-bottom: 10px;
    cursor: pointer;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #eab308, #f59e0b);
    border-radius: 4px;
    position: relative;
    transition: width 0.1s;
  }

  .progress-thumb {
    position: absolute;
    right: -5px; top: 50%;
    transform: translateY(-50%);
    width: 12px; height: 12px;
    background: #eab308;
    border-radius: 50%;
    box-shadow: 0 0 8px rgba(234,179,8,0.5);
  }

  .progress-times {
    display: flex;
    justify-content: space-between;
    font-size: 11px;
    color: #4a4840;
  }

  /* Bars animation */
  .bars-wrap {
    display: flex;
    align-items: flex-end;
    gap: 3px;
    height: 32px;
    margin-top: 14px;
  }

  .bar {
    flex: 1;
    background: rgba(234,179,8,0.25);
    border-radius: 2px;
    transition: height 0.1s;
  }

  .bar.active { background: rgba(234,179,8,0.7); animation: pulse-bar 0.8s ease-in-out infinite alternate; }

  @keyframes pulse-bar {
    from { opacity: 0.4; }
    to   { opacity: 1; }
  }

  .audio-generating {
    display: flex; align-items: center; gap: 10px;
    color: #eab308; font-size: 14px;
    padding: 32px 0; justify-content: center;
  }

  /* Step indicator */
  .step-indicator {
    display: flex;
    align-items: center;
    margin-bottom: 28px;
  }

  .step {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13px;
    font-weight: 600;
    color: #3a3830;
    transition: color 0.3s;
  }

  .step.active { color: #eab308; }
  .step.done { color: #5a9a5a; }

  .step-dot {
    width: 28px; height: 28px;
    border-radius: 50%;
    border: 2px solid #2a2820;
    display: flex; align-items: center; justify-content: center;
    font-size: 11px; font-weight: 700;
    transition: all 0.3s;
    flex-shrink: 0;
  }

  .step.active .step-dot {
    border-color: #eab308;
    background: rgba(234,179,8,0.18);
    color: #eab308;
    box-shadow: 0 0 14px rgba(234,179,8,0.25);
  }

  .step.done .step-dot {
    border-color: #4a9a4a;
    background: rgba(74,138,74,0.18);
    color: #6acc6a;
  }

  .step-line {
    flex: 1;
    height: 2px;
    background: #1e1e16;
    margin: 0 12px;
    border-radius: 2px;
    transition: background 0.4s;
  }

  .step-line.done { background: rgba(74,138,74,0.4); }

  /* Approve banner */
  .approve-banner {
    background: rgba(234,179,8,0.08);
    border: 1px solid rgba(234,179,8,0.22);
    border-radius: 14px;
    padding: 16px 20px;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 24px;
  }

  .approve-icon { font-size: 22px; }
  .approve-text { flex: 1; }
  .approve-title { font-size: 14px; font-weight: 600; color: #d8d090; margin-bottom: 4px; }
  .approve-sub { font-size: 12px; color: #6a6840; line-height: 1.4; }

  .modal-actions { display: flex; gap: 14px; }

  .btn-secondary {
    flex: 1;
    padding: 14px 18px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    color: #7a7870;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
  }

  .btn-secondary:hover { background: rgba(255,255,255,0.1); color: #e8e4d9; }

  .btn-primary {
    flex: 2;
    padding: 14px 18px;
    background: linear-gradient(135deg, #eab308, #e5a807);
    border: none;
    border-radius: 12px;
    color: #0a0f1e;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.25s;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    box-shadow: 0 4px 20px rgba(234,179,8,0.25);
  }

  .btn-primary:hover { box-shadow: 0 8px 28px rgba(234,179,8,0.35); transform: translateY(-1px); }

  /* Generating state */
  .generating {
    display: flex; align-items: center; gap: 10px;
    color: #eab308; font-size: 14px;
  }

  .spinner {
    width: 16px; height: 16px;
    border: 2px solid rgba(234,179,8,0.2);
    border-top-color: #eab308;
    border-radius: 50%;
    animation: spin 0.7s linear infinite;
  }

  @keyframes spin { to { transform: rotate(360deg); } }

  .empty-state {
    text-align: center;
    padding: 56px 24px;
    color: #5a5850;
    font-size: 14px;
    line-height: 1.6;
    border-radius: 16px;
    background: rgba(255,255,255,0.02);
    border: 1px dashed rgba(255,255,255,0.06);
  }

  .empty-icon { font-size: 40px; margin-bottom: 14px; opacity: 0.5; }

  .error-text {
    color: #e07a7a;
    font-size: 14px;
    margin-top: 20px;
    text-align: center;
    line-height: 1.5;
  }
`;

const BAR_HEIGHTS = [30, 55, 40, 70, 50, 85, 45, 60, 35, 75, 55, 40, 65, 80, 45, 55, 70, 35, 60, 50, 75, 40, 65, 30, 80, 55, 45, 70, 50, 60];

function CustomAudioPlayer({ voice, name, audioUrl }) {
    const [isPlaying, setIsPlaying] = useState(false);
    const [progress, setProgress] = useState(0);
    const [currentTime, setCurrentTime] = useState(0);
    const [duration, setDuration] = useState(0);
    const audioRef = useRef(null);

    const backendBase = process.env.REACT_APP_API_URL ? process.env.REACT_APP_API_URL.replace('/api/v1', '') : 'http://localhost:8000';
    const fullAudioUrl = audioUrl ?`${backendBase}${audioUrl}` : null;

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
}

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
  const [voice, setVoice] = useState("sachit");
  const currentVoices = getVoicesForLanguage(language);
  // When language changes, reset voice to first option for that language
  const handleLanguageChange = (newLang) => {
    setLanguage(newLang);
    const voices = getVoicesForLanguage(newLang);
    setVoice(voices[0]?.id ?? "sachit");
  };
  const [showModal, setShowModal] = useState(false);
  const [stage, setStage] = useState("transcript_loading");
  
  // State for fetched generated podcast
  const [generatedData, setGeneratedData] = useState(null);
  const [script, setScript] = useState("");
  const [errorMsg, setErrorMsg] = useState("");

  // Storage for previously generated podcasts
  const [podcasts, setPodcasts] = useState(() => {
    try {
      return JSON.parse(localStorage.getItem('podcasts')) || [];
    } catch {
      return [];
    }
  });

  const [financialNews, setFinancialNews] = useState([]);
  const [newsLoading, setNewsLoading] = useState(true);
  const [newsError, setNewsError] = useState(null);

  useEffect(() => {
    localStorage.setItem('podcasts', JSON.stringify(podcasts));
  }, [podcasts]);

  useEffect(() => {
    (async () => {
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
    })();
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

  const handlePublish = () => {
    // Save to local storage with Opening/Closing bell naming
    if (generatedData) {
      const now = new Date();
      // Simple rule: before 2 PM → Opening Bell, after → Closing Bell
      const hour = now.getHours();
      const sessionLabel = hour < 14 ? "Opening Bell" : "Closing Bell";
      const dateLabel = now.toLocaleDateString("en-IN", {
        year: "numeric",
        month: "short",
        day: "2-digit",
      });
      const displayName = `${sessionLabel} - ${dateLabel}`;

      const newPodcast = {
        id: Date.now(),
        name: displayName,
        description: script.substring(0, 100) + "...",
        date: dateLabel,
        lang: language,
        audioUrl:
          generatedData.audio?.eng_pod_audio ||
          generatedData.audio?.hin_pod_audio ||
          null,
      };

      setPodcasts([newPodcast, ...podcasts]);
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

              <div className="podcast-list">
                {filtered.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">🎙</div>
                    No podcasts found for "{searchQuery}"
                  </div>
                ) : filtered.map(p => (
                  <div className="podcast-card" key={p.id} onClick={() => playSavedPodcast(p)}>
                    <div className="play-btn">▶</div>
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
                        href={p.audioUrl ? `${getBackendBaseUrl()}${p.audioUrl}` : "#"}
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
              <div className="form-title">New Podcast</div>
              <div className="form-subtitle">Generate your daily financial brief in seconds.</div>

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
                    {language === "English" ? "English voices" : "Hindi voices"}
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

              <button className="submit-btn" onClick={handleGenerate} disabled={stage === "transcript_loading" && showModal}>
                <span>✦</span> Generate Podcast
              </button>
            </div>
          )}
          </div>

          <aside className="news-column">
            <div className="news-column-title">Market & financial news</div>
            <div className="news-column-sub">Stocks, economy & major updates</div>
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
