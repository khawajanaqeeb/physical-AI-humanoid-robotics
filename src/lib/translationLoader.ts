/**
 * Translation Loader Utility
 *
 * Loads Urdu translations for chapter content from JSON files.
 * Handles async loading, caching, and error handling.
 */

export interface ChapterTranslation {
  path: string;
  title: string;
  content: {
    [sectionKey: string]: {
      heading: string;
      items?: string[];
      text?: string;
    };
  };
}

// In-memory cache for loaded translations
const translationCache: Map<string, ChapterTranslation> = new Map();

/**
 * Load translation for a specific chapter
 * @param chapterPath - Path to the chapter (e.g., "module-1-ros2/chapter-1-ros2-basics")
 * @returns Promise resolving to the translation data or null if not found
 */
export async function loadChapterTranslation(
  chapterPath: string
): Promise<ChapterTranslation | null> {
  // Check cache first
  if (translationCache.has(chapterPath)) {
    return translationCache.get(chapterPath)!;
  }

  try {
    // Extract the chapter filename from the path
    const pathParts = chapterPath.split('/');
    const chapterFile = pathParts[pathParts.length - 1];

    // Dynamically import the translation JSON
    // Note: In production, you might use a different loading strategy
    const translationModule = await import(
      `../translations/${chapterFile}.json`
    );

    const translation: ChapterTranslation = translationModule.default || translationModule;

    // Cache the translation
    translationCache.set(chapterPath, translation);

    return translation;
  } catch (error) {
    console.warn(`Translation not found for chapter: ${chapterPath}`, error);
    return null;
  }
}

/**
 * Check if a translation exists for a chapter
 * @param chapterPath - Path to the chapter
 * @returns Promise resolving to true if translation exists, false otherwise
 */
export async function hasTranslation(chapterPath: string): Promise<boolean> {
  const translation = await loadChapterTranslation(chapterPath);
  return translation !== null;
}

/**
 * Preload translations for multiple chapters
 * Useful for optimizing performance by loading translations in advance
 * @param chapterPaths - Array of chapter paths to preload
 */
export async function preloadTranslations(
  chapterPaths: string[]
): Promise<void> {
  await Promise.all(
    chapterPaths.map((path) => loadChapterTranslation(path))
  );
}

/**
 * Clear the translation cache
 * Useful for development or when translations are updated
 */
export function clearTranslationCache(): void {
  translationCache.clear();
}
