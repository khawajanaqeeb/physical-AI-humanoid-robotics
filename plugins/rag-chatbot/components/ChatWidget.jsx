/**
 * ChatWidget Component
 *
 * Floating chat button that opens the chat modal when clicked.
 */

import React, { useState } from 'react';
import ChatModal from './ChatModal';
import './ChatWidget.css';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <>
      {/* Floating Chat Button */}
      <button
        className="chat-widget-button"
        onClick={toggleChat}
        aria-label="Open chat assistant"
        title="Ask a question"
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          width="24"
          height="24"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
        >
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        {!isOpen && <span className="chat-widget-badge">?</span>}
      </button>

      {/* Chat Modal */}
      {isOpen && <ChatModal onClose={() => setIsOpen(false)} />}
    </>
  );
}
