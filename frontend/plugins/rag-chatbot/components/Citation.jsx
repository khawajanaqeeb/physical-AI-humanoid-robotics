/**
 * Citation Component
 *
 * Displays a clickable citation link that navigates to the exact
 * textbook section referenced in the answer.
 */

import React from 'react';
import './Citation.css';

export default function Citation({ citation }) {
  const { page_title, page_url, chunk_text, relevance_score } = citation;

  const handleClick = () => {
    // Navigate to the citation URL
    window.location.href = page_url;
  };

  // Format relevance score as percentage
  const relevancePercentage = Math.round(relevance_score * 100);

  return (
    <div className="citation-container">
      <button
        className="citation-link"
        onClick={handleClick}
        title={`Jump to: ${page_title}`}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="14"
          height="14"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          className="citation-icon"
        >
          <path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71" />
          <path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71" />
        </svg>
        {page_title}
        <span className="citation-relevance">({relevancePercentage}%)</span>
      </button>
      {chunk_text && (
        <div className="citation-preview">
          <p>{chunk_text}</p>
        </div>
      )}
    </div>
  );
}
