/**
 * Root wrapper component for Docusaurus
 * Provides AuthContext and UserContext to all pages and components
 */
import React from 'react';
import { AuthProvider } from '@site/src/components/auth/AuthContext';
import { UserProvider } from '@site/src/components/auth/UserContext';

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <UserProvider>
      <AuthProvider>
        {children}
      </AuthProvider>
    </UserProvider>
  );
}
