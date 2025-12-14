/**
 * Chat Widget Entry Point
 *
 * This module renders the floating chat button and modal
 * on all pages using Docusaurus Client API.
 */

import React from 'react';
import ReactDOM from 'react-dom';
import ChatWidget from './components/ChatWidget';

// Wait for DOM to load
if (typeof window !== 'undefined') {
  window.addEventListener('DOMContentLoaded', () => {
    // Create mount point for chat widget
    const chatContainer = document.createElement('div');
    chatContainer.id = 'rag-chatbot-root';
    document.body.appendChild(chatContainer);

    // Render chat widget
    ReactDOM.render(<ChatWidget />, chatContainer);
  });
}

export default function clientModule() {
  // Docusaurus client module (no-op, rendering happens in DOMContentLoaded)
}
