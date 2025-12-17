/**
 * useSession Hook
 *
 * Manages browser session ID using sessionStorage.
 * Creates a new UUID on first use, persists per browser tab.
 */

import { useState, useEffect } from 'react';

const SESSION_STORAGE_KEY = 'rag_chat_session_id';

export default function useSession() {
  const [sessionId, setSessionId] = useState(null);

  useEffect(() => {
    // Get or create session ID
    let id = sessionStorage.getItem(SESSION_STORAGE_KEY);

    if (!id) {
      // Generate new UUID
      id = crypto.randomUUID();
      sessionStorage.setItem(SESSION_STORAGE_KEY, id);
    }

    setSessionId(id);
  }, []);

  return sessionId;
}
