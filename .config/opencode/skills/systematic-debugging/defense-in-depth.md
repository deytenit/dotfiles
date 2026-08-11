---
name: defense-in-depth
description: Use after tracing invalid data or a dangerous side effect through multiple system layers where one check could be bypassed
---

# Defense-in-Depth Validation

## Overview

A root-cause fix removes the original trigger. Independent validation at meaningful boundaries prevents another path from recreating the same dangerous outcome and leaves evidence if a guard is reached.

**Core principle:** Validate the same invariant at each layer that owns enough context to enforce it, with each layer protecting against a different failure mode.

Do not use extra guards as a substitute for root-cause investigation. Apply this technique after the source is understood.

## Map the Data Flow

List every boundary crossed by the invalid value or dangerous action:

```
external input
    -> domain operation
    -> environment-sensitive boundary
    -> irreversible or costly side effect
```

For each boundary, record the invariant it can verify and the failure it can prevent.

## Four Complementary Layers

### 1. Entry Validation

Reject malformed, absent, unauthorized, or out-of-range input at the public boundary. Return an error that identifies the invalid contract.

### 2. Domain Invariants

Validate that the value is meaningful for the operation before state changes. This catches internal callers that bypass the public boundary or combine individually valid values into an invalid state.

### 3. Environment and Side-Effect Guards

Immediately before a destructive, external, or environment-sensitive operation, confirm that the resolved target and current context are safe. Refuse the action when the invariant cannot be proven.

### 4. Diagnostic Evidence

Record the target, relevant state, and caller context before the risky operation so a guard failure or unexpected outcome can be traced. Do not expose secrets or unrelated user data.

## Capability-Neutral Example

```
function process(requested_target):
    require requested_target is present              # entry

    resolved_target = resolve(requested_target)
    require resolved_target belongs to this request  # domain

    require current_context permits resolved_target  # environment
    record safe diagnostic context                    # evidence

    perform side_effect(resolved_target)
```

Each check is independent: a caller that bypasses entry validation still meets the domain and environment guards.

## Verification

Test each layer separately with the smallest project-declared check that exercises it:

- Invalid external input is rejected at entry.
- An internal path that bypasses entry is rejected by the domain invariant.
- A valid value in an unsafe context is rejected at the side-effect boundary.
- Diagnostic evidence is useful and does not reveal sensitive data.

## Red Flags

- One validation point is expected to protect every path.
- The same helper and assumptions implement every guard, so one defect bypasses all layers.
- A guard silently changes invalid input instead of rejecting it.
- Logging is treated as prevention.
- Extra checks are added before tracing the root cause.

The goal is independent protection, not duplicated conditionals.
