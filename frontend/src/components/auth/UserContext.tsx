import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

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

  // Load user and token from localStorage on mount
  useEffect(() => {
    const storedUser = localStorage.getItem('user_profile');
    const storedToken = localStorage.getItem('access_token');

    if (storedUser && storedToken) {
      try {
        setUser(JSON.parse(storedUser));
        setToken(storedToken);
      } catch (error) {
        console.error('Error parsing stored user data:', error);
        // Clear invalid data
        localStorage.removeItem('user_profile');
        localStorage.removeItem('access_token');
      }
    }
  }, []);

  // Login function
  const login = (userData: UserProfile, accessToken: string) => {
    setUser(userData);
    setToken(accessToken);

    // Store in localStorage
    localStorage.setItem('user_profile', JSON.stringify(userData));
    localStorage.setItem('access_token', accessToken);
  };

  // Logout function
  const logout = () => {
    setUser(null);
    setToken(null);

    // Remove from localStorage
    localStorage.removeItem('user_profile');
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
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
      localStorage.setItem('user_profile', JSON.stringify(updatedUser));
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