import React, { useState } from 'react';

const SummaryDisplay = ({ data }) => {
    const [showSources, setShowSources] = useState(false);

    if (!data) return null;

    return (
        <div className="summary-display">
            <header className="summary-header">
                <h2>Market Brief - {data.date}</h2>
                {data.topic && <p className="topic-subtitle">Topic: {data.topic}</p>}
            </header>

            <section className="summary-section">
                <h3>🎙️ Executive Summary</h3>
                <div className="summary-content">
                    {data.podcast_script || data.overview}
                </div>
            </section>

            {data.india_analysis && (
                <section className="summary-section">
                    <h3>🇮🇳 India Market Analysis</h3>
                    <div className="summary-content">
                        {data.india_analysis}
                    </div>
                </section>
            )}

            {data.global_analysis && (
                <section className="summary-section">
                    <h3>🌐 Global Market Analysis</h3>
                    <div className="summary-content">
                        {data.global_analysis}
                    </div>
                </section>
            )}

            <section className="summary-section">
                <h3>💡 Key Insights & Connections</h3>
                <div className="summary-content">
                    {data.insights}
                </div>
            </section>

            <div className="data-meta">
                <span className="quality-tag">Data Quality: {data.data_quality}</span>
            </div>

            <div className="sources-container">
                <button
                    onClick={() => setShowSources(!showSources)}
                    className="sources-toggle"
                >
                    {showSources ? "Hide Sources" : "View Sources Used"}
                </button>
                {showSources && (
                    <ul className="sources-list">
                        {data.sources_used.map((url, i) => (
                            <li key={i}><a href={url} target="_blank" rel="noopener noreferrer">{url}</a></li>
                        ))}
                    </ul>
                )}
            </div>
        </div>
    );
};

export default SummaryDisplay;
