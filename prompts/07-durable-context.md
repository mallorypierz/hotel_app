# 07 — Create or Refresh Durable Project Context

Purpose: Leave accurate evidence-based context that another contributor can safely resume without reconstructing prior work.

## Copyable prompt

```text
Read AGENTS.md, README.md, all relevant files in docs/, the ordered prompt library, handoffs/create-handoff.md, and handoffs/current.md. Inspect the current project structure, dependency manifests, implemented features, verification scripts, and Git state, treating existing handoff claims as leads that must be checked against the filesystem. Refresh durable project context with concise facts: architecture boundaries, important decisions, current feature state, exact verification commands and results, skipped checks, known risks or blockers, and the clearest next step. Keep docs/design-pipeline.md and docs/verification.md aligned with reality, retain only major reusable prompts under prompts/, and update handoffs/current.md using the handoff template. Do not change application behavior, dependencies, or Git history during this context-only task. Preserve existing visual assets and do not create docs/README.md.
```
