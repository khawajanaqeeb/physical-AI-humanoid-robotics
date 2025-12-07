# Tasks: Physical AI Humanoid Robotics Textbook

**Input**: Design documents from `/specs/001-project-create-textbook/`
**Prerequisites**: plan.md (required), spec.md (required for user stories)

**Tests**: The feature specification does not explicitly request test tasks in a TDD manner; however, validation checks are defined. Tasks will include validation steps.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `- [ ] [ID] [P?] [Story?] Description with file path`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- All Docusaurus documentation and associated files will be created under the `/docs` directory at the repository root.

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic Docusaurus structure

- [X] T001 Initialize Docusaurus project in `/` (repo root)
- [X] T002 Configure Docusaurus `docusaurus.config.ts` with basic settings for the textbook project
- [X] T003 Create `/docs` directory at the repository root
- [X] T004 Create `docs/introduction` directory
- [X] T005 Create `docs/module-1-ros2` directory
- [X] T006 Create `docs/module-2-digital-twin` directory
- [X] T007 Create `docs/module-3-isaac` directory
- [X] T008 Create `docs/module-4-vla` directory
- [X] T009 Create `docs/weekly-breakdowns` directory
- [X] T010 Create `docs/assessments` directory
- [X] T011 Create `docs/hardware` directory
- [X] T012 Create `docs/lab-setup` directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core Docusaurus navigation and structural elements that MUST be complete before ANY user story content can be added.

**⚠️ CRITICAL**: No user story content creation can begin until this phase is complete

- [X] T013 Create `docs/introduction/_category_.json` for sidebar configuration
- [X] T014 Create `docs/module-1-ros2/_category_.json` for sidebar configuration
- [X] T015 Create `docs/module-2-digital-twin/_category_.json` for sidebar configuration
- [X] T016 Create `docs/module-3-isaac/_category_.json` for sidebar configuration
- [X] T017 Create `docs/module-4-vla/_category_.json` for sidebar configuration
- [X] T018 Create `docs/weekly-breakdowns/_category_.json` for sidebar configuration
- [X] T019 Create `docs/assessments/_category_.json` for sidebar configuration
- [X] T020 Create `docs/hardware/_category_.json` for sidebar configuration
- [X] T021 Create `docs/lab-setup/_category_.json` for sidebar configuration
- [X] T022 Define sidebar items in `docusaurus.config.ts` to reflect the module hierarchy
- [X] T023 Run Docusaurus local build to validate basic navigation and structure

**Checkpoint**: Foundation ready - user story content creation can now begin

---

## Phase 3: User Story 1 - Define High-Level Textbook Layout (Priority: P1) 🎯 MVP

**Goal**: Establish the overarching structure and placeholder content for all major sections and chapters, delivering a clear content roadmap.

**Independent Test**: Review the generated Docusaurus site locally to ensure all high-level sections and chapter placeholders are present and logically ordered, aligning with `spec.md` FR-001 through FR-009.

### Implementation for User Story 1

- [X] T024 [P] [US1] Create placeholder `docs/introduction/index.md` for the Introduction to Physical AI
- [X] T025 [P] [US1] Create placeholder `docs/module-1-ros2/chapter-1-ros2-basics.md`
- [X] T026 [P] [US1] Create placeholder `docs/module-1-ros2/chapter-2-urdf-humanoids.md`
- [X] T027 [P] [US1] Create placeholder `docs/module-2-digital-twin/chapter-1-physics-simulation.md`
- [X] T028 [P] [US1] Create placeholder `docs/module-2-digital-twin/chapter-2-gazebo-unity-environments.md`
- [X] T029 [P] [US1] Create placeholder `docs/module-3-isaac/chapter-1-isaac-sim.md`
- [X] T030 [P] [US1] Create placeholder `docs/module-3-isaac/chapter-2-isaac-ros-navigation.md`
- [X] T031 [P] [US1] Create placeholder `docs/module-4-vla/chapter-1-whisper-llms.md`
- [X] T032 [P] [US1] Create placeholder `docs/module-4-vla/chapter-2-capstone-pipeline.md`
- [X] T033 [P] [US1] Create placeholder `docs/weekly-breakdowns/week-1-overview.md`
- [X] T034 [P] [US1] Create placeholder `docs/assessments/ros2-project.md`
- [X] T035 [P] [US1] Create placeholder `docs/hardware/workstation-jetson.md`
- [X] T036 [P] [US1] Create placeholder `docs/lab-setup/on-prem-cloud.md`

**Checkpoint**: At this point, User Story 1 should be fully implemented with high-level content and testable independently.

---

## Phase 4: User Story 2 - Elaborate Detailed Module Specifications (Priority: P1)

**Goal**: Expand each module's content to include detailed specifications such as learning objectives, prerequisites, required tools, chapter structure, and module-specific deep specs, providing comprehensive guidance for content creation.

**Independent Test**: Examine individual module chapter files locally to confirm the presence and completeness of all required detailed sections (Learning Objectives, Prerequisites, Required Tools, Chapter Structure, and Module-Specific Deep Specs), delivering actionable guidance for content. Validates alignment with `spec.md` FR-010 through FR-014.

### Implementation for User Story 2

- [X] T037 [P] [US2] Add Learning Objectives section to `docs/introduction/index.md`
- [X] T038 [P] [US2] Add Prerequisites section to `docs/introduction/index.md`
- [X] T039 [P] [US2] Add Required Tools section to `docs/introduction/index.md`
- [X] T040 [P] [US2] Add Chapter Structure outline to `docs/introduction/index.md`
- [X] T041 [P] [US2] Add Module-Specific Deep Specs (Introduction) to `docs/introduction/index.md`
- [X] T042 [P] [US2] Add Learning Objectives section to `docs/module-1-ros2/chapter-1-ros2-basics.md`
- [X] T043 [P] [US2] Add Prerequisites section to `docs/module-1-ros2/chapter-1-ros2-basics.md`
- [X] T044 [P] [US2] Add Required Tools section to `docs/module-1-ros2/chapter-1-ros2-basics.md`
- [X] T045 [P] [US2] Add Chapter Structure outline to `docs/module-1-ros2/chapter-1-ros2-basics.md`
- [X] T046 [P] [US2] Add Module-Specific Deep Specs (ROS 2) to `docs/module-1-ros2/chapter-1-ros2-basics.md` (e.g., Node lifecycle states, Topic QoS)
- [X] T047 [P] [US2] Add Learning Objectives section to `docs/module-1-ros2/chapter-2-urdf-humanoids.md`
- [X] T048 [P] [US2] Add Prerequisites section to `docs/module-1-ros2/chapter-2-urdf-humanoids.md`
- [X] T049 [P] [US2] Add Required Tools section to `docs/module-1-ros2/chapter-2-urdf-humanoids.md`
- [X] T050 [P] [US2] Add Chapter Structure outline to `docs/module-1-ros2/chapter-2-urdf-humanoids.md`
- [X] T051 [P] [US2] Add Module-Specific Deep Specs (URDF) to `docs/module-1-ros2/chapter-2-urdf-humanoids.md` (e.g., Parsing URDF, `ros2_control` usage)
- [X] T052 [P] [US2] Add Learning Objectives section to `docs/module-2-digital-twin/chapter-1-physics-simulation.md`
- [X] T053 [P] [US2] Add Prerequisites section to `docs/module-2-digital-twin/chapter-1-physics-simulation.md`
- [X] T054 [P] [US2] Add Required Tools section to `docs/module-2-digital-twin/chapter-1-physics-simulation.md`
- [X] T055 [P] [US2] Add Chapter Structure outline to `docs/module-2-digital-twin/chapter-1-physics-simulation.md`
- [X] T056 [P] [US2] Add Module-Specific Deep Specs (Physics) to `docs/module-2-digital-twin/chapter-1-physics-simulation.md` (e.g., Gravity, collisions, sensors)
- [X] T057 [P] [US2] Add Learning Objectives section to `docs/module-2-digital-twin/chapter-2-gazebo-unity-environments.md`
- [X] T058 [P] [US2] Add Prerequisites section to `docs/module-2-digital-twin/chapter-2-gazebo-unity-environments.md`
- [X] T059 [P] [US2] Add Required Tools section to `docs/module-2-digital-twin/chapter-2-gazebo-unity-environments.md`
- [X] T060 [P] [US2] Add Chapter Structure outline to `docs/module-2-digital-twin/chapter-2-gazebo-unity-environments.md`
- [X] T061 [P] [US2] Add Module-Specific Deep Specs (Gazebo/Unity) to `docs/module-2-digital-twin/chapter-2-gazebo-unity-environments.md` (e.g., SDF vs URDF, Multi-camera rigs)
- [X] T062 [P] [US2] Add Learning Objectives section to `docs/module-3-isaac/chapter-1-isaac-sim.md`
- [X] T063 [P] [US2] Add Prerequisites section to `docs/module-3-isaac/chapter-1-isaac-sim.md`
- [X] T064 [P] [US2] Add Required Tools section to `docs/module-3-isaac/chapter-1-isaac-sim.md`
- [X] T065 [P] [US2] Add Chapter Structure outline to `docs/module-3-isaac/chapter-1-isaac-sim.md`
- [X] T066 [P] [US2] Add Module-Specific Deep Specs (Isaac Sim) to `docs/module-3-isaac/chapter-1-isaac-sim.md` (e.g., Scene graph, USD pipelines)
- [X] T067 [P] [US2] Add Learning Objectives section to `docs/module-3-isaac/chapter-2-isaac-ros-navigation.md`
- [X] T068 [P] [US2] Add Prerequisites section to `docs/module-3-isaac/chapter-2-isaac-ros-navigation.md`
- [X] T069 [P] [US2] Add Required Tools section to `docs/module-3-isaac/chapter-2-isaac-ros-navigation.md`
- [X] T070 [P] [US2] Add Chapter Structure outline to `docs/module-3-isaac/chapter-2-isaac-ros-navigation.md`
- [X] T071 [P] [US2] Add Module-Specific Deep Specs (Isaac ROS) to `docs/module-3-isaac/chapter-2-isaac-ros-navigation.md` (e.g., VSLAM, Nav2 for biped locomotion)
- [X] T072 [P] [US2] Add Learning Objectives section to `docs/module-4-vla/chapter-1-whisper-llms.md`
- [X] T073 [P] [US2] Add Prerequisites section to `docs/module-4-vla/chapter-1-whisper-llms.md`
- [X] T074 [P] [US2] Add Required Tools section to `docs/module-4-vla/chapter-1-whisper-llms.md`
- [X] T075 [P] [US2] Add Chapter Structure outline to `docs/module-4-vla/chapter-1-whisper-llms.md`
- [X] T076 [P] [US2] Add Module-Specific Deep Specs (VLA) to `docs/module-4-vla/chapter-1-whisper-llms.md` (e.g., Whisper speech-to-intent, LLM task planners)
- [X] T077 [P] [US2] Add Learning Objectives section to `docs/module-4-vla/chapter-2-capstone-pipeline.md`
- [X] T078 [P] [US2] Add Prerequisites section to `docs/module-4-vla/chapter-2-capstone-pipeline.md`
- [X] T079 [P] [US2] Add Required Tools section to `docs/module-4-vla/chapter-2-capstone-pipeline.md`
- [X] T080 [P] [US2] Add Chapter Structure outline to `docs/module-4-vla/chapter-2-capstone-pipeline.md`
- [X] T081 [P] [US2] Add Module-Specific Deep Specs (Capstone) to `docs/module-4-vla/chapter-2-capstone-pipeline.md` (e.g., Voice → Plan → Navigate → Perceive → Manipulate)
- [X] T082 [P] [US2] Add Learning Objectives section to `docs/weekly-breakdowns/week-1-overview.md`
- [X] T083 [P] [US2] Add Prerequisites section to `docs/weekly-breakdowns/week-1-overview.md`
- [X] T084 [P] [US2] Add Required Tools section to `docs/weekly-breakdowns/week-1-overview.md`
- [X] T085 [P] [US2] Add Chapter Structure outline to `docs/weekly-breakdowns/week-1-overview.md`
- [X] T086 [P] [US2] Add Module-Specific Deep Specs (Weekly Breakdown) to `docs/weekly-breakdowns/week-1-overview.md` (e.g., lecture expansions, tutorials)
- [X] T087 [P] [US2] Add Learning Objectives section to `docs/assessments/ros2-project.md`
- [X] T088 [P] [US2] Add Prerequisites section to `docs/assessments/ros2-project.md`
- [X] T089 [P] [US2] Add Required Tools section to `docs/assessments/ros2-project.md`
- [X] T090 [P] [US2] Add Chapter Structure outline to `docs/assessments/ros2-project.md`
- [X] T091 [P] [US2] Add Module-Specific Deep Specs (Assessments) to `docs/assessments/ros2-project.md` (e.g., ROS 2 project guidelines)
- [X] T092 [P] [US2] Add Learning Objectives section to `docs/hardware/workstation-jetson.md`
- [X] T093 [P] [US2] Add Prerequisites section to `docs/hardware/workstation-jetson.md`
- [X] T094 [P] [US2] Add Required Tools section to `docs/hardware/workstation-jetson.md`
- [X] T095 [P] [US2] Add Chapter Structure outline to `docs/hardware/workstation-jetson.md`
- [X] T096 [P] [US2] Add Module-Specific Deep Specs (Hardware) to `docs/hardware/workstation-jetson.md` (e.g., Jetson edge kits, Unitree robots)
- [X] T097 [P] [US2] Add Learning Objectives section to `docs/lab-setup/on-prem-cloud.md`
- [X] T098 [P] [US2] Add Prerequisites section to `docs/lab-setup/on-prem-cloud.md`
- [X] T099 [P] [US2] Add Required Tools section to `docs/lab-setup/on-prem-cloud.md`
- [X] T100 [P] [US2] Add Chapter Structure outline to `docs/lab-setup/on-prem-cloud.md`
- [X] T101 [P] [US2] Add Module-Specific Deep Specs (Lab Setup) to `docs/lab-setup/on-prem-cloud.md` (e.g., Cost models, Latency traps)

**Checkpoint**: All user stories should now be independently functional.

---

## Phase 5: Landing Page Image and Footer Update (Priority: P1)

**Goal**: Fix the landing-page image that is not showing in the Docusaurus site, and update the footer so it contains links to all textbook modules and all chapter pages as an "Introduction" section.

### Implementation for Phase 5

- [X] T102 Create static directory structure for Docusaurus assets in `static/img/`
- [X] T103 Create placeholder hero image file `static/img/hero-image.jpg`
- [X] T104 Create landing page directory `src/pages/`
- [X] T105 Create landing page component `src/pages/index.js` with hero image
- [X] T106 Create landing page CSS module `src/pages/index.module.css`
- [X] T107 Create HomepageFeatures component directory `src/components/`
- [X] T108 Create HomepageFeatures component `src/components/HomepageFeatures.js`
- [X] T109 Create HomepageFeatures CSS module `src/components/HomepageFeatures.module.css`
- [X] T110 Update footer in `docusaurus.config.ts` to include all modules and chapters under "Introduction" section
- [X] T111 Verify landing page image loads successfully
- [X] T112 Test footer rendering with all module and chapter links

**Checkpoint**: Landing page image loads successfully and footer displays all module + chapter links under "Introduction".

---

## Phase 6: Fix Missing SVG Images (Priority: P1)

**Goal**: Fix the Docusaurus build errors caused by missing SVG images that components are trying to import.

### Implementation for Phase 6

- [X] T113 Check if /static/img/ contains undraw_docusaurus_mountain.svg
- [X] T114 Check if /static/img/ contains undraw_docusaurus_tree.svg
- [X] T115 Check if /static/img/ contains undraw_docusaurus_react.svg
- [X] T116 Create placeholder undraw_docusaurus_mountain.svg in static/img/
- [X] T117 Create placeholder undraw_docusaurus_tree.svg in static/img/
- [X] T118 Create placeholder undraw_docusaurus_react.svg in static/img/
- [X] T119 Verify all components import SVGs without module errors
- [X] T120 Test Docusaurus dev server compiles without errors
- [X] T121 Ensure HomepageFeatures component renders without broken images

**Checkpoint**: Docusaurus dev server compiles with ZERO errors and all components render without missing images.

---

## Phase 7: Remove Images from Landing Page (Priority: P1)

**Goal**: Modify the landing page to become minimal and clean by removing all images and logo references.

### Implementation for Phase 7

- [X] T122 Remove all image imports and usage from src/pages/index.js
- [X] T123 Remove hero image from landing page component
- [X] T124 Remove HomepageFeatures component usage from landing page (or make it optional)
- [X] T125 Remove all image imports and SVG references from src/components/HomepageFeatures.js
- [X] T126 Simplify HomepageFeatures component to text-only format
- [X] T127 Remove logo block from navbar in docusaurus.config.ts
- [X] T128 Verify landing page loads correctly with only text content
- [X] T129 Ensure build succeeds with zero image-related module errors

**Checkpoint**: Landing page is now a clean text-only page with sidebar + footer, and the build succeeds with zero image-related module errors.

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements and validations that affect multiple user stories or the overall textbook quality.

- [X] T130 Review overall content consistency and terminology across all modules and chapters
- [X] T131 Run Docusaurus local build to validate entire textbook structure and content rendering (`npm run build` or `yarn build`)
- [X] T132 Format all APA citations for research notes according to standards
- [X] T133 Ensure all embedded code examples are valid, runnable, and correctly formatted
- [X] T134 Perform final review of textbook for grade level 8-12 clarity and educational effectiveness

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3 & 4)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P1)
- **Landing Page & Footer (Phase 5)**: Can run in parallel with user stories
- **SVG Image Fixes (Phase 6)**: Can run in parallel with other phases
- **Polish (Phase 7)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories

### Within Each User Story

- Tasks related to creating directories should precede creating files within those directories.
- Basic content placeholders should be created before detailed specifications are added.

### Parallel Opportunities

- All Setup tasks (Phase 1) marked [P] can run in parallel.
- All Foundational tasks (Phase 2) marked [P] can run in parallel.
- Once Foundational phase completes, both User Story 1 and User Story 2 can start in parallel (if team capacity allows).
- Within User Story 1 and User Story 2, tasks marked [P] can run in parallel (e.g., creating multiple chapter placeholders, adding detailed specs to different files).

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Review the high-level layout locally and ensure all main sections are present.

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 (High-level layout) → Validate independently → Review and iterate
3. Add User Story 2 (Detailed module specs) → Validate independently → Review and iterate
4. Complete Landing Page & Footer phase → Validate independently → Review and iterate
5. Complete SVG Image fixes → Validate independently → Review and iterate
6. Complete Polish phase → Final validation and quality checks

### Parallel Team Strategy

With multiple content developers:

1. Team completes Setup + Foundational together.
2. Once Foundational is done:
   - Developer A: User Story 1 (creating high-level chapter placeholders across modules)
   - Developer B: User Story 2 (adding detailed specs to individual chapter files, potentially in parallel with A, or after A for a specific module).
3. Landing Page & Footer can be developed in parallel
4. SVG Image fixes can be developed in parallel
5. Stories complete and integrate independently.

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence