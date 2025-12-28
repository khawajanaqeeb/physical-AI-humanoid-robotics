/**
 * Translation Context Provider
 *
 * Provides translation state and functions throughout the application.
 * Wraps the app to make translation functionality available to all components.
 */

import React, { createContext, useContext, ReactNode } from 'react';
import { useTranslation } from '../lib/useTranslation';

type Language = 'en' | 'ur';

interface TranslationContextValue {
  language: Language;
  isUrdu: boolean;
  isEnglish: boolean;
  toggleLanguage: () => void;
  setLanguage: (lang: Language) => void;
}

const TranslationContext = createContext<TranslationContextValue | undefined>(
  undefined
);

interface TranslationProviderProps {
  children: ReactNode;
}

export function TranslationProvider({ children }: TranslationProviderProps) {
  const translation = useTranslation();

  return (
    <TranslationContext.Provider value={translation}>
      {children}
    </TranslationContext.Provider>
  );
}

/**
 * Hook to access translation context
 * Must be used within a TranslationProvider
 */
export function useTranslationContext() {
  const context = useContext(TranslationContext);
  if (context === undefined) {
    throw new Error(
      'useTranslationContext must be used within a TranslationProvider'
    );
  }
  return context;
}
