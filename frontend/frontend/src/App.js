import React, { useState, useEffect, useRef } from "react";
import { generatePodcast } from './api/apiClient';

// bulbul:v2 supported speakers only (Sarvam TTS)
const voices = [
  "abhilash (Male/En)",
  "anushka (Female/Hi)",
  "karun (Male/Hi)",
];
const languages = ["Hindi", "English", "Both"];

const style = `
  @import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Sans:wght@300;400;500;600&display=swap');

  *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    background: #0a0f1e;
    color: #e8e4d9;
    font-family: 'DM Sans', sans-serif;
    min-height: 100vh;
  }

  .app {
    min-height: 100vh;
    background: #0a0f1e;
    background-image:
      radial-gradient(ellipse 80% 50% at 50% -20%, rgba(234,179,8,0.12) 0%, transparent 60%),
      radial-gradient(ellipse 60% 40% at 80% 80%, rgba(234,179,8,0.05) 0%, transparent 50%);
    padding: 0 0 60px;
  }

  header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 28px 40px 20px;
    border-bottom: 1px solid rgba(234,179,8,0.12);
  }

  .logo {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .logo-icon {
    width: 36px; height: 36px;
    background: linear-gradient(135deg, #eab308, #f59e0b);
    border-radius: 10px;
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
  }

  .logo-text {
    font-family: 'DM Serif Display', serif;
    font-size: 22px;
    color: #f5f0e8;
    letter-spacing: -0.3px;
  }

  .logo-text span { color: #eab308; }

  .header-tag {
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #eab308;
    background: rgba(234,179,8,0.1);
    border: 1px solid rgba(234,179,8,0.25);
    padding: 5px 12px;
    border-radius: 20px;
  }

  .main { max-width: 760px; margin: 0 auto; padding: 40px 20px 0; }

  /* Tabs */
  .tabs {
    display: flex;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 5px;
    margin-bottom: 36px;
    gap: 4px;
  }

  .tab {
    flex: 1;
    padding: 12px 20px;
    border-radius: 10px;
    border: none;
    background: transparent;
    color: #7c7a72;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex; align-items: center; justify-content: center; gap: 8px;
  }

  .tab.active {
    background: #eab308;
    color: #0a0f1e;
    font-weight: 600;
    box-shadow: 0 4px 16px rgba(234,179,8,0.3);
  }

  .tab:not(.active):hover { color: #e8e4d9; background: rgba(255,255,255,0.06); }

  /* Search bar */
  .search-wrap {
    position: relative;
    margin-bottom: 28px;
  }

  .search-input {
    width: 100%;
    padding: 14px 20px 14px 48px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px;
    color: #e8e4d9;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s;
  }

  .search-input:focus { border-color: rgba(234,179,8,0.5); }
  .search-input::placeholder { color: #4a4840; }

  .search-icon {
    position: absolute; left: 16px; top: 50%; transform: translateY(-50%);
    color: #4a4840; font-size: 16px;
  }

  /* Section label */
  .section-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #5a5850;
    margin-bottom: 16px;
  }

  /* Podcast card */
  .podcast-list { display: flex; flex-direction: column; gap: 12px; }

  .podcast-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 18px 20px;
    display: flex;
    align-items: center;
    gap: 16px;
    transition: all 0.2s ease;
    cursor: auto;
  }

  .podcast-card:hover {
    background: rgba(255,255,255,0.07);
    border-color: rgba(234,179,8,0.2);
    transform: translateY(-1px);
  }

  .play-btn {
    width: 48px; height: 48px; flex-shrink: 0;
    background: linear-gradient(135deg, rgba(234,179,8,0.2), rgba(234,179,8,0.1));
    border: 1.5px solid rgba(234,179,8,0.35);
    border-radius: 12px;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; color: #eab308;
    transition: all 0.2s;
    cursor: pointer;
  }

  .podcast-card:hover .play-btn {
    background: linear-gradient(135deg, rgba(234,179,8,0.35), rgba(234,179,8,0.2));
    box-shadow: 0 0 18px rgba(234,179,8,0.2);
  }

  .podcast-info { flex: 1; min-width: 0; }

  .podcast-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; }

  .podcast-name {
    font-weight: 600;
    font-size: 15px;
    color: #f0ece0;
  }

  .podcast-lang {
    font-size: 10px;
    font-weight: 600;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 8px;
    border-radius: 20px;
    background: rgba(234,179,8,0.12);
    color: #eab308;
    border: 1px solid rgba(234,179,8,0.2);
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
    width: 34px; height: 34px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    color: #6a6860; font-size: 14px;
    cursor: pointer;
    transition: all 0.2s;
    text-decoration: none;
  }

  .download-btn:hover { background: rgba(234,179,8,0.15); color: #eab308; border-color: rgba(234,179,8,0.3); }

  /* Create form */
  .create-form {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 20px;
    padding: 32px;
  }

  .form-title {
    font-family: 'DM Serif Display', serif;
    font-size: 26px;
    color: #f5f0e8;
    margin-bottom: 6px;
  }

  .form-subtitle {
    font-size: 13px;
    color: #5a5850;
    margin-bottom: 32px;
  }

  .form-group { margin-bottom: 20px; }

  .form-label {
    display: block;
    font-size: 12px;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #7a7870;
    margin-bottom: 8px;
  }

  .form-input, .form-select {
    width: 100%;
    padding: 13px 16px;
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
    color: #e8e4d9;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    outline: none;
    transition: border-color 0.2s, box-shadow 0.2s;
    appearance: none;
  }

  .form-input:focus, .form-select:focus {
    border-color: rgba(234,179,8,0.5);
    box-shadow: 0 0 0 3px rgba(234,179,8,0.08);
  }

  .form-input::placeholder { color: #3a3830; }

  .form-select option { background: #131929; }

  .select-wrap { position: relative; }
  .select-arrow {
    position: absolute; right: 14px; top: 50%; transform: translateY(-50%);
    color: #4a4840; pointer-events: none; font-size: 12px;
  }

  .lang-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 10px; }

  .lang-option {
    padding: 12px 16px;
    background: rgba(255,255,255,0.04);
    border: 1.5px solid rgba(255,255,255,0.08);
    border-radius: 10px;
    cursor: pointer;
    text-align: center;
    font-size: 14px;
    font-weight: 500;
    color: #7a7870;
    transition: all 0.2s;
  }

  .lang-option.selected {
    background: rgba(234,179,8,0.12);
    border-color: rgba(234,179,8,0.45);
    color: #eab308;
  }

  .lang-option:hover:not(.selected) { background: rgba(255,255,255,0.07); color: #e8e4d9; }

  .submit-btn {
    width: 100%;
    padding: 15px;
    margin-top: 8px;
    background: linear-gradient(135deg, #eab308, #f59e0b);
    border: none;
    border-radius: 12px;
    color: #0a0f1e;
    font-family: 'DM Sans', sans-serif;
    font-size: 15px;
    font-weight: 700;
    cursor: pointer;
    display: flex; align-items: center; justify-content: center; gap: 8px;
    transition: all 0.2s;
    box-shadow: 0 4px 24px rgba(234,179,8,0.25);
  }

  .submit-btn:hover { box-shadow: 0 8px 32px rgba(234,179,8,0.4); transform: translateY(-1px); }
  .submit-btn:active { transform: translateY(0); }
  .submit-btn:disabled { opacity: 0.5; cursor: not-allowed; }

  /* Script modal */
  .modal-overlay {
    position: fixed; inset: 0;
    background: rgba(5,8,18,0.88);
    backdrop-filter: blur(8px);
    display: flex; align-items: center; justify-content: center;
    z-index: 100;
    padding: 20px;
    animation: fadeIn 0.2s ease;
  }

  @keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }

  .modal {
    background: #0f1628;
    border: 1px solid rgba(234,179,8,0.2);
    border-radius: 24px;
    padding: 36px;
    max-width: 620px;
    width: 100%;
    max-height: 80vh;
    overflow-y: auto;
    box-shadow: 0 32px 80px rgba(0,0,0,0.6), 0 0 0 1px rgba(234,179,8,0.08);
    animation: slideUp 0.25s ease;
  }

  @keyframes slideUp { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

  .modal-tag {
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 2.5px;
    text-transform: uppercase;
    color: #eab308;
    background: rgba(234,179,8,0.1);
    border: 1px solid rgba(234,179,8,0.2);
    border-radius: 20px;
    padding: 4px 12px;
    display: inline-block;
    margin-bottom: 14px;
  }

  .modal-title {
    font-family: 'DM Serif Display', serif;
    font-size: 28px;
    color: #f5f0e8;
    margin-bottom: 20px;
    line-height: 1.2;
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
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 22px;
    font-size: 14px;
    line-height: 1.8;
    color: #c0bab0;
    margin-bottom: 20px;
    min-height: 160px;
    max-height: 260px;
    overflow-y: auto;
    white-space: pre-wrap;
  }

  .script-box::-webkit-scrollbar { width: 4px; }
  .script-box::-webkit-scrollbar-track { background: transparent; }
  .script-box::-webkit-scrollbar-thumb { background: rgba(234,179,8,0.2); border-radius: 4px; }

  /* Audio player */
  .audio-section {
    margin-bottom: 20px;
  }

  .audio-waveform {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 14px;
    padding: 24px 22px 20px;
    margin-bottom: 0;
  }

  .audio-top {
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 18px;
  }

  .audio-play-btn {
    width: 44px; height: 44px; flex-shrink: 0;
    background: linear-gradient(135deg, #eab308, #f59e0b);
    border: none;
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 16px; color: #0a0f1e;
    cursor: pointer;
    transition: all 0.2s;
    box-shadow: 0 4px 16px rgba(234,179,8,0.3);
  }

  .audio-play-btn:hover { transform: scale(1.08); box-shadow: 0 6px 24px rgba(234,179,8,0.4); }

  .audio-info { flex: 1; }
  .audio-title { font-size: 14px; font-weight: 600; color: #f0ece0; margin-bottom: 2px; }
  .audio-meta { font-size: 12px; color: #5a5850; }

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
    margin-bottom: 24px;
  }

  .step {
    display: flex;
    align-items: center;
    gap: 7px;
    font-size: 12px;
    font-weight: 600;
    color: #3a3830;
    transition: color 0.3s;
  }

  .step.active { color: #eab308; }
  .step.done { color: #5a8a5a; }

  .step-dot {
    width: 24px; height: 24px;
    border-radius: 50%;
    border: 2px solid #2a2820;
    display: flex; align-items: center; justify-content: center;
    font-size: 10px; font-weight: 700;
    transition: all 0.3s;
    flex-shrink: 0;
  }

  .step.active .step-dot {
    border-color: #eab308;
    background: rgba(234,179,8,0.15);
    color: #eab308;
    box-shadow: 0 0 10px rgba(234,179,8,0.2);
  }

  .step.done .step-dot {
    border-color: #4a8a4a;
    background: rgba(74,138,74,0.15);
    color: #6aaa6a;
  }

  .step-line {
    flex: 1;
    height: 2px;
    background: #1e1e16;
    margin: 0 10px;
    border-radius: 2px;
    transition: background 0.4s;
  }

  .step-line.done { background: rgba(74,138,74,0.35); }

  /* Approve banner */
  .approve-banner {
    background: rgba(234,179,8,0.06);
    border: 1px solid rgba(234,179,8,0.2);
    border-radius: 12px;
    padding: 14px 18px;
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
  }

  .approve-icon { font-size: 20px; }
  .approve-text { flex: 1; }
  .approve-title { font-size: 13px; font-weight: 600; color: #d4c870; margin-bottom: 2px; }
  .approve-sub { font-size: 12px; color: #5a5840; }

  .modal-actions { display: flex; gap: 12px; }

  .btn-secondary {
    flex: 1;
    padding: 13px;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.1);
    border-radius: 10px;
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
    padding: 13px;
    background: linear-gradient(135deg, #eab308, #f59e0b);
    border: none;
    border-radius: 10px;
    color: #0a0f1e;
    font-family: 'DM Sans', sans-serif;
    font-size: 14px;
    font-weight: 700;
    cursor: pointer;
    transition: all 0.2s;
    display: flex; align-items: center; justify-content: center; gap: 6px;
  }

  .btn-primary:hover { box-shadow: 0 6px 24px rgba(234,179,8,0.35); transform: translateY(-1px); }

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
    text-align: center; padding: 48px 20px;
    color: #4a4840; font-size: 14px;
  }

  .empty-icon { font-size: 36px; margin-bottom: 12px; opacity: 0.4; }
  
  .error-text {
      color: #ef4444;
      font-size: 14px;
      margin-top: 20px;
      text-align: center;
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
  const [name, setName] = useState("");
  const [voice, setVoice] = useState(voices[0]);
  const [language, setLanguage] = useState(languages[0]);
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

  useEffect(() => {
    localStorage.setItem('podcasts', JSON.stringify(podcasts));
  }, [podcasts]);

  const filtered = podcasts.filter(p =>
    p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    (p.description && p.description.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  const handleGenerate = async () => {
    if (!name.trim()) return;
    
    // Map UI language to backend specific format
    let langCode = 'both';
    if (language === 'Hindi') langCode = 'hi';
    if (language === 'English') langCode = 'en';

    let voiceCode = voice.split(' ')[0]; // extracts 'sachit' from 'sachit (Male/En)'

    setShowModal(true);
    setStage("transcript_loading");
    setScript("");
    setErrorMsg("");
    setGeneratedData(null);

    try {
      const data = await generatePodcast(name, voiceCode, langCode);
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

  const handleApproveTranscript = () => {
    setStage("audio_loading");
    // Since backend already generated the audio, we just mock the audio generation time
    // to give user the perception of the 2-step process.
    setTimeout(() => {
      setStage("audio_ready");
    }, 1500);
  };

  const handlePublish = () => {
    // Save to local storage
    if (generatedData) {
      const newPodcast = {
        id: Date.now(),
        name: generatedData.name || name,
        description: script.substring(0, 100) + '...',
        date: new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' }),
        lang: language,
        audioUrl: generatedData.audio?.eng_pod_audio || generatedData.audio?.hin_pod_audio || null
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
          setName(podcast.name);
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
                <label className="form-label">Name</label>
                <input
                  className="form-input"
                  placeholder="Enter your name or entity..."
                  value={name}
                  onChange={e => setName(e.target.value)}
                />
              </div>

              <div className="form-group">
                <label className="form-label">Voice</label>
                <div className="select-wrap">
                  <select className="form-select" value={voice} onChange={e => setVoice(e.target.value)}>
                    {voices.map(v => <option key={v}>{v}</option>)}
                  </select>
                  <span className="select-arrow">▾</span>
                </div>
              </div>

              <div className="form-group">
                <label className="form-label">Language</label>
                <div className="lang-grid">
                  {languages.map(l => (
                    <div
                      key={l}
                      className={`lang-option ${language === l ? "selected" : ""}`}
                      onClick={() => setLanguage(l)}
                    >
                      {l === "Hindi" ? "🇮🇳 Hindi" : (l === "English" ? "🌐 English" : "🔄 Both")}
                    </div>
                  ))}
                </div>
              </div>

              <button className="submit-btn" onClick={handleGenerate} disabled={!name.trim() || stage === "transcript_loading" && showModal}>
                <span>✦</span> Generate Podcast
              </button>
            </div>
          )}
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
