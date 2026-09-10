---
name: video-comment-voc
description: Collect and interpret comments from research videos to analyze VOC, consumer tasks, journey evidence, objections, and feedback about content trust. Use for video-comment VOC research; do not generate a video content landscape workbook unless separately requested.
---

# Video Comment VOC

Interpret comments at the individual-record level before aggregating themes. Keep journey evidence and content-trust feedback related but distinct.

## Success condition

Included comments retain their original meaning and source, aggregated themes can be traced to individual comments and distinct videos, journey updates are evidence-based, and content-trust feedback is not forced into journey stages.

## Required guidance

Read:

- `../../shared/references/research-foundation.md`;
- `../../shared/references/project-state.md`;
- `../../shared/references/runtime-rules.md`;
- `references/voc-analysis-guide.md` for inclusion, interpretation, journey, and trust analysis;
- `references/workbook-schema.md` before creating the workbook.

Use `assets/comment-voc-template.xlsx` as the base reference format when it exists.

## Workflow

1. Read the project scope, available videos, search history, and cached comments.
2. Confirm whether the user means comments from specified videos, the existing project sample, or a newly discovered category sample.
3. Reuse existing video data and collect only missing comments and replies required by the scope.
4. Preserve raw comments and context, then clean duplicates and non-usable records without overwriting the raw source.
5. Interpret each usable comment before theme aggregation.
6. Record user task, meaning, need, decision effect, journey evidence, sentiment direction, and resonance signals when supported.
7. Separately record content-trust feedback about information, demonstrations, filming, speakers, creator credibility, advertising suspicion, corrections, and reply quality.
8. Aggregate by comment count and distinct-video count, preserving representative originals, disagreement, and counter-evidence.
9. Propose journey revisions without creating a second independent journey.
10. Produce `02_评论VOC分析_Comment_VOC.xlsx` and update the project state.

Do not generate the video landscape workbook or Markdown report unless requested.

## Shared programs

- Use `../../shared/scripts/manage_project.py` for state and artifact registration.
- Reuse video IDs recorded by the content skill before making new discovery calls.
- Use the relevant collector only for missing comments or replies.
- Use `../../shared/scripts/process_records.py --kind comment` for normalization and comment-level deduplication.
- Complete AI semantic, journey-evidence, and content-trust fields only after deterministic processing.
- Use `../../shared/scripts/build_excel.mjs` with the comment-VOC template to populate the workbook.
