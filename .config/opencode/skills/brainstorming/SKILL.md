---
name: brainstorming
description: Use when the user explicitly requests design exploration or a solve handoff identifies material ambiguity that requires human decisions before implementation
---

# Brainstorming Ideas Into Designs

Turn an idea into an approved, durable design before implementation begins.

Run this workflow only when the user explicitly requests it directly or when a high-ambiguity solve handoff identifies material decisions that require human approval. Once active, it may transition to `writing-plans` through the workflow below.

<HARD-GATE>
Do not write code, scaffold files, or take any other implementation action until the exact written design artifact has been reviewed and approved. Perceived simplicity is not an exception; a simple design may be brief, but the gate still applies.
</HARD-GATE>

## Solve Handoff

Read the latest manifest supplied by a high-ambiguity solve handoff before design work. Interactive clarification and artifact approvals remain mandatory. After the user approves the exact design artifact, return `status: done | blocked`, `latest_manifest: absolute path`, `artifact: absolute design path`, and concise `evidence_or_blocker` to `solve`; do not independently select an execution route or finalize branch state.

## Delegation Boundary

Read and follow [the agent workflow contract](../_shared/agent-workflow.md).
The main session leads the interactive exploration: scoping, one question at a
time, comparing approaches, developing the design with the user, and approvals.
Workers handle bounded source exploration, feasibility analysis, and proposed
wording for the section currently being discussed. Their compact findings inform
that dialogue; the main session evaluates and discusses them with the user.

Use [design-worker.md](design-worker.md) for support tasks. Assign recording of
the complete durable design only after every section is approved. The recorder
captures agreed content and returns unresolved details instead of deciding them.
Delegation changes who performs detailed work; the workflow and gates below stay
the same.

## Workflow

1. **Discover context.** Read the applicable project instructions and documentation needed for coordination. Delegate detailed inspection of the relevant structure, files, constraints, and established patterns to a bounded researcher; retain its concise findings and evidence paths.
2. **Check scope.** Identify independent subsystems before detailed clarification. If the request is too broad for one coherent design, help the user decompose it, explain relationships and dependency order, and choose one scoped part for this design cycle.
3. **Clarify one question at a time.** Understand purpose, constraints, success criteria, and boundaries. Ask only one question per message; prefer a concise set of choices when that makes the decision easier.
4. **Compare approaches.** Present two or three viable approaches with tradeoffs. Lead with the recommended approach and explain why it best fits the discovered context.
5. **Present the design in sections.** Scale each section to its complexity and ask for approval after each section. Cover the relevant architecture, responsibilities, interfaces, data flow, error handling, and verification strategy. Revise any section that is not approved.
6. **Write the approved design.** Only after every section is approved, give a document worker the approved content and a fresh artifact path. Have it record the durable design under the shared artifact policy, then self-review it against the agreed sections. The main session checks that the recorded design matches those decisions.
7. **Obtain artifact approval.** Ask the user to review the exact artifact that was written. Apply requested changes, repeat the self-review, and ask again. Do not begin implementation while review is pending.
8. **Transition to planning.** After the artifact is approved, use `writing-plans`. Do not transition directly to an implementation workflow or any other implementation skill.

## Design Quality

- Give each unit one clear responsibility and define how it is used, what it exposes, and what it depends on.
- Prefer boundaries that allow a unit to be understood and tested independently.
- Follow existing project patterns and include only targeted structural improvements needed for the requested outcome.
- Remove unrequested features and unrelated refactoring.
- Return to clarification whenever the design exposes an unresolved decision.

## Output Contract

Before writing the approved design, read ../_shared/artifact-policy.md and follow it. Write the design there, self-review it for omissions, contradictions, ambiguity, and scope, then ask the user to review that exact artifact. Do not start implementation before approval.

The self-review must also remove placeholders and incomplete requirements. Report the absolute artifact path so the user can review the precise document being approved.
