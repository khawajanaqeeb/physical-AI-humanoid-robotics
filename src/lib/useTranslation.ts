/**
 * useTranslation Hook
 *
 * Custom hook to manage translation state for chapter content.
 * Handles language toggling between English and Urdu with localStorage persistence.
 */

import { useState, useEffect, useCallback } from 'react';

type Language = 'en' | 'ur';

const STORAGE_KEY = 'chapter-language-preference';

export function useTranslation() {
  // Initialize state from localStorage or default to 'en'
  const [language, setLanguageState] = useState<Language>(() => {
    if (typeof window !== 'undefined') {
      const stored = localStorage.getItem(STORAGE_KEY);
      return (stored === 'ur' || stored === 'en') ? stored : 'en';
    }
    return 'en';
  });

  // Persist language preference to localStorage
  useEffect(() => {
    if (typeof window !== 'undefined') {
      localStorage.setItem(STORAGE_KEY, language);
    }
  }, [language]);

  // Toggle between English and Urdu
  const toggleLanguage = useCallback(() => {
    setLanguageState((prev) => (prev === 'en' ? 'ur' : 'en'));
  }, []);

  // Set specific language
  const setLanguage = useCallback((lang: Language) => {
    setLanguageState(lang);
  }, []);

  return {
    language,
    isUrdu: language === 'ur',
    isEnglish: language === 'en',
    toggleLanguage,
    setLanguage,
  };
}
