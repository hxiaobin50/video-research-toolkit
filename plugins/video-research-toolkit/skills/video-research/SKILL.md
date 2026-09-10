---
name: video-research
description: Coordinate an end-to-end, category-agnostic video research project when the user requests a complete study or a request spans research design, video landscape, comment VOC, and reporting. Do not use for a single clearly scoped subtask that matches one specialist skill.
---

# Video Research Coordinator

Use natural language to determine which specialist skills are required. Keep the user-facing workflow simple and never generate every deliverable by default.

## Success condition

Complete only the research scope the user requested, reuse available project evidence, and leave every produced conclusion traceable to its source.

## Routing

- Research scope, project setup, search terms, or pilot only: use `video-research-design`.
- What videos exist, what they cover, performance, or manual viewing: use `video-content-landscape`.
- Video comments, VOC, journey needs, objections, or content trust: use `video-comment-voc`.
- Synthesis or a Markdown report from existing evidence: use `video-research-report`.
- A complete study: coordinate the necessary skills in the order justified by the request.

If the request is ambiguous between video content and comment VOC and the answer changes collection cost or output, ask one short clarification. Otherwise make the narrowest reasonable interpretation and state it.

## Shared instructions

Before routing, read:

- `../../shared/references/research-foundation.md` for research scope and adaptive search;
- `../../shared/references/project-state.md` for project reuse and handoffs;
- `../../shared/references/runtime-rules.md` for security, missing data, caching, retry, and evidence rules.

## Workflow

1. Find or establish the project directory.
2. Read `project-config.json` and `.video-research/state.json` if present.
3. Identify the requested deliverable and usable prior artifacts.
4. Ask only for missing information that would materially change execution.
5. State which specialist skill or skills will run and what each will output.
6. Reuse data and analysis already recorded in the project state.
7. Run only the required skills.
8. Summarize outputs, limitations, decisions requiring review, and the logical next optional step.

Do not expand video research into brand positioning, production planning, content calendars, paid media, sales attribution, or GTM unless the user explicitly asks.
