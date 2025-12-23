/**
 * Authentication Context Provider
 * Provides centralized auth state management using Better Auth
 */
import React, { createContext, useContext, useState, useEffect } from 'react';
import { useSession, useSignIn, useSignUp, useSignOut } from '@site/src/lib/auth-client';

interface User {
  id: string;
  email: string;
  profile?: {
    software_experience: string;
    hardware_experience: string;
    interests: string[];
  };
}

interface SignupData {
  email: string;
  password: string;
  software_experience: string;
  hardware_experience: string;
  interests?: string[];
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (data: SignupData) => Promise<void>;
  signout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { data: session, isLoading } = useSession();
  const { mutateAsync: signinMutation } = useSignIn();
  const { mutateAsync: signupMutation } = useSignUp();
  const { mutateAsync: signoutMutation } = useSignOut();

  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    if (session?.user) {
      setUser(session.user as User);
    } else {
      setUser(null);
    }
  }, [session]);

  const signin = async (email: string, password: string) => {
    const result = await signinMutation({ email, password });
    // Manually update user from response
    const profileResponse = await fetch(`${window.CHATBOT_API_URL || 'http://localhost:8000'}/api/v1/profile/`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
      credentials: 'include',
    });
    if (profileResponse.ok) {
      const profileData = await profileResponse.json();
      setUser({
        id: profileData.user_id,
        email: profileData.email,
        profile: {
          software_experience: profileData.software_experience,
          hardware_experience: profileData.hardware_experience,
          interests: profileData.interests || [],
        },
      });
    }
  };

  const signup = async (data: SignupData) => {
    const result = await signupMutation(data);
    // Manually update user from response
    const profileResponse = await fetch(`${(window as any).CHATBOT_API_URL || 'http://localhost:8000'}/api/v1/profile/`, {
      headers: { 'Authorization': `Bearer ${localStorage.getItem('access_token')}` },
      credentials: 'include',
    });
    if (profileResponse.ok) {
      const profileData = await profileResponse.json();
      setUser({
        id: profileData.user_id,
        email: profileData.email,
        profile: {
          software_experience: profileData.software_experience,
          hardware_experience: profileData.hardware_experience,
          interests: profileData.interests || [],
        },
      });
    }
  };

  const signout = async () => {
    await signoutMutation();
    setUser(null);
  };

  const value: AuthContextType = {
    user,
    isAuthenticated: !!user,
    isLoading,
    signin,
    signup,
    signout,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
