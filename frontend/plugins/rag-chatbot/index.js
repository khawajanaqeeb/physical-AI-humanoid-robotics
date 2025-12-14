/**
 * RAG Chatbot Plugin for Docusaurus
 *
 * This plugin adds a floating chat widget to all pages,
 * enabling students to ask questions and receive AI-powered answers.
 */

module.exports = function ragChatbotPlugin(context, options) {
  return {
    name: 'rag-chatbot',

    getClientModules() {
      return [require.resolve('./chatWidget.js')];
    },

    injectHtmlTags() {
      return {
        headTags: [
          {
            tagName: 'link',
            attributes: {
              rel: 'stylesheet',
              href: '/rag-chatbot-styles.css',
            },
          },
        ],
      };
    },
  };
};
