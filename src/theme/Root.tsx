/**
 * Root wrapper component for Docusaurus
 * Provides AuthContext, UserContext, and TranslationContext to all pages and components
 */
import React from 'react';
import { AuthProvider } from '@site/src/components/auth/AuthContext';
import { UserProvider } from '@site/src/components/auth/UserContext';
import { TranslationProvider } from '@site/src/components/TranslationProvider';

export default function Root({ children }: { children: React.ReactNode }) {
  return (
    <UserProvider>
      <AuthProvider>
        <TranslationProvider>
          {children}
        </TranslationProvider>
      </AuthProvider>
    </UserProvider>
  );
}
