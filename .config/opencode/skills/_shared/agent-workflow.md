# Agent Workflow Contract

Use this contract across design, planning, and execution. The main session is
the controller and accumulator: it owns user dialogue, authorization, accepted
decisions, task ordering, integration, and the current recovery record. Workers
perform the detailed investigation, drafting, implementation, and review assigned
by the owning skill. That skill keeps its original sequence, interaction,
approvals, reviews, retry limits and completion rules. This contract changes
workload placement and context transfer, not those rules.

Brainstorming remains interactive in the main session. Workers support the
current question or section; the user and main session develop the design
together. The owning skill determines when recording a complete artifact begins.

## Dispatch and Context

1. Discover available delegation and file capabilities. Use fresh worker context
   with the smallest task brief; disable inherited conversation when supported.
   Otherwise supply a bounded brief and treat context isolation as unavailable.
2. Assign one outcome, applicable instruction paths, exact input paths and
   relevant sections, constraints, allowed writes, and required evidence. Give
   workers only the decisions and interfaces their task consumes. Include the
   applicable worker contract, artifact policy and compact-return format in
   each brief; fresh workers cannot rely on instructions loaded by the parent.
3. Use a read-only researcher for discovery, a document worker with permission
   to write only named artifacts for drafting, an implementer for approved code
   changes, and an independent read-only checker for review. Use equivalent
   available roles; a role name never grants a missing capability. Workers do
   not delegate. Read-only workers return concise evidence for the controller
   to persist; do not ask them to write reports.
4. Run dependent work sequentially. Parallel work requires independent inputs
   and disjoint writable ownership. Tell each writer it shares the workspace,
   must preserve others' edits, and must report conflicting external changes.
5. Require the return below. Inspect cited evidence only as needed to resolve a
   decision, finding, conflict, or verification gap. Perform the reviews required
   by the owning skill; delegate their detailed inspection where useful. Retain
   author self-review where that is the original requirement. A worker status
   alone is not proof of completion.

If delegation is unavailable, report the context limitation and continue the
original workflow inline when its capabilities and authorization allow it; this
does not add a new permission or blocker gate. Honor explicit user instructions
about delegation. Small coordination work may stay in the main session; a heavy
tightly coupled sequence can stay with one worker.

## Compact Return

Keep the worker's final message within 200 words, excluding artifact paths:

- Status: done, needs-context, or blocked; executors may use their existing statuses.
- Artifact: absolute path and the exact section needed for coordination, or none.
- Summary: at most five decision-relevant findings, with evidence references.
- Verification: checks actually run and their results, or not run with reason.
- Open issue: the missing fact, decision, or capability and its consequence, or none.

Put detailed reasoning, source excerpts, code, logs, and full plans in named
artifacts under the shared artifact policy. A controller persists a read-only
worker's bounded result when needed. Resolve a missing report by requesting a
compact corrected return, rather than ingesting a transcript.

## Accumulator and Recovery

Maintain compact recovery state using the owning skill's progress artifacts or
manifest. Include the objective and authorization, accepted decisions and exact
approved artifact versions, task status and ownership, evidence paths, blockers
and next action. Write a separate snapshot when needed for reliable recovery;
retain the owning skill's existing persistence and completion requirements.
For solve runs, the manifest's Controller state field may reference that snapshot.
Only the controller advances manifest lineage; workers return their input
manifest path alongside results.

A new run needs no pre-existing recovery record. An existing approved plan stays
valid without a coordination index. The assigned worker can extract a compact
task summary during its normal preflight without changing the approved plan or
adding a separate approval stage. New plans may start with an index of task IDs,
dependencies, ownership, expected results and detail anchors so the controller
can coordinate without loading implementation detail.

Keep the ongoing dialogue, accepted decisions and compact coordination state in
the main session; detailed research, code and logs stay with workers and their
artifacts. After compaction, restore from the latest existing progress or manifest
record and inspect only artifacts needed for the next action. Findings remain
proposals until accepted; workers cannot approve designs,
change scope, authorize publication, or advance approval gates.
