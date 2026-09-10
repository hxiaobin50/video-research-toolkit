---
name: video-research-design
description: Define a category-agnostic video research project, create adaptive search terms, and run a small pilot before collection. Use for project setup, scope definition, search planning, query expansion, or pilot validation; do not run full collection unless the user asks to continue.
---

# Video Research Design

Create a practical research foundation without forcing a fixed search taxonomy, journey, or sample size.

## Success condition

The project scope is clear enough to execute, search terms are traceable and adaptable, the pilot has tested data availability and cost, and the research design workbook is usable as the next skill's input.

## Required guidance

Read:

- `../../shared/references/research-foundation.md`;
- `../../shared/references/project-state.md`;
- `../../shared/references/runtime-rules.md`;
- `references/workbook-schema.md` before creating the workbook.

Use `assets/research-design-template.xlsx` as the base reference format when it exists. Users may add or adjust business fields; preserve system identifiers and provenance fields.

## Workflow

1. Read the user's request and any existing project files.
2. Ask only for missing project details that change the study.
3. Create or update the project configuration.
4. Draft an initial journey hypothesis when useful, clearly marking it as a hypothesis.
5. Generate search terms from the current object, language, research questions, platform language, journey tasks, and user-supplied ideas such as review or recommendation terms.
6. Record why every term was added; do not force terms into preset categories.
7. Check API setup and make a small pilot request on each selected platform.
8. Review relevance, duplication, field availability, comment availability, and expected paid credits.
9. Expand, revise, retain, or stop queries based on observed results.
10. Produce `00_研究设计与证据计划_Research_Design.xlsx` and update the project state.

Stop after the pilot unless the user explicitly asks for formal collection or a complete study.

## Shared programs

- Use `../../shared/scripts/manage_project.py` to create and update project state.
- Use `../../shared/scripts/check_setup.py` before real API calls. Run live checks only after explaining that the ScrapeCreators balance check may consume one credit.
- Use the relevant collector for the small pilot and preserve its collection index.
- Use `../../shared/scripts/build_excel.mjs` with the research-design template to populate the final workbook.
