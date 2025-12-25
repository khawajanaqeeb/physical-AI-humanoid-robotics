/**
 * Custom Auth client for FastAPI backend
 * Provides authentication utilities and React hooks
 */
import { useState, useEffect, useCallback } from 'react';

// Custom error class for better error differentiation
export class AuthError extends Error {
  type: 'network' | 'cors' | 'validation' | 'authentication' | 'server';
  statusCode?: number;
  originalError?: any;

  constructor(message: string, type: string, statusCode?: number, originalError?: any) {
    super(message);
    this.name = 'AuthError';
    this.type = type as any;
    this.statusCode = statusCode;
    this.originalError = originalError;
  }
}

// Helper function to determine error type
const getErrorType = (statusCode: number): string => {
  if (statusCode >= 500) return 'server';
  if (statusCode === 401 || statusCode === 403) return 'authentication';
  if (statusCode === 400) return 'validation';
  if (statusCode >= 400) return 'server';
  return 'server';
};

// Function to make authenticated requests with better error handling
const makeAuthRequest = async (endpoint: string, options: RequestInit) => {
  try {
    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
      credentials: 'include',
      ...options,
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      const errorMessage = errorData.detail || 'Authentication request failed';

      throw new AuthError(
        errorMessage,
        getErrorType(response.status),
        response.status,
        errorData
      );
    }

    return await response.json();
  } catch (error) {
    if (error instanceof AuthError) {
      throw error;
    }

    // Network error (failed to fetch)
    if (error instanceof TypeError && error.message.includes('fetch')) {
      throw new AuthError(
        'Unable to connect to authentication server. Please check your internet connection and try again.',
        'network',
        undefined,
        error
      );
    }

    throw new AuthError(
      'Authentication request failed due to an unexpected error',
      'server',
      undefined,
      error
    );
  }
};

// Get backend URL - use environment variables with fallback to localhost
const getBackendUrl = (): string => {
  // Check for build-time environment variable first
  if (typeof process !== 'undefined' && process.env?.NEXT_PUBLIC_API_URL) {
    return process.env.NEXT_PUBLIC_API_URL;
  }

  // Check for runtime configuration
  if (typeof window !== 'undefined' && (window as any).__ENV__?.API_URL) {
    return (window as any).__ENV__.API_URL;
  }

  // Fallback to localhost for development
  return 'http://localhost:8000';
};

const BACKEND_URL = getBackendUrl();
console.log('[DEBUG] Auth backend URL:', BACKEND_URL);

// Types
export interface User {
  id: string;
  email: string;
  profile?: {
    software_experience: string;
    hardware_experience: string;
    interests: string[];
  };
}

export interface Session {
  user: User | null;
  tokens?: {
    access_token: string;
    refresh_token: string;
  };
}

export interface SignupData {
  email: string;
  password: string;
  software_experience: string;
  hardware_experience: string;
  interests?: string[];
}

// Helper to safely access localStorage
const storage = {
  getItem: (key: string): string | null => {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem(key);
  },
  setItem: (key: string, value: string): void => {
    if (typeof window === 'undefined') return;
    localStorage.setItem(key, value);
  },
  removeItem: (key: string): void => {
    if (typeof window === 'undefined') return;
    localStorage.removeItem(key);
  },
};

// Auth API functions
export const authApi = {
  async signup(data: SignupData) {
    const result = await makeAuthRequest('/api/v1/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify(data),
    });

    // Store tokens
    storage.setItem('access_token', result.tokens.access_token);
    storage.setItem('refresh_token', result.tokens.refresh_token);

    return result;
  },

  async signin(email: string, password: string) {
    const result = await makeAuthRequest('/api/v1/auth/signin', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      credentials: 'include',
      body: JSON.stringify({ email, password }),
    });

    // Store tokens
    storage.setItem('access_token', result.tokens.access_token);
    storage.setItem('refresh_token', result.tokens.refresh_token);

    return result;
  },

  async signout() {
    const refreshToken = storage.getItem('refresh_token');

    if (refreshToken) {
      try {
        await makeAuthRequest('/api/v1/auth/signout', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ refresh_token: refreshToken }),
        });
      } catch (error) {
        // For signout, we still want to clear tokens even if the backend request fails
        console.warn('Signout request failed:', error);
      }
    }

    // Clear tokens
    storage.removeItem('access_token');
    storage.removeItem('refresh_token');
  },

  async getSession(): Promise<Session | null> {
    const AccessToken = storage.getItem('access_token');

    if (!AccessToken) {
      return null;
    }

    try {
      const response = await makeAuthRequest('/api/v1/profile/', {
        method: 'GET',
        headers: { 'Authorization': `Bearer ${AccessToken}` },
        credentials: 'include',
      });

      // Transform profile response to user format
      const user = {
        id: response.user_id,
        email: response.email,
        profile: {
          software_experience: response.software_experience,
          hardware_experience: response.hardware_experience,
          interests: response.interests || [],
        },
      };

      return {
        user,
        tokens: {
          access_token: AccessToken,
          refresh_token: storage.getItem('refresh_token') || '',
        },
      };
    } catch (error) {
      if (error instanceof AuthError && error.statusCode === 401) {
        // Try refresh
        const refreshed = await this.refreshToken();
        if (refreshed) {
          return this.getSession();
        }
      }
      console.error('Session fetch error:', error);
      return null;
    }
  },

  async refreshToken(): Promise<boolean> {
    const refreshToken = storage.getItem('refresh_token');

    if (!refreshToken) {
      return false;
    }

    try {
      const result = await makeAuthRequest('/api/v1/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      storage.setItem('access_token', result.access_token);
      if (result.refresh_token) {
        storage.setItem('refresh_token', result.refresh_token);
      }

      return true;
    } catch (error) {
      // If refresh fails, clear tokens to force re-authentication
      storage.removeItem('access_token');
      storage.removeItem('refresh_token');
      console.error('Token refresh error:', error);
      return false;
    }
  },
};

// React Hooks
export function useSession() {
  const [data, setData] = useState<Session | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Only run in browser
    if (typeof window !== 'undefined') {
      authApi.getSession().then((session) => {
        setData(session);
        setIsLoading(false);
      });
    } else {
      setIsLoading(false);
    }
  }, []);

  return { data, isLoading };
}

export function useSignUp() {
  const [isLoading, setIsLoading] = useState(false);

  const mutateAsync = useCallback(async (data: SignupData) => {
    setIsLoading(true);
    try {
      const result = await authApi.signup(data);
      return result;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { mutateAsync, isLoading };
}

export function useSignIn() {
  const [isLoading, setIsLoading] = useState(false);

  const mutateAsync = useCallback(async ({ email, password }: { email: string; password: string }) => {
    setIsLoading(true);
    try {
      const result = await authApi.signin(email, password);
      return result;
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { mutateAsync, isLoading };
}

export function useSignOut() {
  const [isLoading, setIsLoading] = useState(false);

  const mutateAsync = useCallback(async () => {
    setIsLoading(true);
    try {
      await authApi.signout();
    } finally {
      setIsLoading(false);
    }
  }, []);

  return { mutateAsync, isLoading };
}