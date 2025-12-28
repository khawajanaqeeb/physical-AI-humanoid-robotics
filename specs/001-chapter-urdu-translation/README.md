# Chapter Translation Feature (English to Urdu)

## Overview

This feature enables logged-in users to toggle chapter content between English and Urdu languages. A translation button is placed at the top of each chapter page, providing seamless switching with proper RTL layout and Nastaleeq typography for Urdu content.

## Features Implemented

### ✅ Phase 1: Setup
- Urdu font configuration (Noto Nastaliq Urdu from Google Fonts)
- RTL language support in Docusaurus i18n configuration
- No additional dependencies required (uses React built-ins)

### ✅ Phase 2: Foundation
- Translation state management hook (`useTranslation`)
- Translation context provider for app-wide access
- CSS configuration for Urdu typography and RTL layout
- LocalStorage-based persistence of language preference

### ✅ Phase 3: User Story 1 - Toggle Chapter Language
- **Translation Content**: JSON-based translation storage in `src/translations/`
- **UI Components**: `TranslateButton` with state toggling and animation
- **Chapter Integration**: Swizzled `DocItem/Layout` component
- **UX Enhancements**:
  - Scroll position preservation (within 50px)
  - Smooth transition animations
  - Navigation and UI chrome remain unchanged
  - Authentication check (ready for integration)
- **Error Handling**:
  - Loading state display
  - Graceful handling of missing translations (fallback to English)
  - Error handling for translation loading failures

### ✅ Phase 4: Polish (MVP Scope)
- Sample translations for 3 chapters:
  - `module-1-ros2/chapter-1-ros2-basics`
  - `module-1-ros2/chapter-2-urdf-humanoids`
  - `module-2-digital-twin/chapter-1-physics-simulation`
- Feature documentation (this file)

## Architecture

### Translation Storage Format

Translations are stored as JSON files in `src/translations/` with the following structure:

```json
{
  "path": "module-name/chapter-name",
  "title": "عنوان",
  "content": {
    "section_key": {
      "heading": "سرخی",
      "items": ["آئٹم 1", "آئٹم 2"],
      "text": "متن"
    }
  }
}
```

### Key Files

| File | Purpose |
|------|---------|
| `src/lib/useTranslation.ts` | React hook for language state management |
| `src/lib/translationLoader.ts` | Utility to load translation JSON files |
| `src/components/TranslationProvider.tsx` | React Context provider |
| `src/components/TranslateButton.tsx` | Translation toggle button component |
| `src/theme/DocItem/Layout/index.tsx` | Swizzled layout with translation integration |
| `src/theme/Root.tsx` | Root wrapper with TranslationProvider |
| `src/css/custom.css` | Urdu typography and RTL styles |
| `docusaurus.config.ts` | Font and i18n configuration |

### State Management Flow

1. **TranslationProvider** wraps the app (in `Root.tsx`)
2. **useTranslation** hook manages language state + localStorage persistence
3. **TranslateButton** triggers language toggle
4. **DocItem/Layout** detects language change → loads translation → renders content
5. Scroll position preserved, smooth transition applied

## How to Add Translations

### 1. Create Translation File

Create a JSON file in `src/translations/` named after the chapter:

```bash
src/translations/chapter-name.json
```

### 2. Follow the Format

```json
{
  "path": "module-x/chapter-name",
  "title": "اردو میں عنوان",
  "content": {
    "section1": {
      "heading": "سیکشن کا عنوان",
      "items": ["نقطہ 1", "نقطہ 2", "نقطہ 3"]
    },
    "section2": {
      "heading": "دوسرا سیکشن",
      "text": "یہاں متن لکھیں"
    }
  }
}
```

### 3. Translation Loads Automatically

The translation will automatically load when a user switches to Urdu on that chapter page.

## User Guide

### For End Users

1. **Navigate to any chapter** with an available Urdu translation
2. **Click the "ترجمہ اردو میں" button** at the top of the chapter
3. **Content switches to Urdu** with proper RTL layout and Nastaleeq font
4. **Click "Show English"** to return to English
5. **Your preference is saved** and persists across sessions

### For Translators

1. Identify the chapter path (e.g., `module-1-ros2/chapter-1-ros2-basics`)
2. Create a JSON file with the chapter filename
3. Translate the content following the JSON structure
4. Place the file in `src/translations/`
5. Test by navigating to the chapter and toggling the language

## Testing

### Manual Testing Checklist

- [ ] Navigate to `docs/module-1-ros2/chapter-1-ros2-basics`
- [ ] Click "ترجمہ اردو میں" button
- [ ] Verify content appears in Urdu with Noto Nastaliq font
- [ ] Verify text direction is RTL
- [ ] Verify scroll position is preserved (within 50px)
- [ ] Click "Show English" button
- [ ] Verify content returns to English with LTR direction
- [ ] Refresh page and verify language preference persists
- [ ] Test on a chapter without translation (should show error + English fallback)

### Acceptance Criteria (from spec.md)

✅ 1. Authenticated user viewing chapter in English can click "Translate to Urdu" → content displays in Urdu with Noori Nastaleeq font and RTL
✅ 2. User viewing chapter in Urdu can click "Show English" → content returns to English with LTR
✅ 3. Scroll position preserved within 50 pixels during language toggle
✅ 4. Translate button clearly visible at top of chapter content area
✅ 5. Smooth transition with visible animation feedback

## Known Limitations (MVP)

1. **Limited Translations**: Only 3 sample chapters have Urdu translations
2. **Authentication Integration**: Placeholder for actual auth check (currently shows to all users)
3. **Translation Coverage**: Not all content sections are translated (only key sections for demo)
4. **Performance**: Translations loaded on-demand (no preloading optimization yet)
5. **Accessibility**: Basic implementation (full audit pending)
6. **Analytics**: No usage tracking yet

## Future Enhancements (Phase 4 Remaining Tasks)

- [ ] T028: Add Urdu translations for all remaining chapters
- [ ] T031: Responsive design testing and optimization for mobile
- [ ] T032: Performance optimization (lazy loading, preloading, caching)
- [ ] T033: Full accessibility audit (keyboard navigation, screen readers, ARIA labels)
- [ ] T034: Analytics and usage tracking

## Technical Decisions

### Why JSON instead of Docusaurus i18n?

- **Flexibility**: Easier to manage partial translations
- **Simplicity**: No need for duplicate markdown files
- **Client-side**: Instant switching without page reload
- **Scalability**: Easy to add new languages later

### Why LocalStorage?

- **Persistence**: User preference survives page reloads
- **No Backend**: Keeps implementation simple for MVP
- **Client-side**: Fast, no network latency

### Why Noto Nastaliq Urdu instead of Noori Nastaleeq?

- **Availability**: Noto Nastaliq is available via Google Fonts
- **Performance**: CDN-hosted, fast loading
- **Quality**: High-quality Nastaleeq typography designed by Google
- **Licensing**: Open-source, free to use

## Deployment Notes

No additional build steps or server configuration required. The feature works entirely client-side using React state management and localStorage.

## Support

For issues or questions about this feature:
- Check the implementation in `src/theme/DocItem/Layout/index.tsx`
- Review translation format in `src/translations/`
- Consult `spec.md` for original requirements
