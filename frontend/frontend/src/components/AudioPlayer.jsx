import React from 'react';

const AudioPlayer = ({ data }) => {
    // If generation is successful but audio is missing (e.g. 402 error)
    const audioUrl = data?.audio_bytes || data?.audio_url;

    // Construct full URL if it's a relative path
    const baseUrl = process.env.REACT_APP_API_URL
        ? process.env.REACT_APP_API_URL.replace('/api/v1', '')
        : 'http://localhost:8000';

    const fullAudioUrl = audioUrl && (audioUrl.startsWith('http')
        ? audioUrl
        : `${baseUrl}${audioUrl}`);

    return (
        <div className="audio-player-container">
            <h3>🎙️ Listen to your podcast</h3>
            {audioUrl ? (
                <>
                    <div className="audio-wrapper">
                        <audio controls src={fullAudioUrl} className="audio-element">
                            Your browser does not support the audio element.
                        </audio>
                    </div>
                    <div className="audio-footer">
                        <a href={fullAudioUrl} download className="download-btn" target="_blank" rel="noopener noreferrer">
                            <span className="icon">⬇️</span> Archive Transcript & Audio
                        </a>
                    </div>
                </>
            ) : (
                <div className="audio-unavailable">
                    <p>⚠️ Audio generation is currently unavailable (subscription limit reached).</p>
                    <p className="hint">The full verified script is available below.</p>
                </div>
            )}
        </div>
    );
};

export default AudioPlayer;
