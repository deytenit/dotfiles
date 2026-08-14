---
name: subagent-driven-development
description: Use when executing a written implementation plan with bounded tasks in the current session
---

# Subagent-Driven Development

## Overview

Execute a written plan through bounded implementation tasks and independent combined reviews. Keep tightly coupled work sequential, preserve progress in durable artifacts, and stop repeated correction loops with a concrete blocker.

## Durable Artifacts

Before creating a progress document, task brief, implementer report, or review document, read and follow [the shared artifact policy](../_shared/artifact-policy.md). Put every document directly in the resolved scope directory. Use names such as:

```text
YYYY-MM-DD-HHMMSS-subagent-driven-development-<plan-slug>-progress.md
YYYY-MM-DD-HHMMSS-subagent-driven-development-<plan-slug>-task-<N>-brief.md
YYYY-MM-DD-HHMMSS-subagent-driven-development-<plan-slug>-task-<N>-report.md
YYYY-MM-DD-HHMMSS-subagent-driven-development-<plan-slug>-task-<N>-report-correction-<R>.md
YYYY-MM-DD-HHMMSS-subagent-driven-development-<plan-slug>-task-<N>-review.md
YYYY-MM-DD-HHMMSS-subagent-driven-development-<plan-slug>-task-<N>-review-correction-<R>.md
```

The initial implementation uses the task report name. Each correction round gets a fresh, uniquely named correction report; never replace an earlier report. Give that report path to the correcting implementer and pass the same path to the scoped re-review. Each progress update is also a fresh, uniquely named artifact; the latest one is the recovery record. Record a task as complete only after its review passes.

When a solve handoff supplies a manifest, preserve its absolute path in every progress document, task brief, implementer report, review document, and recovery record.

## Solve Handoff

When a solve handoff supplies a manifest, return `status: done | blocked`, `latest_manifest: absolute path`, `artifact: absolute integrated review-and-verification path`, and concise `evidence_or_blocker` to `solve`. Do not invoke a finishing workflow or claim end-to-end completion.

## Lifecycle

1. Read the plan once. Before dispatch, reject internal contradictions and requirements that conflict with applicable constraints.
2. Work directly for a small or tightly coupled plan. Otherwise dispatch one `implementer` per bounded task, sequentially unless the plan explicitly proves disjoint file ownership.
3. Give the worker only its task brief, applicable constraints, earlier interfaces it consumes, and the implementer-report path.
4. Handle `DONE`, `DONE_WITH_CONCERNS`, `NEEDS_CONTEXT`, and `BLOCKED` according to their meaning; never repeat an unchanged dispatch blindly.
5. Dispatch one `checker` for a combined requirements and quality review.
6. Resume the same implementer for a substantial correction when the client supports resumption; otherwise dispatch one corrected task. Stop after three unsuccessful correction rounds and report the concrete blocker.
7. Write a fresh progress artifact only after both review verdicts pass and required verification gaps are resolved.
8. Run one final integrated `checker` only when the combined change is broad or risky.
9. Report completion and verification evidence without invoking a branch-finishing workflow.

## Task Dispatch

Create a bounded brief from the plan. The brief owns the exact task requirements; do not send the worker the entire plan or accumulated session history. State writable paths explicitly and keep ownership disjoint before any parallel implementation.

Use [implementer-prompt.md](implementer-prompt.md). An implementer must never spawn additional agents.

## Status Handling

- `DONE`: proceed to the combined task review.
- `DONE_WITH_CONCERNS`: inspect the concerns and resolve correctness or scope uncertainty before review; otherwise preserve the concern in the report and proceed.
- `NEEDS_CONTEXT`: provide only the missing information, then resume or issue one corrected task.
- `BLOCKED`: diagnose the stated blocker, change the brief or context when that can resolve it, and stop when progress requires a user decision or unavailable capability.

Status is evidence, not a retry signal. Never repeat the same prompt after `NEEDS_CONTEXT` or `BLOCKED`.

## Combined Review

Use [task-reviewer-prompt.md](task-reviewer-prompt.md) with one `checker`. Supply the requirements path, implementer-report path, relevant changed paths, and verification evidence. The checker returns both requirements and quality verdicts using the contract from [requesting-code-review](../requesting-code-review/code-reviewer.md).

The controller saves every checker result as a fresh, uniquely named review artifact under the shared artifact policy. Use the task review name for the initial review and a correction suffix for each scoped re-review; never replace an earlier review artifact.

If the checker finds a substantial problem, send its exact findings to the same implementer when resumption is available. Otherwise dispatch one corrected implementation task with the findings and fix scope. Use [re-review-prompt.md](re-review-prompt.md) to verify only the prior findings against the correction.

One correction round consists of one correction and one scoped re-review. After three unsuccessful rounds, stop and report the remaining findings, attempted corrections, and concrete blocker. Do not reopen the full task during a scoped re-review.

## Completion Gate

A task is complete only when:

- Requirements pass.
- Quality is approved.
- Verification gaps are resolved.
- Its latest progress and review artifacts are current.

An unresolved verification gap keeps the task blocked and incomplete. Report the gap and the evidence or capability needed to resolve it; do not mark progress complete.

Workers do not delegate. The controller owns dispatch, integration, progress, review-artifact persistence, and escalation.
