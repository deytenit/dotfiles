---
name: writing-skills
description: Use when creating or editing reusable skills or instruction files, or when evaluating whether instructions reliably change agent behavior
---

# Writing Skills

## Overview

Writing skills is test-driven development for reusable instructions. Define the
behavior, observe the failure without the instruction, add the smallest useful
guidance, and verify both the intended behavior and nearby behavior.

**Core principle:** If the baseline never showed the failure, the instruction
has not proved that it teaches the right thing.

**REQUIRED BACKGROUND:** Understand **test-driven-development** before using
this skill.

## What Belongs in a Skill

A skill captures a reusable technique, pattern, or reference that applies across
tasks. Put project-only conventions in the closest project instruction file.
Automate rules that can be checked mechanically; reserve instructions for
judgment, sequencing, and decisions.

Create or extend a skill when:

- the behavior is useful across multiple tasks;
- the correct approach is not reliably obvious;
- a distinct trigger should make the guidance discoverable; or
- agents repeatedly omit, misorder, or rationalize away an important action.

Do not create a skill for a one-off solution, a narrative of past work, or a
standard fact already documented at the point of use.

## Instruction Architecture

- Treat a skill description or an instruction-file pointer as a trigger: name the job and every genuinely distinct branch that should load it.
- Budget always-loaded text aggressively; put branch-specific reference behind a precise pointer.
- Separate ordered actions from reference material and keep definitions beside the rules that use them.
- Give every step a checkable completion criterion. Prefer a clear bound over motivational prose.
- Split a document when its branches force unrelated readers to load irrelevant instructions.

Apply progressive disclosure in three layers:

1. **Trigger metadata:** only enough information to decide whether to load the
   skill.
2. **Main instructions:** the shared workflow and routing decisions needed for
   every use.
3. **References:** branch-specific detail loaded only through an explicit,
   nearby pointer.

Keep references one level from the main file. A reader should never have to
follow a chain of references to discover a required rule.

## Design the Trigger

The frontmatter contains only:

~~~yaml
---
name: writing-skills
description: Use when creating or editing reusable skills or instruction files
---
~~~

For a new skill:

- use a lowercase, hyphenated, action-oriented name;
- start the description with “Use when...”;
- describe observable situations, symptoms, and distinct branches;
- use third-person trigger wording;
- keep process steps out of the description; and
- include terms a user or agent would naturally use for the problem.

The description is a routing contract, not a summary. If it describes the
workflow, an agent may act from the metadata without reading the instructions.

## Match the Form to the Failure

Classify the baseline failure before choosing the instruction form.

| Baseline behavior | Best instruction form | Completion criterion |
|---|---|---|
| A known rule is skipped under pressure | Bright-line rule plus counters for observed rationalizations | The pressure scenario follows the rule |
| Output has the wrong shape | Positive recipe that names the parts and their order | Every required part appears in order |
| A required element is omitted | A required field or slot beside the template | The field is present and populated |
| Behavior depends on context | Conditional keyed to an observable predicate | Each branch chooses the expected action |
| A technique is applied incorrectly | Worked example plus boundary conditions | A fresh application produces the expected result |
| Reference information cannot be found | Searchable headings, terms, and direct routing | A retrieval probe finds and applies the fact |

Do not use prohibitions to shape an output. State what the output is. Use
prohibitions only when the baseline shows a discipline failure and record the
specific workaround they close.

Match specificity to risk:

- use flexible guidance when several approaches are valid;
- use ordered steps when sequence matters;
- use an exact template or reusable tool only when variation is unsafe.

## Test Before Editing

When the user explicitly requests an instruction change, make that change first. Do not delay it for a baseline behavior test or RED. Review the revised wording and run proportionate checks afterward.

~~~text
FOR SELF-DIRECTED INSTRUCTION CHANGES, REQUIRE A FAILING BEHAVIOR TEST FIRST
~~~

For self-directed instruction changes, before editing instruction text:

1. Define one observable behavior and its pass/fail criterion.
2. Run a baseline without the skill or proposed instruction.
3. Record the exact failure, omission, or rationalization.
4. Add the smallest instruction that addresses that evidence.
5. Re-run the behavior test with the instruction.
6. Add realistic pressure and verify the behavior still holds.
7. Run a regression scenario for an adjacent branch or ordinary case.
8. Refactor wording only while every scenario remains green.

For the complete worker protocol, scenario templates, and evidence table, read
[testing-skills-with-subagents.md](testing-skills-with-subagents.md).

For discipline-enforcing language, read
[persuasion-principles.md](persuasion-principles.md) before adding emphatic
rules. Persuasion must serve the user's stated interests, not manufacture
urgency.

## Write the Smallest Skill

A useful main file normally contains:

~~~text
skill-name/
  SKILL.md
  branch-reference.md
~~~

Only add a reference when a branch has enough independent detail that readers
outside that branch should not pay its context cost. Only add a reusable tool
when deterministic execution is materially safer than prose.

Prefer:

- one strong example over several variants;
- tables for repeated mappings;
- numbered lists for ordered actions;
- definitions next to the rules that depend on them;
- concrete predicates and bounds;
- consistent terms throughout the bundle.

Remove:

- facts an agent can already infer;
- repeated explanations;
- client-specific tool names or fixed invocation syntax;
- vendor, model, shell, package-manager, or version-control assumptions;
- time-sensitive setup details;
- narrative history; and
- choices that do not change behavior.

## RED–GREEN–REFACTOR for Instructions

### RED: Observe the Missing Behavior

Run the smallest realistic scenario without the instruction. Confirm the
scenario executes, the intended failure is visible, and the failure is not
caused by missing context or an invalid setup.

### GREEN: Add Only What the Failure Requires

Write the minimum trigger, rule, recipe, example, or reference pointer that
addresses the observed failure. Re-run the same scenario with fresh context.

### REFACTOR: Close Evidence-Based Gaps

If pressure reveals a new rationalization, add a precise counter. If a normal
case regresses, narrow the trigger or conditional. Remove duplicated text and
re-run the full scenario set after each meaningful change.

Do not add hypothetical defenses that no test exposed. More instruction can
create more steering and more ambiguity.

## Quick Reference

| Need | Action | Done when |
|---|---|---|
| Discovery | Write trigger-only metadata with all distinct branches | Each intended request selects the skill |
| Progressive disclosure | Route branch detail through a direct pointer | Unrelated branches do not load it |
| Ordered behavior | Number actions and state a check for each | Every step has observable evidence |
| Discipline | Baseline, then pressure-test the smallest rule | The rule survives realistic pressure |
| Output shape | Give a positive ordered recipe | The output matches the recipe |
| Safety against overreach | Run an adjacent regression scenario | Ordinary behavior remains unchanged |
| Concision | Remove repetition and obvious background | Every retained section changes a decision |

## Common Mistakes

| Mistake | Correction |
|---|---|
| Self-directed writing before observing a baseline | Restore the old instruction and run RED first |
| Describing the workflow in metadata | Keep only trigger conditions in the description |
| Putting every branch in the main file | Move branch-only detail behind a precise pointer |
| Adding vague advice | Replace it with an observable predicate and completion check |
| Using “do not” language to shape output | State the required output parts in order |
| Testing only the happy path | Add pressure and adjacent regression scenarios |
| Assuming a fixed runtime capability | Describe worker outcomes and discover available roles |
| Expanding after a passing test | Stop at the smallest instruction justified by evidence |

## Completion Checklist

- [ ] Frontmatter has only **name** and **description**.
- [ ] The description names the job and every genuinely distinct trigger branch.
- [ ] The main file contains only shared workflow and routing.
- [ ] Branch-specific detail is behind a direct pointer.
- [ ] Ordered actions and reference material are separate.
- [ ] Every required step has a checkable completion criterion.
- [ ] For self-directed changes, a baseline without the instruction exposed the intended failure.
- [ ] The smallest revised instruction passed the original scenario.
- [ ] A realistic pressure scenario passed.
- [ ] An adjacent regression scenario passed.
- [ ] The bundle contains no fixed client, vendor, command, or repository assumptions.
- [ ] Every changed file was re-read and the relevant structural checks are green.

## Final Rule

~~~text
No observed failure -> no justified self-directed instruction change.
No pressure and regression evidence -> behavior is not verified.
~~~
