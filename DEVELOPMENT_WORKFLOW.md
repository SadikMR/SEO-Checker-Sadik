# Development Workflow

## Purpose

This document defines the standard development process for the SEO Audit Tool and should be followed throughout the project.

---

## Core Principles

* Follow `seo_tool_specs.md` before every implementation task.
* Build incrementally, phase by phase.
* Implement only the requested scope for the current phase.
* Do not make architectural or functional assumptions.
* Ask for clarification when requirements are unclear.
* Keep changes small, modular, and maintainable.
* Avoid unnecessary refactoring unless required for the current task.

---

## Phase-by-Phase Development

1. Review the current phase goals in `seo_tool_specs.md`.
2. Break the work into small, self-contained tasks.
3. Complete one focused task at a time.
4. Do not introduce future-phase features or assumptions without explicit direction.
5. Validate the implementation against the specification before moving to the next phase.

---

## Implementation Guidelines

* Use the agreed technology stack, project structure, and coding standards.
* Keep backend and frontend responsibilities clearly separated.
* Prefer readable, maintainable, and testable code.
* Follow the DRY (Don't Repeat Yourself) principle and minimize code duplication.
* Reuse existing components, utilities, and logic whenever appropriate.
* Make only the changes required for the current task.
* Preserve existing behavior unless the current task explicitly requires a change.
* If a change makes existing code, logic, or files obsolete, remove or refactor them, provided they are not used elsewhere.
* Avoid dead code, unused imports, duplicate implementations, and unnecessary dependencies.

---

## Git & Collaboration

* Use a dedicated feature branch for each task or phase.
* Make small, atomic commits with meaningful commit messages.
* Keep Pull Requests focused on a single objective.
* Reference the relevant specification or requirement whenever appropriate.

---

## Validation & Definition of Done

A task is complete when:

* The requested feature or change is fully implemented.
* The implementation follows `seo_tool_specs.md` and this workflow.
* Code is clean, modular, and limited to the approved scope.
* Changes have been tested or manually validated.
* Documentation is updated if required.
* No unrelated modifications are included.

---

## Context Recovery

If a new model or contributor continues the project:

1. Read `seo_tool_specs.md`.
2. Read `DEVELOPMENT_WORKFLOW.md`.
3. Review the current project state and the latest prompt before making changes.
4. Use only these documents and the current prompt as the working context.
5. Ask for clarification if any requirement is unclear or missing.
