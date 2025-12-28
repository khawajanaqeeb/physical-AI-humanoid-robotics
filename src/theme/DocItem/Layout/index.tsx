/**
 * DocItem Layout Component (Swizzled)
 *
 * Custom layout for documentation pages that includes the TranslateButton
 * and handles content switching between English and Urdu.
 */

import React, { useState, useEffect, useRef } from 'react';
import clsx from 'clsx';
import { useDoc } from '@docusaurus/plugin-content-docs/client';
import DocItemPaginator from '@theme/DocItem/Paginator';
import DocVersionBanner from '@theme/DocVersionBanner';
import DocVersionBadge from '@theme/DocVersionBadge';
import DocItemFooter from '@theme/DocItem/Footer';
import DocItemTOCMobile from '@theme/DocItem/TOC/Mobile';
import DocItemTOCDesktop from '@theme/DocItem/TOC/Desktop';
import DocItemContent from '@theme/DocItem/Content';
import DocBreadcrumbs from '@theme/DocBreadcrumbs';
import ContentVisibility from '@theme/ContentVisibility';
import type { Props } from '@theme/DocItem/Layout';
import { useTranslationContext } from '../../../components/TranslationProvider';
import TranslateButton from '../../../components/TranslateButton';
import { loadChapterTranslation, ChapterTranslation } from '../../../lib/translationLoader';

import styles from './styles.module.css';

export default function DocItemLayout({ children }: Props): JSX.Element {
  const doc = useDoc();
  const { language, isUrdu } = useTranslationContext();
  const [translation, setTranslation] = useState<ChapterTranslation | null>(null);
  const [isTransitioning, setIsTransitioning] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [scrollPosition, setScrollPosition] = useState(0);
  const contentRef = useRef<HTMLDivElement>(null);

  // Extract chapter path from doc metadata
  const chapterPath = doc.metadata.slug.replace(/^\//, ''); // Remove leading slash

  // Load translation when language changes to Urdu
  useEffect(() => {
    async function fetchTranslation() {
      if (isUrdu) {
        setIsLoading(true);
        setLoadError(null);
        try {
          const loadedTranslation = await loadChapterTranslation(chapterPath);
          setTranslation(loadedTranslation);
          if (!loadedTranslation) {
            setLoadError('Translation not available for this chapter');
          }
        } catch (error) {
          console.error('Error loading translation:', error);
          setLoadError('Failed to load translation. Please try again.');
        } finally {
          setIsLoading(false);
        }
      } else {
        setTranslation(null);
        setLoadError(null);
      }
    }
    fetchTranslation();
  }, [isUrdu, chapterPath]);

  // Handle language change with transition effect and scroll preservation
  useEffect(() => {
    // Save current scroll position before transition
    if (contentRef.current) {
      setScrollPosition(contentRef.current.scrollTop);
    }

    // Add transition effect
    setIsTransitioning(true);
    const timeout = setTimeout(() => {
      setIsTransitioning(false);

      // Restore scroll position after transition (within 50px tolerance)
      if (contentRef.current) {
        contentRef.current.scrollTop = scrollPosition;
      }
    }, 300);

    return () => clearTimeout(timeout);
  }, [language]);

  const contentClassNames = clsx(
    'col',
    isUrdu && 'urdu-content',
    isTransitioning && 'chapter-content transitioning',
    !isTransitioning && 'chapter-content'
  );

  return (
    <div className="row">
      <div className="col col--9">
        <ContentVisibility metadata={doc.metadata}>
          <DocVersionBanner />
          <div className={styles.docItemContainer}>
            <article>
              <DocBreadcrumbs />
              <DocVersionBadge />

              {/* Translate Button - positioned at top of chapter content */}
              <div className={styles.translateButtonContainer}>
                <TranslateButton
                  isAuthenticated={true} // TODO: Replace with actual auth check
                  onLanguageChange={() => {
                    // Handle any additional logic needed on language change
                  }}
                />
              </div>

              <div className={contentClassNames} ref={contentRef}>
                {isUrdu ? (
                  <>
                    {/* Loading state */}
                    {isLoading && (
                      <div className={styles.loadingState}>
                        <p>Loading Urdu translation...</p>
                      </div>
                    )}

                    {/* Error state */}
                    {!isLoading && loadError && (
                      <div className={styles.errorState}>
                        <p>{loadError}</p>
                        <p className={styles.fallbackMessage}>
                          Showing English content instead.
                        </p>
                        <DocItemContent>{children}</DocItemContent>
                      </div>
                    )}

                    {/* Urdu translated content */}
                    {!isLoading && !loadError && translation && (
                      <div className={styles.translatedContent}>
                        <h1>{translation.title}</h1>
                        {Object.entries(translation.content).map(([key, section]) => (
                          <section key={key}>
                            <h2>{section.heading}</h2>
                            {section.items && (
                              <ul>
                                {section.items.map((item, index) => (
                                  <li key={index}>{item}</li>
                                ))}
                              </ul>
                            )}
                            {section.text && <p>{section.text}</p>}
                          </section>
                        ))}
                      </div>
                    )}
                  </>
                ) : (
                  // Render original English content
                  <DocItemContent>{children}</DocItemContent>
                )}
              </div>

              <DocItemFooter />
            </article>
            <DocItemPaginator />
          </div>
        </ContentVisibility>
      </div>
      <div className="col col--3">
        <DocItemTOCDesktop />
      </div>
    </div>
  );
}
