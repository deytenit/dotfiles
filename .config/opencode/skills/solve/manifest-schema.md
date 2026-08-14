# Solve Run Manifest v1

Write every snapshot as Markdown with this exact heading and these sections in this order:

```text
# Solve Run Manifest v1

## Identity
- Run ID
- Created at
- Stage
- Predecessor
- Solve authorization

## Assignment
- Original input
- Input kind
- Canonical ticket
- Normalized objective
- Requirements sources
- Acceptance criteria
- Verification surfaces

## Environment
- Project root
- Instruction paths
- State-management capability
- Issue capability
- Remote capability
- Review capability
- Semantic base
- Base evidence
- Task workspace
- Workspace provenance
- Branch-name derivation
- Remote expected tip

## Routing
- Ambiguity signals
- Selected pipeline
- Routing evidence

## Artifacts
- Design
- Plan
- Execution evidence
- Review evidence
- Finishing outcome

## Delivery
- Mode
- Commits
- Synchronization
- Review request
- Limitations

## Continuation
- Next action
- Goal completion eligible
- Terminal result
```

## Snapshot Rules

Write snapshots through the shared artifact policy. Use one stable Run ID for a lineage. Every successor repeats the complete current state, names exactly one predecessor by absolute path, and never overwrites a predecessor. Use `unavailable:` followed by the factual reason for an unknown optional value; do not omit it.

Use these lifecycle stages: `intake`, `preserved`, `provisioned`, `routed`, `designed`, `planned`, `executed`, `reviewed`, `finalized`, and `blocked`. Terminal states are `complete`, `locally-complete`, and `blocked`.

Treat multiple successors that name one predecessor as a lineage conflict. Reconcile it from current environment evidence and write the resolved successor; if safe identity cannot be established, record a blocked snapshot.

## Handoff Paths

Carry the latest manifest snapshot and, when available, the authoritative assignment or approved design and current plan as absolute paths. Every solve-controlled return includes the current manifest path, its artifact path, and concise evidence or blocker.
