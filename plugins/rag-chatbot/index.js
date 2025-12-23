/**
 * RAG Chatbot Plugin for Docusaurus
 *
 * This plugin adds a floating chat widget to all pages,
 * enabling students to ask questions and receive AI-powered answers.
 */

module.exports = function ragChatbotPlugin(context, options) {
  const backendUrl = options.backendUrl || 'http://localhost:8000';

  return {
    name: 'rag-chatbot',

    getClientModules() {
      return [require.resolve('./chatWidget.js')];
    },

    injectHtmlTags() {
      return {
        headTags: [
          {
            tagName: 'script',
            innerHTML: `window.CHATBOT_API_URL = ${JSON.stringify(backendUrl)};`,
          },
        ],
      };
    },
  };
};
