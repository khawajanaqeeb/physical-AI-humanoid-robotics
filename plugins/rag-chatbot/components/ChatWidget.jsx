/**
 * ChatWidget Component
 *
 * Floating chat button that opens the chat modal when clicked.
 * Requires authentication - redirects to signin if user is not logged in.
 */

import React, { useState, useEffect } from 'react';
import { useAuth } from '@site/src/components/auth/AuthContext';
import ChatModal from './ChatModal';
import './ChatWidget.css';

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, isLoading } = useAuth();

  // Check for chatbot open query param (from auth redirect)
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('chatbot') === 'open' && isAuthenticated) {
      setIsOpen(true);
      // Clean up URL
      params.delete('chatbot');
      const newUrl = `${window.location.pathname}${params.toString() ? '?' + params.toString() : ''}`;
      window.history.replaceState({}, '', newUrl);
    }
  }, [isAuthenticated]);

  const toggleChat = () => {
    if (!isAuthenticated) {
      // Store current page for redirect after signin
      sessionStorage.setItem('auth_redirect', window.location.pathname);
      window.location.href = '/auth/signin';
      return;
    }

    setIsOpen(!isOpen);
  };

  if (isLoading) {
    return null; // Hide widget while loading auth state
  }

  return (
    <>
      {/* Floating Chat Button */}
      <button
        className="chat-widget-button"
        onClick={toggleChat}
        aria-label="Open chat assistant"
        title={isAuthenticated ? "Ask a question" : "Sign in to use chatbot"}
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
      {isOpen && isAuthenticated && <ChatModal onClose={() => setIsOpen(false)} />}
    </>
  );
}
