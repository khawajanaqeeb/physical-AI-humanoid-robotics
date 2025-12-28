/**
 * TranslateButton Component
 *
 * Toggle button for switching between English and Urdu chapter content.
 * Only visible to authenticated users.
 * Includes state toggling logic and animation feedback.
 */

import React, { useState } from 'react';
import { useTranslationContext } from './TranslationProvider';
import styles from './TranslateButton.module.css';

interface TranslateButtonProps {
  className?: string;
  isAuthenticated?: boolean;
  onLanguageChange?: (language: 'en' | 'ur') => void;
}

export default function TranslateButton({
  className,
  isAuthenticated = true, // Default to true for now, will be replaced with actual auth check
  onLanguageChange,
}: TranslateButtonProps) {
  const { language, toggleLanguage, isUrdu } = useTranslationContext();
  const [isSwitching, setIsSwitching] = useState(false);

  // Don't render button if user is not authenticated
  if (!isAuthenticated) {
    return null;
  }

  const handleClick = async () => {
    // Add switching animation state
    setIsSwitching(true);

    // Trigger language toggle
    toggleLanguage();

    // Notify parent component if callback provided
    if (onLanguageChange) {
      const newLanguage = isUrdu ? 'en' : 'ur';
      onLanguageChange(newLanguage);
    }

    // Reset switching state after animation completes
    setTimeout(() => {
      setIsSwitching(false);
    }, 300); // Match the animation duration in CSS
  };

  const buttonText = isUrdu ? 'Show English' : 'ترجمہ اردو میں';
  const ariaLabel = isUrdu
    ? 'Switch to English'
    : 'Translate to Urdu';

  return (
    <button
      onClick={handleClick}
      className={`${styles.translateButton} ${
        isSwitching ? styles.switching : ''
      } ${className || ''}`}
      aria-label={ariaLabel}
      title={ariaLabel}
      disabled={isSwitching}
    >
      <span className={styles.icon}>
        {isUrdu ? '🇬🇧' : '🇵🇰'}
      </span>
      <span className={styles.label}>{buttonText}</span>
    </button>
  );
}
