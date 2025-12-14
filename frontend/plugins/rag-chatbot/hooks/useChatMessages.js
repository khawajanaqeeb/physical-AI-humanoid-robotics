/**
 * useChatMessages Hook
 *
 * Manages chat message state with add and update operations.
 * Messages are stored in memory only (not persisted).
 */

import { useState } from 'react';

export default function useChatMessages() {
  const [messages, setMessages] = useState([]);

  const addMessage = (message) => {
    setMessages((prev) => [...prev, message]);
  };

  const updateLastMessage = (updates) => {
    setMessages((prev) => {
      if (prev.length === 0) return prev;

      const newMessages = [...prev];
      const lastIndex = newMessages.length - 1;
      newMessages[lastIndex] = { ...newMessages[lastIndex], ...updates };

      return newMessages;
    });
  };

  const clearMessages = () => {
    setMessages([]);
  };

  return {
    messages,
    addMessage,
    updateLastMessage,
    clearMessages,
  };
}
