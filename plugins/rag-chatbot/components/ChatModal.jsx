/**
 * ChatModal Component
 *
 * Modal window containing the chat interface with message list,
 * input field, and citation display.
 */

import React, { useState, useRef, useEffect } from 'react';
import { useUser } from '@site/src/components/auth/UserContext';
import useSession from '../hooks/useSession';
import useChatMessages from '../hooks/useChatMessages';
import { submitQuery } from '../api/client';
import Citation from './Citation';
import './ChatModal.css';

export default function ChatModal({ onClose, initialText = '' }) {
  // Safely access user context, providing fallback values if not available
  let user, token, isAuthenticated;
  try {
    ({ user, token, isAuthenticated } = useUser());
  } catch (error) {
    // Context not available, provide fallback values
    user = null;
    token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;
    isAuthenticated = () => !!(token && localStorage.getItem('user_profile'));
  }

  const sessionId = useSession();
  const { messages, addMessage, updateLastMessage } = useChatMessages();
  const [input, setInput] = useState(initialText);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const messagesEndRef = useRef(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!input.trim() || isLoading) return;

    const userMessage = input.trim();
    setInput('');
    setError(null);

    // Add user message to chat
    addMessage({
      role: 'user',
      content: userMessage,
      timestamp: new Date().toISOString(),
    });

    // Add loading placeholder for assistant
    addMessage({
      role: 'assistant',
      content: '...',
      isLoading: true,
      timestamp: new Date().toISOString(),
    });

    setIsLoading(true);

    try {
      // Submit query to backend with user context
      const response = await submitQuery({
        query: userMessage,
        session_id: sessionId,
        selected_text: initialText || undefined,
        user_profile: isAuthenticated() ? {
          software_experience: user?.software_experience,
          hardware_experience: user?.hardware_experience,
          interests: user?.interests
        } : undefined
      }, token);

      // Update assistant message with actual response
      updateLastMessage({
        role: 'assistant',
        content: response.answer,
        sources: response.sources,  // Our API returns sources as SourceCitation array
        timing: {
          response_time_ms: response.response_time_ms,
        },
        isLoading: false,
        timestamp: new Date().toISOString(),
      });
    } catch (err) {
      console.error('Query failed:', err);

      // Update assistant message with error
      updateLastMessage({
        role: 'assistant',
        content: err.message || 'An error occurred while processing your question. Please try again.',
        isError: true,
        isLoading: false,
        timestamp: new Date().toISOString(),
      });

      setError(err.message || 'An error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chat-modal-overlay" onClick={onClose}>
      <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="chat-modal-header">
          <h3>AI Assistant</h3>
          <button
            className="chat-modal-close"
            onClick={onClose}
            aria-label="Close chat"
          >
            ×
          </button>
        </div>

        {/* Messages */}
        <div className="chat-modal-messages">
          {messages.length === 0 && (
            <div className="chat-welcome-message">
              <p>👋 Hi! I'm your AI assistant for this textbook.</p>
              <p>Ask me anything about the content!</p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`chat-message chat-message-${message.role}`}
            >
              <div className="chat-message-content">
                {message.isLoading ? (
                  <div className="chat-loading">
                    <span className="chat-loading-dot"></span>
                    <span className="chat-loading-dot"></span>
                    <span className="chat-loading-dot"></span>
                  </div>
                ) : (
                  <div className={message.isError ? 'chat-error-text' : ''}>
                    {message.content}
                  </div>
                )}

                {/* Citations */}
                {message.sources && message.sources.length > 0 && (
                  <div className="chat-citations">
                    <p className="chat-citations-label">Sources:</p>
                    {message.sources.map((source, idx) => (
                      <Citation key={idx} citation={source} />
                    ))}
                  </div>
                )}

                {/* Timing info */}
                {message.timing && (
                  <div className="chat-timing">
                    <small>
                      Response time: {message.timing.response_time_ms}ms
                    </small>
                  </div>
                )}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Input Form */}
        <form className="chat-modal-input-form" onSubmit={handleSubmit}>
          {error && (
            <div className="chat-error-banner">
              {error}
            </div>
          )}
          <div className="chat-input-wrapper">
            <input
              type="text"
              className="chat-input"
              placeholder="Ask a question..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              disabled={isLoading}
              autoFocus
            />
            <button
              type="submit"
              className="chat-submit-button"
              disabled={!input.trim() || isLoading}
              aria-label="Send message"
            >
              {isLoading ? (
                '⏳'
              ) : (
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  width="20"
                  height="20"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                >
                  <line x1="22" y1="2" x2="11" y2="13" />
                  <polygon points="22 2 15 22 11 13 2 9 22 2" />
                </svg>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
