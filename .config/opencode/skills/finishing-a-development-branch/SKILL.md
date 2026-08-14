---
name: finishing-a-development-branch
description: Use when current branch state must be stored autonomously through semantic commits, safe synchronization, and a draft unassigned review request, either for preservation or delivery
---

# Finishing a Development Branch

Store the current branch state autonomously so the workspace can be released for subsequent work.

## Boundary

Explicit invocation authorizes state inspection, semantic commits, safe branch synchronization, and draft unassigned review publication. This skill does not run tests, builds, linters, project commands, implementation checks, requirements review, or judge correctness.

Never merge, assign reviewers, discard work, delete branches, rewrite unrelated history, or destructively clean a workspace. Completion means branch state is durably stored; it does not mean the software is correct.

Before writing an outcome, read and follow [the shared artifact policy](../_shared/artifact-policy.md).

## Modes

- **Preservation:** store unknown or incomplete state without a correctness claim. Direct invocation uses this mode unless the caller explicitly supplies a delivery decision and verification evidence.
- **Delivery:** accept a completion decision and fresh verification evidence from `solve` or the caller. Record that evidence without rerunning or evaluating it.

## Workflow

1. Read applicable instructions, the optional solve manifest, requested mode, and supplied evidence. Complete this step when mode and factual context are explicit.
2. Discover state-management, remote, and review capabilities without running project checks. Map branch, commit, remote, detached-state, and pending-change roles to the capability's native model; record each unsupported role with its reason. Complete this step when every required role is mapped or unavailable.
3. Through that mapping, identify the semantic base, current line or detached workspace, stored revisions, and intended pending changes. Complete this step when included state and unavailable inspection gaps are enumerated.
4. When preservation starts on the semantic base or detached state with pending changes, create a factual collision-safe preservation branch. Complete this step when the state has a named recoverable identity.
5. Use discovered inspection capabilities to apply ignore rules and inspect pending content for credentials, private keys, and tokens. Unsafe content blocks revision storage and publication with path evidence. If ignore or content inspection is unavailable, record an unsafe blocker rather than assuming the pending state is safe.
6. Through the native revision-capture mechanism, select every intended non-ignored change and split changes only into coherent semantic units. Prove the mechanism targets the preservation or task line and captures the complete intended set. Complete this step when no intended file is omitted or an unsafe capture gap is recorded.
7. Follow declared commit conventions or use a concise semantic subject. Prefix the exact ticket identifier when known. Make preservation subjects explicitly describe preserved work. Create no empty commit and do not rewrite existing commits without need.
8. When the mapped commit capability exists, store every intended change on the proven target line and require no intended pending state before reporting safe release. Safe release depends on durable state only; do not require project verification or optional remote/review publication. Without commit capability, record exact local state and report unsafe release.
9. Publish a new task line when supported. Before synchronizing divergent state, prove the direction, target peer, task lineage, and peer revision, then use the capability's native expected-state protection. On stale-state rejection, re-inspect and repeat the proof or record synchronization unavailable. Never overwrite unknown provenance.
10. Reuse an active review request or create a draft unassigned request using discovered templates and conventions. When draft state is unavailable, create an unassigned non-draft request only when authoritative platform semantics prove it is non-notifying. Otherwise record review publication as unavailable.
11. Write a `Branch Finalization Outcome v1` artifact and return its absolute path. Complete this step when durability, limitations, and release status are explicit.

## Capability Gaps

A local semantic commit is sufficient for safe release when optional remote or review publication is unavailable. Authentication or publication failure is a limitation when local durability remains intact. No usable commit capability leaves release unsafe. Never simulate unavailable operations.

## Outcome Contract

Write these sections in order: `## Context`, `## Included state`, `## Commits`, `## Synchronization`, `## Review request`, `## Limitations`, and `## Release status`. In delivery mode, include every supplied evidence path and state `not evaluated by finishing`. Use `safe` only when all intended state is durably stored and no intended uncommitted change remains; otherwise write `unsafe:` followed by the factual reason.
