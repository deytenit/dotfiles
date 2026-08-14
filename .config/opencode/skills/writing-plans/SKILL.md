---
name: writing-plans
description: Use when an approved specification or requirements describe a multi-step implementation task
---

# Writing Plans

Create an implementation plan that a capable engineer can execute without hidden context or invented details.

## Input and Scope

- Start from an approved specification and retain its absolute path in the plan, or from a low-ambiguity solve manifest whose assignment is the authorized specification.
- Read applicable project instructions, the approved specification, and the relevant source before planning changes.
- If the specification contains independent subsystems that cannot form one coherent, testable delivery, split it into ordered plans instead of hiding the decomposition inside oversized tasks.

Before writing the plan, read ../_shared/artifact-policy.md and follow it. Reference the approved spec by absolute path when one exists. Save the plan artifact and self-review it. For direct invocation, then offer subagent-driven-development for independent tasks or continuous-driven-development for inline execution. Do not require workspace isolation, a branch operation, or a save-to-VCS step.

## Solve Handoff

When a solve handoff supplies a manifest, preserve its absolute path and shape the plan for its recorded route without offering a choice. A continuous plan uses one primary-agent sequence. A subagent plan defines bounded task ownership, role intent, dependencies, and review points. After self-review, return `status: done | blocked`, `latest_manifest: absolute path`, `artifact: absolute plan path`, and concise `evidence_or_blocker` to `solve`.

## File Responsibility Map

Before defining tasks, add an up-front map of every file to create, modify, or delete:

- Give each file its exact path and one clear responsibility.
- State the interfaces it consumes and produces, including exact names, parameters, return types, data shapes, and relevant error behavior.
- Keep related responsibilities together while preserving existing project boundaries and conventions.
- Record dependencies between files and use them to determine task order.

Do not proceed to task drafting until the map and interfaces are internally consistent.

## Task and Step Structure

Order tasks by dependency so each task relies only on artifacts and interfaces established earlier. Each task must identify:

- its exact file paths and relevant locations;
- its prerequisites and the later tasks that consume its outputs;
- its exact interfaces and expected behavior;
- an independently verifiable result.

Write execution steps as small Markdown checkboxes, with one concrete action per step. For every code change, include the explicit code the implementer must add or replace. Include complete test code, implementation code, configuration, and data shapes wherever those change; prose alone is not enough.

For verification steps, discover the commands from current project documentation, manifests, or declared capabilities. Record the exact scoped command and its expected result, including the expected RED failure and GREEN success when the plan uses test-first development. Never substitute a remembered ecosystem command for a project-declared command.

## No Placeholders

The final plan must contain no deferred decisions, incomplete sections, vague instructions, or references to undefined types, functions, methods, files, or tasks. Do not use “TBD,” “TODO,” “implement later,” “handle edge cases,” “write tests,” or “same as an earlier task” in place of executable detail.

If a required fact or verification command cannot be discovered, resolve it before finalizing the plan or report the plan as blocked. Do not invent the missing detail.

## Inline Self-Review

Before handing off the saved plan, review and fix it in place:

1. **Specification coverage:** Map every requirement and constraint to at least one task and remove scope that the specification did not approve.
2. **Placeholder scan:** Remove every deferred decision, vague instruction, incomplete section, and unexplained reference.
3. **Type and interface consistency:** Check that names, signatures, properties, error shapes, and file responsibilities agree across all tasks.
4. **Dependency order:** Confirm every prerequisite is produced before it is consumed and that each task ends in a verifiable state.
5. **Verification quality:** Confirm every relevant change has a discovered project-declared command and a concrete expected result.

For direct invocation, report the absolute plan artifact path, then offer the two execution choices named in the output contract. For a solve handoff, return the plan and manifest to `solve` without offering a choice.
