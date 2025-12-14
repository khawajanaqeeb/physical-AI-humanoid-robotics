# ADR-0004: Frontend Integration Strategy

> **Scope**: Document decision clusters, not individual technology choices. Group related decisions that work together (e.g., "Frontend Stack" not separate ADRs for framework, styling, deployment).

- **Status:** Accepted
- **Date:** 2025-12-14
- **Feature:** 002-gemini-rag-chatbot
- **Context:** The chatbot UI must integrate into an existing Docusaurus book without modifying content files. The solution must be portable, maintain visual consistency with the book's theme, and support both desktop and mobile interfaces. The integration strategy affects long-term maintainability, deployment complexity, and user experience.

<!-- Significance checklist (ALL must be true to justify this ADR)
     1) Impact: Long-term consequence for architecture/platform/security?
     2) Alternatives: Multiple viable options considered with tradeoffs?
     3) Scope: Cross-cutting concern (not an isolated detail)?
     If any are false, prefer capturing as a PHR note instead of an ADR. -->

## Decision

We will use a **Docusaurus custom plugin architecture** with React components:

- **Integration Method**: Custom Docusaurus plugin (`docusaurus-plugin-rag-chat`)
- **UI Framework**: React 18+ (matches Docusaurus requirement)
- **Component Architecture**:
  - `<ChatWidget>`: Top-level component injected into theme layout
  - `<ChatButton>`: Floating action button (bottom-right)
  - `<ChatPanel>`: Conversation interface (expandable modal)
  - `<MessageList>`, `<InputBox>`, `<SourceCitation>`: Sub-components
- **State Management**: React `useState` and `useContext` (no Redux)
- **API Client**: Native `fetch` API for backend communication
- **Styling**: Inline CSS-in-JS (styled-components or Emotion) to avoid theme conflicts
- **TypeScript**: Full type safety for props and API contracts
- **Configuration**: Plugin options in `docusaurus.config.js` (API URL, theme colors, position)

## Consequences

### Positive

- **Zero Content Modification**: Plugin injects component into theme layout; existing book pages untouched
- **Native React Integration**: Seamless integration with Docusaurus (already React-based)
- **Portability**: Plugin can be copied to other Docusaurus projects with minimal changes
- **Theme Compatibility**: CSS-in-JS prevents style conflicts with book's custom theme
- **Configuration Flexibility**: Plugin options allow per-site customization without code changes
- **Developer Experience**: Standard React patterns; familiar to Docusaurus contributors
- **Hot Module Replacement**: Fast iteration during development via Docusaurus dev server

### Negative

- **Docusaurus Lock-In**: Plugin architecture specific to Docusaurus; not reusable for other static site generators (Hugo, Jekyll)
- **Build-Time Coupling**: Requires rebuilding Docusaurus site to update plugin code
- **React Version Dependency**: Must match Docusaurus-supported React version (currently 18.x)
- **CSS-in-JS Overhead**: Inline styles increase bundle size compared to static CSS
- **Limited Customization**: Users cannot modify chatbot UI without forking the plugin

## Alternatives Considered

### Alternative 1: Embedded Iframe Widget
- **Pros**: Completely isolated from Docusaurus, can be hosted separately, easier to update independently
- **Cons**: Awkward UX (scrolling issues, mobile responsiveness), styling isolation prevents theme matching, security concerns (CORS, CSP)
- **Why Not Chosen**: Poor user experience; iframe isolation prevents seamless integration with book theme

### Alternative 2: Swizzle Docusaurus Theme Component
- **Pros**: Direct theme modification, maximum control, simpler than plugin architecture
- **Cons**: Breaks on Docusaurus theme updates, harder to port across projects, violates "zero modification" principle
- **Why Not Chosen**: Less maintainable; custom plugin provides better upgrade path and portability

### Alternative 3: Standalone SPA (Separate React App)
- **Pros**: Full control over routing, state management, styling; completely decoupled from book
- **Cons**: Requires separate deployment, awkward navigation between book and chatbot, duplicates header/footer
- **Why Not Chosen**: Breaks user experience continuity; chatbot should feel embedded, not separate

### Alternative 4: Vanilla JavaScript Widget (No React)
- **Pros**: Lightweight, framework-agnostic, can be injected via `<script>` tag
- **Cons**: Loses Docusaurus integration benefits, more complex state management, harder to maintain
- **Why Not Chosen**: React already required by Docusaurus; vanilla JS adds complexity without clear benefit

### Alternative 5: Web Components (Custom Elements)
- **Pros**: Framework-agnostic, standards-based, good encapsulation
- **Cons**: Less mature React interop, awkward data binding, limited Docusaurus ecosystem support
- **Why Not Chosen**: React-based plugin simpler and better supported by Docusaurus community

## References

- Feature Spec: `specs/002-gemini-rag-chatbot/spec.md`
- Implementation Plan: `specs/002-gemini-rag-chatbot/plan.md`
- Research Document: `specs/002-gemini-rag-chatbot/research.md` (Section 6: React Component Integration)
- Project Structure: `specs/002-gemini-rag-chatbot/plan.md` (frontend/ directory layout)
- Related ADRs: ADR-0003 (Backend Stack)
- Evaluator Evidence: To be created during implementation phase
