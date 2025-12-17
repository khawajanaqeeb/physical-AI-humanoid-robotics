/**
 * Chat Widget Entry Point
 *
 * This module renders the floating chat button and modal
 * on all pages using Docusaurus Client API.
 */

import ExecutionEnvironment from '@docusaurus/ExecutionEnvironment';

export default (function () {
  if (!ExecutionEnvironment.canUseDOM) {
    return null;
  }

  function initializeChatWidget() {
    // Import React and components dynamically
    import('react').then((React) => {
      import('react-dom/client').then((ReactDOM) => {
        import('./components/ChatWidget').then((module) => {
          const ChatWidget = module.default;

          // Check if container already exists
          let chatContainer = document.getElementById('rag-chatbot-root');

          if (!chatContainer) {
            // Create mount point for chat widget
            chatContainer = document.createElement('div');
            chatContainer.id = 'rag-chatbot-root';
            document.body.appendChild(chatContainer);

            // Render chat widget using React 18 API
            const root = ReactDOM.createRoot(chatContainer);
            root.render(React.createElement(ChatWidget));
          }
        });
      });
    });
  }

  // Initialize immediately or wait for DOM
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializeChatWidget);
  } else {
    // DOM already loaded
    initializeChatWidget();
  }

  return {
    onRouteUpdate() {
      // Ensure widget persists across page navigation
      setTimeout(initializeChatWidget, 0);
    },
  };
})();
