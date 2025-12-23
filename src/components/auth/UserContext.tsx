import React, { createContext, useContext, useState, useEffect, useCallback, useRef, ReactNode } from 'react';

// Session timeout constant: 1 hour in milliseconds
const SESSION_TIMEOUT_MS = 60 * 60 * 1000; // 1 hour
// Backend validation interval: 5 minutes
const TOKEN_VALIDATION_INTERVAL_MS = 5 * 60 * 1000; // 5 minutes

// Define the user profile type
interface UserProfile {
  user_id: string;
  email: string;
  software_experience: string;
  hardware_experience: string;
  interests: string[];
  created_at: string;
  last_login_at?: string;
}

// Define the context type
interface UserContextType {
  user: UserProfile | null;
  token: string | null;
  login: (userData: UserProfile, accessToken: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
  updateUserProfile: (profile: Partial<UserProfile>) => void;
}

// Create the context
const UserContext = createContext<UserContextType | undefined>(undefined);

// Provider component
export const UserProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLocalStorageAvailable, setIsLocalStorageAvailable] = useState(true);

  // Refs for timeout and interval timers
  const sessionTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const validationIntervalRef = useRef<NodeJS.Timeout | null>(null);

  // Check localStorage availability
  const checkLocalStorageAvailability = useCallback(() => {
    try {
      const testKey = '__localStorage_test__';
      localStorage.setItem(testKey, 'test');
      localStorage.removeItem(testKey);
      return true;
    } catch (error) {
      console.warn('localStorage is not available:', error);
      return false;
    }
  }, []);

  // Logout function (defined early so callbacks can reference it)
  const logout = useCallback(() => {
    setUser(null);
    setToken(null);

    // Clear session timers
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current);
    }
    if (validationIntervalRef.current) {
      clearInterval(validationIntervalRef.current);
    }

    // Remove from localStorage
    if (isLocalStorageAvailable) {
      localStorage.removeItem('user_profile');
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      localStorage.removeItem('last_activity');
    }
  }, [isLocalStorageAvailable]);

  // Reset session timeout timer
  const resetSessionTimeout = useCallback(() => {
    // Clear existing timeout
    if (sessionTimeoutRef.current) {
      clearTimeout(sessionTimeoutRef.current);
    }

    // Set new timeout for 1 hour
    sessionTimeoutRef.current = setTimeout(() => {
      console.warn('Session timed out due to inactivity');
      logout();
    }, SESSION_TIMEOUT_MS);

    // Update last activity timestamp in localStorage
    if (isLocalStorageAvailable) {
      localStorage.setItem('last_activity', Date.now().toString());
    }
  }, [isLocalStorageAvailable, logout]);

  // Validate token with backend
  const validateTokenWithBackend = useCallback(async () => {
    if (!token) return;

    try {
      const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
      const response = await fetch(`${backendUrl}/auth/profile`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        console.warn('Token validation failed, logging out');
        logout();
      }
    } catch (error) {
      console.error('Error validating token:', error);
      // Don't logout on network errors, only on auth failures
    }
  }, [token, logout]);

  // Load user and token from localStorage on mount
  useEffect(() => {
    // Check localStorage availability on mount
    const isAvailable = checkLocalStorageAvailability();
    setIsLocalStorageAvailable(isAvailable);

    if (!isAvailable) {
      console.warn('localStorage unavailable - session will not persist across page refreshes');
      return;
    }

    const storedUser = localStorage.getItem('user_profile');
    const storedToken = localStorage.getItem('access_token');
    const lastActivity = localStorage.getItem('last_activity');

    if (storedUser && storedToken) {
      try {
        // Check if session has expired
        if (lastActivity) {
          const timeSinceLastActivity = Date.now() - parseInt(lastActivity, 10);
          if (timeSinceLastActivity > SESSION_TIMEOUT_MS) {
            console.warn('Session expired, clearing stored data');
            localStorage.removeItem('user_profile');
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            localStorage.removeItem('last_activity');
            return;
          }
        }

        setUser(JSON.parse(storedUser));
        setToken(storedToken);
        resetSessionTimeout();
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        // Clear invalid data
        localStorage.removeItem('user_profile');
        localStorage.removeItem('access_token');
        localStorage.removeItem('last_activity');
      }
    }
  }, [checkLocalStorageAvailability, resetSessionTimeout]);

  // Activity tracking - reset timeout on user interaction
  useEffect(() => {
    if (!user || !token) return;

    const activityEvents = ['mousedown', 'keydown', 'scroll', 'touchstart'];

    const handleActivity = () => {
      resetSessionTimeout();
    };

    // Add event listeners
    activityEvents.forEach(event => {
      window.addEventListener(event, handleActivity);
    });

    // Initial timeout setup
    resetSessionTimeout();

    // Cleanup
    return () => {
      activityEvents.forEach(event => {
        window.removeEventListener(event, handleActivity);
      });
      if (sessionTimeoutRef.current) {
        clearTimeout(sessionTimeoutRef.current);
      }
    };
  }, [user, token, resetSessionTimeout]);

  // Periodic backend token validation (every 5 minutes)
  useEffect(() => {
    if (!user || !token) return;

    // Validate immediately on mount
    validateTokenWithBackend();

    // Set up interval for periodic validation
    validationIntervalRef.current = setInterval(() => {
      validateTokenWithBackend();
    }, TOKEN_VALIDATION_INTERVAL_MS);

    // Cleanup
    return () => {
      if (validationIntervalRef.current) {
        clearInterval(validationIntervalRef.current);
      }
    };
  }, [user, token, validateTokenWithBackend]);

  // Login function
  const login = (userData: UserProfile, accessToken: string) => {
    setUser(userData);
    setToken(accessToken);

    // Store in localStorage if available
    if (isLocalStorageAvailable) {
      localStorage.setItem('user_profile', JSON.stringify(userData));
      localStorage.setItem('access_token', accessToken);
      localStorage.setItem('last_activity', Date.now().toString());
    }
  };

  // Check if user is authenticated
  const isAuthenticated = () => {
    return !!user && !!token;
  };

  // Update user profile
  const updateUserProfile = (profile: Partial<UserProfile>) => {
    if (user) {
      const updatedUser = { ...user, ...profile };
      setUser(updatedUser);
      if (isLocalStorageAvailable) {
        localStorage.setItem('user_profile', JSON.stringify(updatedUser));
      }
    }
  };

  // Context value
  const value: UserContextType = {
    user,
    token,
    login,
    logout,
    isAuthenticated,
    updateUserProfile,
  };

  return <UserContext.Provider value={value}>{children}</UserContext.Provider>;
};

// Hook to use the context
export const useUser = (): UserContextType => {
  const context = useContext(UserContext);
  if (context === undefined) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};