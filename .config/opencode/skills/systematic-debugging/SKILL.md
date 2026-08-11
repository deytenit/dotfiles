---
name: systematic-debugging
description: Use when encountering any bug, test failure, or unexpected behavior, before proposing fixes
---

# Systematic Debugging

## Overview

**Core principle:** Find the root cause before implementing a fix. A change at the visible symptom is not a solution unless evidence shows the symptom is the source.

**Violating the letter of this process is violating the spirit of debugging.**

## The Iron Law

```
NO FIX WITHOUT ROOT-CAUSE EVIDENCE FIRST
```

Complete each phase in order. Use only capabilities discovered from the current environment and applicable project instructions; do not substitute remembered tools or commands.

## Phase 1: Reproduce and Gather Root-Cause Evidence

Before proposing a fix:

1. **Read the failure completely.** Record exact messages, locations, status values, and warnings.
2. **Reproduce consistently.** Identify the smallest project-declared check or controlled action that shows the problem. If it is intermittent, gather more observations rather than guessing.
3. **Establish the boundary of the failure.** Determine what is healthy, what first becomes incorrect, and what differs between successful and failing runs.
4. **Inspect relevant changes and context.** Use the project's discovered inspection capabilities to identify nearby behavioral, dependency, configuration, or environment changes.
5. **Trace bad data backward.** Follow the value, state, or side effect through its callers until reaching the original trigger. See [root-cause-tracing.md](root-cause-tracing.md).

For a multi-component path, collect evidence at each boundary:

```
for each boundary from input to failure:
    record incoming data and relevant state
    record outgoing data and resulting state
    compare successful and failing observations
locate the first boundary where they diverge
```

Phase 1 is complete when you have a reliable reproduction, an observed failure boundary, and an evidence-backed candidate causal chain that is specific enough to test.

## Phase 2: Compare Patterns and References

Before designing the fix:

1. Locate the closest working example in the same project.
2. Read the applicable reference or declared convention completely.
3. Compare the working and failing paths line by line or behavior by behavior.
4. List every relevant difference without dismissing small ones.
5. Identify assumptions about inputs, lifecycle, ordering, configuration, and environment.

Phase 2 is complete when the difference that explains the evidence is explicit.

## Phase 3: State and Minimally Test One Hypothesis

Write one explicit hypothesis:

```
I think <cause> produces <failure> because <evidence>.
If that is true, changing or observing <one variable> will produce <predicted result>.
```

Test only that variable using the smallest project-declared capability that can confirm or refute the prediction. Do not bundle fixes or adjust several conditions at once.

- If confirmed, proceed to Phase 4.
- If refuted, remove the experimental change, record what was learned, and form a new single hypothesis.
- If the result is ambiguous, improve the evidence instead of stacking another change on top.
- If you do not understand part of the path, say so and research or ask for the missing information.

Phase 3 is complete only when a minimally tested hypothesis confirms the root-cause explanation. A refuted or ambiguous hypothesis stays in Phase 3 until a new single hypothesis is tested.

## Phase 4: Fix the Root Cause and Prevent Regression

1. **Create regression protection first.** Add the smallest failing test or controlled reproduction for the confirmed root cause. Follow the test-driven-development skill when production behavior changes.
2. **Implement one root-cause fix.** Avoid adjacent improvements and unrelated restructuring.
3. **Add proportionate prevention.** When invalid data or a dangerous side effect crossed several boundaries, apply the layered validation in [defense-in-depth.md](defense-in-depth.md).
4. **Replace timing guesses.** When the cause is asynchronous ordering, use the technique in [condition-based-waiting.md](condition-based-waiting.md).
5. **Verify with current evidence.** Run the relevant project-declared checks, inspect their full current output, and confirm both the original symptom and the regression case.

If the fix fails, stop and return to Phase 1 with the new evidence. Do not add a second speculative fix. After three failed fix attempts, pause and discuss whether the underlying design or assumptions are wrong before trying again.

## Red Flags

Stop and return to the current phase if you are thinking:

- "Apply a quick patch and investigate later."
- "It is probably this; I will change it and see."
- "Several related changes will save time."
- "The failure looks obvious, so reproduction is unnecessary."
- "The reference is long; I know the pattern already."
- "The first hypothesis failed, but another change on top may help."
- "The test is flaky, so a longer delay is enough."

## Quick Reference

| Phase | Evidence required before continuing |
|---|---|
| 1. Reproduce and root cause | Reliable reproduction, observed failure boundary, and a candidate causal chain to test |
| 2. Pattern comparison | Relevant differences from a working example and complete reference |
| 3. One hypothesis | A minimally tested hypothesis that confirms the root-cause explanation |
| 4. Root-cause implementation | Regression protection plus fresh output from relevant project-declared checks |

## Supporting Techniques

- [root-cause-tracing.md](root-cause-tracing.md): trace an incorrect value or side effect backward to its original trigger.
- [defense-in-depth.md](defense-in-depth.md): validate independently at each meaningful layer after the root cause is known.
- [condition-based-waiting.md](condition-based-waiting.md): replace timing guesses with observation of the required condition.
