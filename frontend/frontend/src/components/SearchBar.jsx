import React from 'react';

const SearchBar = ({ topic, onTopicChange, onSearch, isLoading }) => {
    const handleSubmit = (e) => {
        e.preventDefault();
        onSearch();
    };

    return (
        <form onSubmit={handleSubmit} className="search-bar-form">
            <input
                type="text"
                placeholder="Search podcast"
                value={topic}
                onChange={(e) => onTopicChange(e.target.value)}
                disabled={isLoading}
                className="search-bar-input"
                aria-label="Search podcast topic"
            />
            <button type="submit" disabled={isLoading} className="search-bar-btn">
                {isLoading ? '…' : 'Search'}
            </button>
        </form>
    );
};

export default SearchBar;
