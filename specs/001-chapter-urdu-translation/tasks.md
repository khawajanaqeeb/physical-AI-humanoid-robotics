---
description: "Task list for chapter content translation feature (English to Urdu)"
---

# Tasks: Chapter Content Translation (English to Urdu)

**Input**: Design documents from `/specs/001-chapter-urdu-translation/`
**Prerequisites**: spec.md (user story defined), existing Docusaurus project with authentication

**Tests**: Not explicitly requested in the specification - focusing on implementation only.

**Organization**: Tasks are organized to deliver the core translation toggle feature (User Story 1).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1)
- Include exact file paths in descriptions

## Path Conventions

- **Web app structure**: `src/` (frontend React/Docusaurus), `backend/src/` (FastAPI)
- **Docs content**: `docs/` (chapter markdown files)
- **Theme customizations**: `src/theme/` (Docusaurus swizzled components)

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare the translation infrastructure and configure Urdu language support

- [X] T001 Research and configure Urdu font (Noori Nastaleeq) in docusaurus.config.ts
- [X] T002 [P] Add RTL language support configuration to docusaurus.config.ts i18n section
- [X] T003 [P] Install required dependencies for translation (if any) in package.json

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core translation infrastructure that MUST be complete before the toggle feature can work

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Create translation service or hook to manage language state in src/lib/useTranslation.ts
- [X] T005 [P] Configure CSS for Urdu typography (Noori Nastaleeq font) in src/css/custom.css
- [X] T006 [P] Add RTL layout styles in src/css/custom.css
- [X] T007 Determine translation storage strategy (client-side state vs localStorage vs API)
- [X] T008 Create translation context provider (if using React Context) in src/components/TranslationProvider.tsx

**Checkpoint**: Foundation ready - user story implementation can now begin ✅

---

## Phase 3: User Story 1 - Toggle Chapter Language (Priority: P1) 🎯 MVP

**Goal**: Enable logged-in users to toggle chapter content between English and Urdu with a button at the top of each chapter page

**Independent Test**: Can be fully tested by: (1) logging in as a user, (2) navigating to any chapter, (3) clicking the translate button, (4) verifying content appears in Urdu with correct font and RTL layout, and (5) clicking again to return to English.

### Implementation for User Story 1

#### Translation Content & Data

- [X] T009 [P] [US1] Create Urdu translation file/data structure for sample chapter in i18n/ur/docusaurus-plugin-content-docs/current/module-1-ros2/chapter-1-ros2-basics.md (or appropriate format)
- [X] T010 [P] [US1] Define translation content storage format (embedded in markdown frontmatter, separate JSON, or API-based)
- [X] T011 [US1] Implement translation loader utility to fetch Urdu content in src/lib/translationLoader.ts

#### UI Components

- [X] T012 [P] [US1] Create TranslateButton component in src/components/TranslateButton.tsx
- [X] T013 [P] [US1] Add button styling with clear visibility in src/components/TranslateButton.module.css
- [X] T014 [US1] Implement button state toggling logic (Translate to Urdu ↔ Show English)
- [X] T015 [US1] Add animation/transition feedback for language switching

#### Chapter Integration

- [X] T016 [US1] Swizzle or customize DocItem/Layout component to inject TranslateButton at src/theme/DocItem/Layout/index.tsx
- [X] T017 [US1] Position translate button at the top of chapter content area
- [X] T018 [US1] Implement content replacement logic when translation is toggled in chapter view
- [X] T019 [US1] Apply Urdu font (Noori Nastaleeq) and RTL direction when displaying Urdu content
- [X] T020 [US1] Apply English font and LTR direction when displaying English content

#### User Experience Enhancements

- [X] T021 [US1] Implement scroll position preservation (within 50 pixels) during language toggle
- [X] T022 [US1] Add smooth transition animation when switching between languages
- [X] T023 [US1] Ensure navigation and UI chrome remain unchanged during translation
- [X] T024 [US1] Add authentication check - only show button to logged-in users

#### Error Handling & Edge Cases

- [X] T025 [US1] Handle missing Urdu translation gracefully (show message or keep English)
- [X] T026 [US1] Add loading state during translation fetch (if API-based)
- [X] T027 [US1] Implement error handling for translation loading failures

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently ✅

---

## Phase 4: Polish & Cross-Cutting Concerns

**Purpose**: Extend to all chapters and improve overall quality

- [X] T028 [P] Add Urdu translations for sample chapter files (3 chapters for MVP demo)
- [X] T029 [P] Add documentation for translation feature in specs/001-chapter-urdu-translation/README.md
- [X] T030 Verify translation works across sample chapters (tested during implementation)
- [ ] T031 [P] Test responsive design on mobile devices (button visibility, RTL layout) - DEFERRED
- [ ] T032 [P] Performance optimization - lazy load translations only when needed - DEFERRED
- [ ] T033 Accessibility audit - ensure button is keyboard accessible and screen-reader friendly - DEFERRED
- [ ] T034 [P] Add analytics/logging for translation usage tracking - DEFERRED

**Note**: Tasks T031-T034 are deferred for post-MVP iteration. Core functionality is complete and testable.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **Polish (Phase 4)**: Depends on User Story 1 being complete

### Within User Story 1

**Sequence**:
1. Translation Content & Data (T009-T011) - establish how content is stored/loaded
2. UI Components (T012-T015) - build the button component independently
3. Chapter Integration (T016-T020) - integrate button into chapter pages and wire up content switching
4. UX Enhancements (T021-T024) - polish the interaction experience
5. Error Handling (T025-T027) - ensure robustness

**Parallel Opportunities within US1**:
- T009 and T010 can run in parallel (sample translation + format definition)
- T012 and T013 can run in parallel (component + styling)
- After T011 completes: T016, T017, T012-T015 can proceed in parallel
- T021, T022, T023 can be worked on in parallel (different UX concerns)
- T025, T026, T027 can run in parallel (different error scenarios)

### Parallel Opportunities by Phase

- **Phase 1**: T002 and T003 can run in parallel
- **Phase 2**: T005 and T006 can run in parallel (CSS tasks)
- **Phase 3**: See parallel opportunities within US1 above
- **Phase 4**: T028, T029, T031, T032, T033, T034 can all run in parallel

---

## Parallel Example: User Story 1

```bash
# After establishing translation format (T011), work on UI in parallel:
Task: "Create TranslateButton component in src/components/TranslateButton.tsx"
Task: "Add button styling with clear visibility in src/components/TranslateButton.module.css"
Task: "Swizzle DocItem/Layout component at src/theme/DocItem/Layout/index.tsx"

# UX enhancements can be tackled in parallel:
Task: "Implement scroll position preservation during toggle"
Task: "Add smooth transition animation"
Task: "Ensure navigation and UI chrome remain unchanged"

# Error handling tasks can run in parallel:
Task: "Handle missing Urdu translation gracefully"
Task: "Add loading state during translation fetch"
Task: "Implement error handling for translation loading failures"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (font, RTL config, dependencies)
2. Complete Phase 2: Foundational (translation infrastructure, state management)
3. Complete Phase 3: User Story 1 (implement toggle for ONE chapter first)
4. **STOP and VALIDATE**: Test translation toggle on single chapter independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Translation infrastructure ready
2. Add User Story 1 for ONE chapter → Test independently → Demo (MVP!)
3. Extend to all chapters (Phase 4: T028, T030) → Full feature deployed
4. Polish with performance, accessibility, analytics → Production-ready

### Recommended First Implementation

**Start with a single chapter** (e.g., `docs/module-1-ros2/chapter-1-ros2-basics.md`):
1. Create its Urdu translation (T009)
2. Build and test the complete toggle flow on this one chapter (T012-T027)
3. Validate all acceptance criteria from spec.md
4. Once validated, scale to remaining chapters (T028, T030)

---

## Notes

- **Authentication requirement**: Translate button should only appear for logged-in users (T024)
- **Font**: Noori Nastaleeq is specified for Urdu display - ensure it loads correctly
- **RTL Layout**: Must apply `dir="rtl"` when showing Urdu content
- **Scroll preservation**: Critical UX requirement - maintain position within 50px
- **Independent testing**: Feature should work standalone without affecting other site functionality
- **Translation storage**: Decision point at T007/T010 - choose between static files, API, or embedded in markdown
- Commit after each task or logical group
- Stop at checkpoints to validate independently
- Start with one chapter, validate completely, then scale to all chapters
