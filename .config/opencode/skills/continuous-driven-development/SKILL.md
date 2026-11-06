---
name: continuous-driven-development
description: Use when an approved implementation plan exists as an absolute artifact path and must be carried out inline
---

# Continuous-Driven Development

Critically review an approved plan, then execute it continuously with
dependency-aware progress and current verification evidence. One bounded executor
performs the detailed preflight and dependent sequence; the main session owns
interaction, decisions and recovery. Read and follow
[the agent workflow contract](../_shared/agent-workflow.md) and
[the artifact policy](../_shared/artifact-policy.md).

## Input Gate

Accept the plan only when the caller supplies an absolute path whose normalized
location is within `~/.agents/docs`. A solve handoff may also supply an optional
latest manifest at an absolute path within `~/.agents/docs`. For direct
invocation, reject a relative path or a path outside that directory and ask for
the correct artifact path. Read an approved specification only when the plan
references one; a separate specification artifact is not an input requirement.

## Workflow

1. Read the coordination index and current recovery record when present. Give one
   bounded executor the approved plan path, any referenced specification paths,
   applicable instructions and constraints, owned paths and evidence paths,
   using [execution-worker.md](execution-worker.md). During normal preflight,
   that executor reads the entire plan and extracts a compact task summary if
   the plan has no index; no separate index-building phase is required. Preserve
   the approved plan. Initialize recovery from the authorized objective and
   available artifact paths for a new direct invocation.
2. Have the executor critically review the full plan and relevant project files
   before edits. For direct invocation, resolve critical concerns with the user
   before editing. For a solve handoff, return the concern and evidence to
   `solve`. Do not guess or silently rewrite the plan.
3. Execute continuously in dependency order, following every plan step and all
   specified and relevant project-declared verification. Keep detailed task
   progress and fresh verification evidence with the executor. The controller
   handles changed requirements, decisions and blockers; the executor re-reads
   relevant plan sections as context changes and pauses affected work when a
   critical assumption or required verification fails.
4. Save compact task status, evidence paths, verification results and next action
   in recovery. Completion requires every task and relevant specified or
   project-declared verification to have current supporting output. Report tasks
   and files completed, commands and observed results, explicitly approved
   deviations, and checks that could not run with their reasons. Never report
   completion while required work or unresolved blockers remain.

Inline here remains one continuous dependent execution sequence. Honor an
explicit request to execute in the main session; if delegation is unavailable,
report the limitation and follow the same execution contract inline.

## Solve Handoff

Re-read a supplied manifest during preflight and whenever context or external
state changes. Preserve its latest path in progress and evidence artifacts.
Return a critical concern or blocker to `solve` rather than asking the user.
After execution, return `status: done | blocked`, `latest_manifest: absolute
path`, `artifact: absolute execution-evidence path`, and concise
`evidence_or_blocker` to `solve`. Do not publish branch state or claim end-to-end
completion.
