---
name: writing-plans
description: Use when an approved specification or requirements describe a multi-step implementation task
---

# Writing Plans

Create an implementation plan that a capable engineer can execute without hidden
context or invented details. Delegate detailed discovery, drafting and self-review
to a bounded document worker; the main session retains decisions and artifact
paths. Read and follow [the agent workflow contract](../_shared/agent-workflow.md)
and [the artifact policy](../_shared/artifact-policy.md).

## Input and Scope

- Start from an approved specification and retain its absolute path in the plan,
  or from a low-ambiguity solve manifest whose assignment is the authorized
  specification.
- Give the worker applicable project instructions, the approved specification,
  constraints and relevant source paths to inspect before planning changes.
- If independent subsystems cannot form one coherent, testable delivery, split
  them into ordered plans instead of hiding decomposition inside oversized tasks.

## Workflow

1. Dispatch a document worker with [plan-worker.md](plan-worker.md), the input
   paths, constraints, recorded execution route when supplied and a fresh output
   path. The worker discovers source details, exact interfaces and verification
   commands, then writes and self-reviews the plan using the original coverage,
   placeholder, interface, dependency and verification checks in that contract.
2. Read its compact return and coordination index. Resolve missing facts or
   requirements before finalizing the plan; report a blocker when they cannot be
   resolved. Do not invent missing detail. Keep detailed plan content and
   self-review with the worker rather than repeating its investigation.
3. Save the accepted plan path, index and next action in the recovery snapshot.
   For direct invocation, report the absolute plan artifact path, then offer
   subagent-driven-development for independent tasks or
   continuous-driven-development for inline execution. Do not require workspace
   isolation, a branch operation, or a save-to-VCS step.

## Solve Handoff

Preserve the supplied latest manifest path and shape the plan for its recorded
route without offering a choice. A continuous plan uses one sequential executor;
a subagent plan defines bounded task ownership, role intent, dependencies, and
review points. After self-review, return `status: done | blocked`,
`latest_manifest: absolute path`, `artifact: absolute plan path`, and concise
`evidence_or_blocker` to `solve`. Detailed tasks remain in the plan for the
assigned workers to read.
