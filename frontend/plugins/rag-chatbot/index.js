/**
 * RAG Chatbot Plugin for Docusaurus
 *
 * This plugin adds a floating chat widget to all pages,
 * enabling students to ask questions and receive AI-powered answers.
 */

module.exports = function ragChatbotPlugin(context, options) {
  const { siteConfig } = context;
  const { backendUrl } = options;

  return {
    name: 'rag-chatbot',

    getClientModules() {
      return [require.resolve('./chatWidget.js')];
    },

    // Inject configuration into the client
    injectHtmlTags() {
      return {
        headTags: [
          {
            tagName: 'script',
            innerHTML: `window.__APP_ENV__ = ${JSON.stringify({
              BACKEND_URL: backendUrl,
            })};`,
          },
        ],
      };
    },
  };
};
