# Create or Resume a Handoff

## Prompt to Create or Refresh the Handoff

```text
Create or refresh handoffs/current.md so a new coding agent can continue this project without access to this conversation.

The current thread may be too long, the model may have reached an account limit, or another model may take over. Give the next agent enough verified context to continue without guessing.

Before writing, read AGENTS.md, README.md, docs/design-pipeline.md, docs/verification.md, and the relevant files under prompts/. Use the repository as the source of truth. Do not rely on chat memory. Check the current Git branch, HEAD commit, working-tree status, recent commits, configured remotes, and any running project services that can be inspected safely.

The handoff must contain:
1. the current objective and the user's important decisions;
2. a concise architecture and important-file map;
3. the current branch, HEAD commit, relevant branches, upstream relationships, and whether the working tree is clean;
4. completed work, with file paths and commit identifiers where available;
5. incomplete or requested work;
6. exact verification commands already run and their observed results;
7. active services, ports, and how they were started, or a clear statement that none were verified;
8. known failures, unresolved questions, risks, and assumptions;
9. the recommended next action and the files the next agent should read first; and
10. a short list separating verified facts from claims that still require verification.

Do not include secrets, tokens, private URLs, or unnecessary conversation. Do not claim that a check passed unless the evidence is available. Do not change application code, dependencies, Git history, branches, remotes, or running services. Write only handoffs/current.md, then show its path and summarize the evidence used.
```

## Prompt to Check the Handoff Before Resuming

```text
Before resuming work, audit handoffs/current.md against the repository so you do not continue from stale or unsupported context.

Read AGENTS.md, README.md, docs/design-pipeline.md, docs/verification.md, the relevant files under prompts/, and handoffs/current.md. Treat the repository as the source of truth. Independently inspect the current project structure, dependency manifests, Git branch, HEAD commit, working-tree status, recent commits, configured remotes, and any running project services that can be inspected safely.

Check every material handoff claim about the objective, user decisions, architecture, completed and incomplete work, file paths, commit identifiers, verification results, services, ports, failures, risks, assumptions, and recommended next action. Classify each important claim as verified, stale, conflicting, or not yet verified. Do not repeat a claimed test result unless evidence is still available, and do not infer implementation from plans or prompts.

Report the validated current state, discrepancies, unverified claims, risks, and the safest next action. List the files the next agent should read first and any verification command that should be rerun. Do not begin implementation until this audit is complete. Do not change application code, dependencies, Git history, branches, remotes, running services, or handoffs/current.md while performing the check. If a material conflict cannot be resolved from repository evidence, stop and ask the user for direction.
```
