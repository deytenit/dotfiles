# Routing Rules

## Evidence Before Routing

Perform bounded codebase discovery before selecting a pipeline. Treat questions answerable from project instructions, source, tests, manifests, or available ticket evidence as research, not human ambiguity. Size or file count alone is not ambiguity.

High ambiguity exists only when an unresolved decision could materially change requested scope or acceptance criteria, system boundaries or architecture, public interfaces or compatibility, persistent data shape or migration behavior, or security, privacy, authorization, or destructive behavior. Record each signal and its supporting evidence.

## Select and Preserve a Pipeline

For low ambiguity, select `writing-plans` followed by `continuous-driven-development`; the normalized assignment and manifest are the authorized specification. For high ambiguity, select `brainstorming`, then `writing-plans`, then `subagent-driven-development`; `brainstorming` resolves material decisions and supplies the approved design.

Record one selected pipeline in the routing manifest snapshot. Keep it immutable unless new evidence invalidates its recorded predicate. A correction requires a successor snapshot that names the invalidated evidence, replacement evidence, and replacement route; do not drift informally between routes.

## Goal Completion Gate

Mark an active Goal complete only when every requirement is satisfied, relevant fresh verification passes, intended changes are committed when usable commit capability exists or their local state is explicitly recorded when it does not, finishing has produced its outcome with optional publication either completed or recorded unavailable, and a terminal manifest exists. A correctness blocker leaves the Goal incomplete or blocked according to the host lifecycle contract.
