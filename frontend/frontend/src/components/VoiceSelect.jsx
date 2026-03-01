import React, { useState, useRef } from 'react';

const VOICES = [
  { id: 'shubh', name: 'Shubh', sampleUrl: '/samples/shubh.mp3' },
  { id: 'amit', name: 'Amit', sampleUrl: '/samples/amit.mp3' },
  { id: 'simran', name: 'Simran', sampleUrl: '/samples/simran.mp3' },
  { id: 'sheya', name: 'Sheya', sampleUrl: '/samples/sheya.mp3' },
];

const VoiceSelect = ({ value, onChange, disabled }) => {
  const [playingId, setPlayingId] = useState(null);
  const audioRef = useRef(null);

  const handleSamplePlay = (voice) => {
    if (playingId === voice.id) {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current.currentTime = 0;
      }
      setPlayingId(null);
      return;
    }
    setPlayingId(voice.id);
    if (audioRef.current) {
      audioRef.current.src = voice.sampleUrl;
      audioRef.current.play().catch(() => setPlayingId(null));
    }
  };

  return (
    <div className="voice-select-wrapper">
      <label className="voice-select-label">Choose your voice</label>
      <div className="voice-select-row">
        <select
          className="voice-select"
          value={value || ''}
          onChange={(e) => onChange(e.target.value || null)}
          disabled={disabled}
        >
          <option value="">Select a voice</option>
          {VOICES.map((v) => (
            <option key={v.id} value={v.id}>
              {v.name}
            </option>
          ))}
        </select>
        {value && (
          <button
            type="button"
            className="voice-sample-btn"
            onClick={() => handleSamplePlay(VOICES.find((v) => v.id === value) || VOICES[0])}
            disabled={disabled}
            title="Play sample"
          >
            {playingId === value ? (
              <span className="voice-sample-icon">⏹</span>
            ) : (
              <span className="voice-sample-icon">▶</span>
            )}
            <span>Sample</span>
          </button>
        )}
      </div>
      <audio
        ref={audioRef}
        onEnded={() => setPlayingId(null)}
        onError={() => setPlayingId(null)}
      />
    </div>
  );
};

export default VoiceSelect;
export { VOICES };
