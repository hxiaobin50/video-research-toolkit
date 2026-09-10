---
name: video-research-report
description: Create an evidence-based Markdown report from existing video research artifacts. Use for video landscape, comment VOC, or combined synthesis reports; do not collect new platform data unless the user explicitly expands the request.
---

# Video Research Report

Turn existing evidence into a readable, defensible Markdown analysis rather than a table recap.

## Success condition

The report answers the user's research questions, distinguishes evidence from inference, includes counter-evidence and limitations, and lets the reader jump to original sources without triggering unrelated collection.

## Required guidance

Read:

- `../../shared/references/project-state.md`;
- `../../shared/references/runtime-rules.md`;
- `references/report-guide.md`.

## Workflow

1. Read the requested report scope and project state.
2. Identify which existing workbooks, processed data, raw evidence, and links support that scope.
3. If evidence is insufficient, explain the specific gap and offer options; do not silently launch another Skill.
4. Analyze patterns, differences, contradictions, causes that can be supported, and plausible alternative explanations.
5. Compare video supply, platform performance, manual-viewing observations, VOC demand, journey evidence, and trust feedback where available.
6. State what the evidence supports, what it does not support, and what needs validation.
7. Create the requested Markdown report with concise tables or charts only when they improve understanding.
8. Link conclusions to evidence IDs and original URLs.
9. Update the project state with the report path, scope, and evidence versions used.

The default filename is `03_视频调研分析报告_Video_Research_Report.md`, but a narrower user-requested report may use a clearer scope-specific name.

## Shared programs

- Use `../../shared/scripts/manage_project.py` to discover registered artifacts and record the report version.
- Use `../../shared/scripts/validate_artifacts.py` after writing the report to scan for exposed credentials and missing files.
- Do not call collection programs unless the user explicitly approves an expanded research scope.
