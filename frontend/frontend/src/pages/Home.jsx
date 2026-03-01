import React, { useState } from 'react';
import VoiceSelect from '../components/VoiceSelect';
import SummaryDisplay from '../components/SummaryDisplay';
import AudioPlayer from '../components/AudioPlayer';

const Home = ({
    voice,
    onVoiceChange,
    data,
    isLoading,
    error,
    activeView,
    onSummaryClick,
    onListenClick,
}) => {
    const [podcastName, setPodcastName] = useState('');

    return (
        <div className="home-page">
            <div className="podcast-creation-header">
                <span className="podcast-creation-title">Podcast creation</span>
                <span className="podcast-creation-subtitle">Name your episode and pick a voice.</span>
            </div>

            <div className="voice-section podcast-creation">
                <div className="podcast-creation-body">
                    <div className="podcast-name-field">
                        <label htmlFor="podcast-name">Name</label>
                        <input
                            id="podcast-name"
                            type="text"
                            placeholder="e.g. Morning Market Pulse"
                            value={podcastName}
                            onChange={(e) => setPodcastName(e.target.value)}
                            disabled={isLoading}
                            className="podcast-name-input"
                        />
                    </div>
                    <VoiceSelect
                        value={voice}
                        onChange={onVoiceChange}
                        disabled={isLoading}
                    />
                </div>
            </div>

            <div className="action-buttons">
                <button
                    type="button"
                    className={`action-btn action-btn-summary ${activeView === 'summary' ? 'active' : ''}`}
                    onClick={onSummaryClick}
                    disabled={isLoading}
                >
                    <span className="action-btn-icon">📄</span>
                    Transcription
                </button>
                <button
                    type="button"
                    className={`action-btn action-btn-listen ${activeView === 'audio' ? 'active' : ''}`}
                    onClick={onListenClick}
                    disabled={isLoading}
                >
                    <span className="action-btn-icon">▶</span>
                    Listen podcast
                </button>
            </div>

            {isLoading && (
                <div className="loader">
                    <p>Research agent is preparing your podcast…</p>
                    <p>This may take 20–40 seconds.</p>
                </div>
            )}

            {error && <div className="error-message">⚠️ {error}</div>}

            {data && activeView === 'audio' && (
                <AudioPlayer data={data} />
            )}

            {data && activeView === 'summary' && (
                <SummaryDisplay data={data} />
            )}
        </div>
    );
};

export default Home;
