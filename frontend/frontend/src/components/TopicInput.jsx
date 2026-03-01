import React from 'react';
import VoiceSelect from './VoiceSelect';

const TopicInput = ({ topic, onTopicChange, voice, onVoiceChange, onGenerate, isLoading }) => {
    const handleSubmit = (e) => {
        e.preventDefault();
        onGenerate(topic, voice);
    };

    return (
        <div className="topic-input-container">
            <form onSubmit={handleSubmit} className="topic-form">
                <input
                    type="text"
                    placeholder="Search podcast"
                    value={topic}
                    onChange={(e) => onTopicChange(e.target.value)}
                    disabled={isLoading}
                    className="topic-input"
                    aria-label="Search podcast topic"
                />
                <button type="submit" disabled={isLoading} className="generate-button">
                    {isLoading ? 'Generating…' : 'Search'}
                </button>
            </form>
            <VoiceSelect
                value={voice}
                onChange={onVoiceChange}
                disabled={isLoading}
            />
        </div>
    );
};

export default TopicInput;
