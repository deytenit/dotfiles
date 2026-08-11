# Condition-Based Waiting

## Overview

Flaky checks often guess how long asynchronous work needs. A fixed delay can be too short under load and unnecessarily slow when the condition is already satisfied.

**Core principle:** Wait for the observable condition that matters, not an assumed duration.

## When to Use

Use condition-based waiting when a check:

- Passes or fails depending on execution speed.
- Waits for state, an event, output, a resource, or a count to become observable.
- Uses a delay that is unrelated to behavior being verified.

A fixed duration is appropriate only when elapsed time is itself the behavior, such as a rate limit or debounce interval. Document why that duration is part of the contract.

## Core Pattern

```
bad:
    wait guessed_duration
    assert observable_condition

good:
    wait_until observable_condition
    assert resulting_behavior
```

Use the waiting primitive already declared by the project when one exists. Otherwise implement the smallest local helper supported by the project.

## A Safe Wait-Until Contract

```
wait_until(read_condition, description, deadline):
    loop:
        current = read_condition()   # read fresh state every time
        if current satisfies condition:
            return current
        if deadline reached:
            fail with description and last observed state
        yield according to project-supported scheduling
```

The helper must:

- Re-read current state rather than cache stale data.
- Stop at a bounded deadline.
- Report the condition and last observed state on failure.
- Avoid excessive polling.
- Return the observed value when that prevents a second race-prone read.

## Common Scenarios

| Need | Condition to observe |
|---|---|
| Completion event | Matching event is present |
| State transition | Current state equals the required state |
| Accumulated results | Observed count reaches the required count |
| Resource readiness | Resource exists and is usable |
| Compound readiness | Every required predicate is true |

## Common Mistakes

- **Polling too frequently:** wastes resources and can distort the system under test.
- **No deadline:** a missing condition hangs forever.
- **Stale reads:** the loop never sees progress.
- **Waiting for a proxy:** observe the behavior the assertion actually depends on.
- **Swallowing transient errors blindly:** distinguish "not ready" from a real failure.

## When Elapsed Time Is the Behavior

First wait for the triggering condition so measurement begins at a known state. Then wait or measure only the documented interval required by the behavior. Keep tolerance and clock behavior consistent with project conventions.

Condition-based waiting removes timing guesses; it does not remove bounded failure or behavioral assertions.
