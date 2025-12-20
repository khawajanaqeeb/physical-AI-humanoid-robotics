/**
 * API Client for RAG Chatbot
 *
 * Handles communication with the backend API.
 */

// For Docusaurus, we use window.__APP_ENV__ set in docusaurus.config.ts
// This provides a browser-compatible way to access configuration
const getApiBaseUrl = () => {
  // Browser environment: check for custom field in docusaurus config
  if (typeof window !== 'undefined' && window.__APP_ENV__?.BACKEND_URL) {
    return window.__APP_ENV__.BACKEND_URL;
  }

  // Fallback to empty string (will use relative URLs)
  return '';
};

const BASE_URL = getApiBaseUrl();

/**
 * Submit a query to the RAG pipeline
 *
 * @param {Object} params
 * @param {string} params.query - User question
 * @param {string} params.session_id - Session UUID
 * @param {string} [params.selected_text] - Optional text selection
 * @returns {Promise<Object>} Query response with answer and citations
 */
export async function submitQuery({ query, session_id, selected_text }) {
  // Get authentication token from localStorage if available
  const authToken = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  const headers = {
    'Content-Type': 'application/json',
  };

  // Add authorization header if user is authenticated
  if (authToken) {
    headers['Authorization'] = `Bearer ${authToken}`;
  }

  const response = await fetch(`${BASE_URL}/api/v1/query`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      query: query,  // Cohere API uses 'query' field
      max_results: 5,
      score_threshold: 0.7,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));

    // Extract error message
    const errorMessage =
      errorData.error ||
      errorData.detail?.error ||
      `Request failed with status ${response.status}`;

    const error = new Error(errorMessage);
    error.status = response.status;
    error.errorCode = errorData.error_code || errorData.detail?.error_code;
    error.details = errorData.details || errorData.detail?.details;

    throw error;
  }

  return await response.json();
}

/**
 * Submit feedback for a query
 *
 * @param {Object} params
 * @param {string} params.query_id - Query UUID
 * @param {boolean} params.is_helpful - Thumbs up/down
 * @param {string} [params.feedback_text] - Optional text feedback
 * @returns {Promise<Object>} Feedback confirmation
 */
export async function submitFeedback({ query_id, is_helpful, feedback_text }) {
  const response = await fetch(`${BASE_URL}/api/feedback`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      query_id,
      is_helpful,
      feedback_text,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.error || 'Failed to submit feedback');
  }

  return await response.json();
}

/**
 * Check API health
 *
 * @returns {Promise<Object>} Health status
 */
export async function checkHealth() {
  const response = await fetch(`${BASE_URL}/health`);

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return await response.json();
}
