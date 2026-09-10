---
name: video-content-landscape
description: Research what videos exist across selected platforms, classify their content, calculate available engagement metrics, and select high-value videos for manual viewing. Use for video landscape or content supply research; do not perform comment VOC analysis unless requested separately.
---

# Video Content Landscape

Answer what content exists, how it is distributed, what performs relatively well within comparable groups, and what high-value examples reveal after manual viewing.

## Success condition

Every included video is traceable, relevance and classification are explained by evidence, available platform metrics are calculated correctly, and manual viewing is concentrated on excellent or genuinely ambiguous samples.

## Required guidance

Read:

- `../../shared/references/research-foundation.md`;
- `../../shared/references/project-state.md`;
- `../../shared/references/runtime-rules.md`;
- `references/video-analysis-guide.md` for relevance, classification, performance, and manual viewing;
- `references/workbook-schema.md` before creating the workbook.

Use `assets/video-landscape-template.xlsx` as the base reference format when it exists.

## Workflow

1. Read the project scope, existing search terms, pilot results, and cached data.
2. If the project has no usable search plan, create adaptive terms using the shared research foundation without forcing a separate planning deliverable.
3. Collect or reuse video records from selected platforms.
4. Preserve raw data, normalize fields, deduplicate platform records, and retain every discovery source.
5. Complete relevance review and semantic content classification in one pass where practical.
6. Calculate duration bands and available engagement rates with correct denominators.
7. Analyze each platform and comparable group rather than ranking all platforms as one pool.
8. Select manual-viewing candidates: excellent long videos, excellent short videos, and videos the available evidence cannot classify reliably.
9. Watch selected videos and record only facts actually observed, including useful timestamps.
10. Produce `01_视频内容调研_Video_Landscape.xlsx` and update the project state.

Do not generate the VOC workbook or Markdown report unless the user requests them.

## Shared programs

- Use `../../shared/scripts/manage_project.py` for project state and artifact registration.
- Use `../../shared/scripts/collect_youtube.py` and `collect_scrapecreators.py` only for selected platforms.
- Use `../../shared/scripts/process_records.py --kind video` for normalization, metrics, and platform-level deduplication.
- Complete AI relevance, classification, journey, and manual-review selection after deterministic processing.
- Use `../../shared/scripts/build_excel.mjs` with the video-landscape template to populate the workbook.
