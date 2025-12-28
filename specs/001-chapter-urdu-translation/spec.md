# Feature Specification: Chapter Content Translation (English to Urdu)

**Feature Branch**: `001-chapter-urdu-translation`
**Created**: 2025-12-28
**Status**: Draft
**Input**: User description: "Enable logged-in users to translate chapter content from English to Urdu by clicking a Translate to Urdu button placed at the start of each chapter"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Toggle Chapter Language (Priority: P1)

A logged-in user reading a chapter in English wants to view the same content in Urdu. They click a clearly visible "Translate to Urdu" button at the top of the chapter page. The chapter content smoothly transitions to display in Urdu using proper Nastaleeq typography and RTL layout, while navigation and UI chrome remain unchanged. The button label changes to "Show English" to indicate the toggle state.

**Why this priority**: This is the core functionality - without it, there's no translation feature. It delivers immediate value by making content accessible to Urdu readers.

**Independent Test**: Can be fully tested by: (1) logging in as a user, (2) navigating to any chapter, (3) clicking the translate button, (4) verifying content appears in Urdu with correct font and RTL layout, and (5) clicking again to return to English.

**Acceptance Scenarios**:

1. **Given** an authenticated user viewing a chapter in English, **When** they click "Translate to Urdu", **Then** the chapter content displays in Urdu with Noori Nastaleeq font and RTL text direction
2. **Given** an authenticated user viewing a chapter in Urdu, **When** they click "Show English", **Then** the chapter content returns to English with LTR text direction
3. **Given** a user switches language, **When** the transition occurs, **Then** their scroll position is preserved within 50 pixels of original location
4. **Given** a user on chapter page, **When** viewing the translate button, **Then** it is clearly visible at the top of the chapter content area
5. **Given** a user toggles language multiple times, **When** switching between Urdu and English, **Then** the transition completes smoothly with visible animation feedback

---

