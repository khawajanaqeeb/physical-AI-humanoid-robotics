<!-- Sync Impact Report -->
<!--
Version change: 0.0.0 (initial) -> 1.0.0
Modified principles: None
Added sections: Project Standards & Constraints
Removed sections: None
Templates requiring updates:
- .specify/templates/plan-template.md: ✅ updated
- .specify/templates/spec-template.md: ✅ updated
- .specify/templates/tasks-template.md: ✅ updated
- .specify/templates/commands/*.md: ✅ updated
Follow-up TODOs: None
-->
# Physical AI Humanoid Robotics Textbook Constitution

## Core Principles

### I. Fully Spec-Driven Workflow
Every chapter and significant component of the textbook will begin with a clear, explicit specification document (`*.spec.md`). This ensures clarity, consistency, and a shared understanding of requirements before implementation begins.

### II. Technical Accuracy, Clarity, and Educational Focus
All content, code, diagrams, and explanations within the textbook must be technically accurate, clear, and highly focused on pedagogical effectiveness. The primary goal is to educate the target audience (grade level 8–12 clarity) effectively.

### III. Modular Documentation
The textbook's structure will strictly adhere to modular documentation principles, aligning with Docusaurus best practices. This includes well-organized directories, reusable components, and clear content separation for maintainability and scalability.

### IV. Toolchain Fidelity
Development and deployment of the textbook will strictly follow the prescribed toolchain: Spec-Kit Plus for specifications, Claude Code for content generation and assistance, Docusaurus for site generation, and GitHub Pages for deployment. Adherence to this toolchain is non-negotiable to ensure consistency and efficiency.

## Project Standards & Constraints

### Chapter Structure & Count
Each chapter will follow a clear progression: Specification (`.spec.md`) → Implementation/Content Creation → Final Docusaurus Page. The textbook will consist of 12–18 chapters, covering an introduction, setup, robotics fundamentals, AI modules, advanced topics, and deployment.

### Content Formatting & Code Integrity
All content will be written in Markdown/MDX, adhering to Docusaurus best practices for structure and rendering. All embedded code, diagrams, and examples must be correct, runnable, and verifiable.

### Specification & Generation
Specifications will be authored using Spec-Kit Plus, and all associated files and content generation tasks will leverage Claude Code to maintain a spec-driven workflow.

### Accessibility & Deployment
The writing style will target a grade level 8–12 clarity to ensure accessibility for the intended audience. The final Docusaurus site will be deployed to GitHub Pages using recommended configurations to ensure full functionality and maintainability.

## Governance
This constitution supersedes all other project practices. Amendments require a documented proposal, team consensus, and a plan for migration or adaptation. All pull requests and code reviews must verify compliance with these principles. Complexity must always be justified.

**Version**: 1.0.0 | **Ratified**: 2025-12-06 | **Last Amended**: 2025-12-06
