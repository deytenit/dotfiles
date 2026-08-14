---
name: solve
description: Use when a ticket identifier or raw development assignment should be carried autonomously from workspace preparation through verified implementation and draft review publication
---

# Solve

Carry one ticket or text assignment from state preparation through verified implementation and final branch storage.

## Authority and Completion

Explicit invocation authorizes in-scope workspace preparation, semantic commits, safe branch synchronization, and draft unassigned review publication. Only `brainstorming` may ask the user questions. Other stages continue from discovered evidence, use a defined fallback, or return an evidence-backed blocker.

Missing issue, remote, or review capability permits local completion. Missing correctness evidence does not. Do not merge, assign reviewers, discard work, delete branches, or overwrite state of unknown provenance.

## Inputs and Recovery

Accept a non-empty ticket identifier, a raw text assignment, or an absolute path to an existing solve manifest. Before writing an artifact, read and follow [the shared artifact policy](../_shared/artifact-policy.md) and [the manifest schema](manifest-schema.md).

For continuation, locate the newest valid snapshot in the supplied run lineage, compare it with current environment evidence, and resume its recorded next action. A lineage conflict or stale unsafe identity returns a blocker rather than guessing.

## Workflow

1. Read applicable project instructions and discover the project and available capabilities through [environment discovery](environment-discovery.md). This step is complete when facts, inferences, and unavailable capabilities are distinguished.
2. Acquire the ticket description and acceptance evidence when an issue capability exists; otherwise preserve the literal input as the assignment. This step is complete when the objective and evidence surface are explicit.
3. Write the initial manifest snapshot. This step is complete when its absolute path and run identity are available for every handoff.
4. Inspect staged, unstaged, and relevant untracked state. When prior state exists, invoke `finishing-a-development-branch` in preservation mode and continue only when its outcome reports safe release. This step is complete when prior state is durably stored or an unsafe blocker is recorded.
5. Identify and synchronize the semantic base when supported, then provision or resume the task workspace using the environment rules. This step is complete when the workspace identity and provenance are recorded.
6. Apply [the routing rules](routing.md) and write the routing snapshot. This step is complete when every ambiguity signal and one selected pipeline are recorded.
7. For low ambiguity, invoke `writing-plans` and then `continuous-driven-development`. For high ambiguity, invoke `brainstorming`, then `writing-plans`, then `subagent-driven-development`. This step is complete when the selected executor returns current artifacts and evidence.
8. Apply the relevant independent review and `verification-before-completion` contracts. Verification failure returns to execution; a correctness blocker remains blocked. This step is complete only when requirements and current evidence support delivery.
9. Invoke `finishing-a-development-branch` in delivery mode with the completion decision and evidence paths. This step is complete when the outcome records commits, synchronization, review state, limitations, and release status.
10. Write the terminal manifest. When an active Goal lifecycle is available, mark it complete only at the gate in [the routing rules](routing.md). This step is complete when the terminal artifact and honest final status exist.

## Handoff Contract

Pass the latest manifest path, the authoritative assignment or approved design path, and the plan path when one exists. Require every solve-controlled skill to return `status`, `latest_manifest`, `artifact`, and `evidence_or_blocker`. Re-read those artifacts after context compaction or changed external state.

## Autonomy and Blockers

Keep questions inside the high-ambiguity `brainstorming` stage. Return unsafe identity, secret exposure, destructive-state risk, irreconcilable synchronization, or correctness failure as evidence-backed blockers. Treat unavailable optional publication as a recorded limitation. Never weaken verification, invent context, or silently change the selected route.

## References

- [Shared artifact policy](../_shared/artifact-policy.md)
- [Manifest schema](manifest-schema.md)
- [Environment discovery](environment-discovery.md)
- [Routing](routing.md)
