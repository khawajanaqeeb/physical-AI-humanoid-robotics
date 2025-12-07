# Project Coordinator Skill

## Purpose
Manage textbook project tasks, coordinate workflows, ensure quality, and maintain organized documentation structure.

## Coordination Capabilities
- **Task Breakdown**: Decompose large projects into manageable tasks
- **Workflow Planning**: Design efficient multi-step processes
- **Agent Orchestration**: Coordinate multiple specialized agents/skills
- **Progress Tracking**: Monitor task completion and milestones
- **Quality Assurance**: Review and validate content quality
- **Version Control**: Manage updates and iterative improvements
- **Documentation Organization**: Maintain clean file structure
- **Dependency Management**: Track prerequisites and relationships

## When to Use This Skill
- Planning major textbook updates or new sections
- Coordinating complex multi-chapter projects
- Managing iterative content refinement
- Organizing review and feedback cycles
- Restructuring documentation
- Setting up new project components

## Project Management Framework

### 1. Task Analysis
```
PROJECT: [Name]
OBJECTIVE: [Clear goal]
SCOPE: [What's included/excluded]
STAKEHOLDERS: [Who's involved]
DELIVERABLES: [Expected outputs]
```

### 2. Task Breakdown
Break large projects into:
- **Phases**: Major stages of work
- **Milestones**: Key checkpoints
- **Tasks**: Individual work items
- **Dependencies**: What depends on what
- **Resources**: Skills/agents needed

### 3. Workflow Design
```
Phase 1: Research & Planning
  → Task 1.1: Literature review
  → Task 1.2: Outline creation
  → Task 1.3: Resource gathering

Phase 2: Content Creation
  → Task 2.1: Draft writing
  → Task 2.2: Diagram design
  → Task 2.3: Code examples

Phase 3: Review & Refinement
  → Task 3.1: Technical review
  → Task 3.2: Editing & polish
  → Task 3.3: Integration testing
```

### 4. Quality Assurance
- **Content Validation**: Technical accuracy check
- **Style Consistency**: Align with project standards
- **Completeness**: All sections present
- **Cross-references**: Links work correctly
- **Code Testing**: Examples run successfully
- **Accessibility**: Clear for target audience

## Coordination Strategies

### Multi-Agent Workflows
1. **Research Phase**: Use research-analyst skill
2. **Content Creation**: Use technical-writer + robotics-expert
3. **Visual Design**: Use diagram-designer skill
4. **Code Examples**: Use simulation-engineer skill
5. **Curriculum**: Use curriculum-designer skill
6. **Review**: Use code-analyzer agent

### Parallel Execution
Identify independent tasks that can run concurrently:
- Writing different chapters simultaneously
- Creating diagrams while drafting text
- Developing code examples in parallel

### Sequential Dependencies
Respect necessary ordering:
- Research → Outline → Writing
- Draft → Review → Revision
- Code → Test → Documentation

## Project Organization

### File Structure Management
```
docs/
├── chapters/
│   ├── 01-introduction/
│   ├── 02-fundamentals/
│   └── ...
├── figures/
│   ├── chapter-01/
│   └── ...
├── code/
│   ├── examples/
│   └── exercises/
└── resources/
    ├── references/
    └── glossary/
```

### Version Control Best Practices
- Clear commit messages describing changes
- Logical grouping of related updates
- Regular checkpoints for major milestones
- Branch strategy for major revisions

## Output Format

### Project Plan
```markdown
# Project: [Name]

## Overview
[Brief description and goals]

## Phases
### Phase 1: [Name]
- Tasks: [List]
- Skills Needed: [List]
- Timeline: [Estimate]

### Phase 2: [Name]
...

## Success Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Next Steps
1. [Immediate action]
2. [Follow-up action]
```

### Progress Report
```markdown
# Progress Update: [Date]

## Completed
- [Task 1] ✓
- [Task 2] ✓

## In Progress
- [Task 3] (60% complete)

## Blocked
- [Task 4] - Waiting for: [Dependency]

## Next Actions
1. [Priority 1]
2. [Priority 2]
```
