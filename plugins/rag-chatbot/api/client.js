/**
 * API Client for RAG Chatbot
 *
 * Handles communication with the backend API with authentication.
 */

// Get backend URL from window global or use default
// In production, set window.CHATBOT_API_URL in your HTML or via docusaurus config
const API_BASE_URL = typeof window !== 'undefined' && window.CHATBOT_API_URL
  ? window.CHATBOT_API_URL
  : 'http://localhost:8000';

/**
 * Get access token from localStorage
 * @returns {string|null} Access token or null if not found
 */
function getAccessToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('access_token');
}

/**
 * Get refresh token from localStorage
 * @returns {string|null} Refresh token or null if not found
 */
function getRefreshToken() {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem('refresh_token');
}

/**
 * Refresh the access token using the refresh token
 * @returns {Promise<boolean>} True if refresh successful
 */
async function refreshAccessToken() {
  const refreshToken = getRefreshToken();
  if (!refreshToken) return false;

  try {
    const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      credentials: 'include',
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    if (!response.ok) {
      // Refresh token is invalid or expired
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      return false;
    }

    const result = await response.json();

    // Update stored tokens
    localStorage.setItem('access_token', result.access_token);
    if (result.refresh_token) {
      localStorage.setItem('refresh_token', result.refresh_token);
    }

    return true;
  } catch (error) {
    console.error('Failed to refresh token:', error);
    return false;
  }
}

/**
 * Submit a query to the RAG pipeline
 *
 * @param {Object} params
 * @param {string} params.query - User question
 * @param {string} params.session_id - Session UUID
 * @param {string} [params.selected_text] - Optional text selection
 * @param {Object} [params.user_profile] - User profile for personalization
 * @returns {Promise<Object>} Query response with answer and citations
 */
export async function submitQuery({ query, session_id, selected_text, user_profile }) {
  const accessToken = getAccessToken();

  if (!accessToken) {
    throw new Error('Not authenticated');
  }

  const headers = {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${accessToken}`,
  };

  const response = await fetch(`${API_BASE_URL}/api/v1/query`, {
    method: 'POST',
    headers,
    credentials: 'include',
    body: JSON.stringify({
      query: query,  // Cohere API uses 'query' field
      max_results: 5,
      score_threshold: 0.7,
      session_id,  // Include session_id in the request
      selected_text: selected_text || undefined,
      user_profile: user_profile || undefined,  // Include user profile if available
    }),
  });

  if (!response.ok) {
    // Handle 401 Unauthorized - try to refresh token
    if (response.status === 401) {
      const refreshed = await refreshAccessToken();
      if (refreshed) {
        // Retry request with new token
        return submitQuery({ query, session_id, selected_text, user_profile });
      } else {
        // Redirect to signin
        window.location.href = '/auth/signin';
        throw new Error('Session expired. Please sign in again.');
      }
    }

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
  const response = await fetch(`${API_BASE_URL}/api/feedback`, {
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
  const response = await fetch(`${API_BASE_URL}/health`);

  if (!response.ok) {
    throw new Error('Health check failed');
  }

  return await response.json();
}
