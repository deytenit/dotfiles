---
name: continuous-driven-development
description: Use when an approved implementation plan exists as an absolute artifact path and must be carried out inline
---

# Continuous-Driven Development

Critically review an approved plan, then execute it continuously with dependency-aware progress and current verification evidence.

## Input Gate

Accept the plan only when the caller supplies an absolute path whose normalized location is within `~/.agents/docs`. Reject a relative path or a path outside that directory and ask for the correct artifact path.

## Preflight Before Edits

1. Read the entire plan and any approved specification it references.
2. Read the applicable project instructions and the files needed to validate the plan's assumptions.
3. Critically review scope, exact paths, responsibilities, interfaces, dependency order, verification commands, and expected results.
4. Surface contradictions, unsafe actions, missing prerequisites, stale assumptions, or ambiguity that could change the implementation.
5. Resolve critical concerns with the user before editing. Do not guess or silently rewrite the plan.

## Continuous Execution

- Order work by declared dependencies. Among ready tasks, preserve the plan's intended sequence.
- Track pending, active, completed, and blocked work through an available progress-tracking capability. If none exists, maintain an explicit concise status in conversation.
- Execute ready tasks continuously without arbitrary batches or routine pause points.
- Follow every plan step exactly. Do not skip requirements, substitute a different design, or add adjacent work.
- Run every verification specified by the plan and any additional relevant check declared by the project for the affected area. Compare actual output with the plan's expected result.
- After each task, record the files affected and fresh verification evidence before marking it complete.

## Re-check as Context Changes

Re-read the relevant plan sections before each task and whenever the user updates requirements, files change externally, a discovery invalidates an assumption, or verification behaves differently than expected. Re-evaluate dependency order and the remaining steps; report any required plan correction instead of drifting from the approved artifact.

## Blockers

Report an honest blocker immediately when a dependency is unavailable, an instruction is unclear, a critical assumption is false, or verification cannot reach its expected result. Include the affected task, observed evidence, safe checks already attempted, and the decision or external change needed. Pause affected work rather than concealing the blocker or claiming progress.

## Completion

Completion requires every plan task to be finished and every relevant specified or project-declared verification to have current supporting output. At the end, report:

- tasks and files completed;
- verification commands and observed results;
- deviations explicitly approved during execution;
- any verification that could not run and why.

Never report the plan complete while required work or unresolved blockers remain.
