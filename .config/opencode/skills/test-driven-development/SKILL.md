---
name: test-driven-development
description: Use when implementing any feature or bugfix, before writing implementation code
---

# Test-Driven Development

## Overview

Write the test first. Watch it fail for the expected reason. Write the smallest implementation that makes it pass.

**Core principle:** If you did not observe the test fail, you do not know whether it can detect the missing or broken behavior.

**Violating the letter of the rules is violating the spirit of the rules.**

## When to Use

Use for new behavior, bug fixes, refactoring, and behavior changes.

When the user explicitly requests a change, implement it first without requiring a reproduction or failing test. Add proportionate tests afterward and run the relevant checks; do not block the requested change on RED.

Other exceptions require explicit agreement from the user: disposable experiments, generated output, or declarative configuration that has no executable behavior.

## The Iron Law

```
NO PRODUCTION IMPLEMENTATION WITHOUT A FAILING TEST FIRST, EXCEPT FOR AN EXPLICIT USER CHANGE REQUEST
```

Outside that exception, implementation written first must be removed and recreated from the test. Do not keep it as a reference, adapt it while writing the test, or treat tests written afterward as equivalent.

## Red-Green-Refactor

### RED: Describe One Missing Behavior

Write one minimal test whose name describes the behavior and the break it prevents. Exercise real production behavior; isolate a dependency only when its real boundary is unsuitable for the test.

Before writing the body, identify the production change that would make the test fail. Derive expected values independently of the code under test.

Read [writing-good-tests.md](writing-good-tests.md) whenever writing or changing a test, adding a test double, or adding test support code.

### Verify RED: Observe the Right Failure

Run the smallest project-declared check that exercises the behavior.

Confirm all three:

- The test fails rather than failing to execute.
- The observed failure is the one the test was designed to expose.
- The failure comes from the missing behavior, not a typo, invalid fixture, or environment mistake.

If the test passes immediately, it does not demonstrate the missing behavior. If it cannot execute, correct the test setup and repeat RED until the failure is meaningful.

### GREEN: Implement the Minimum

Write only enough production code to satisfy the failing test. Do not add speculative options, adjacent improvements, or unrelated refactoring.

### Verify GREEN: Observe the Pass

Run the smallest project-declared check that exercises the behavior.

Inspect the current output. The new test must pass, related checks must remain healthy, and unexpected errors or warnings must be investigated rather than ignored.

If the test still fails, correct the implementation, not the established behavioral expectation.

### REFACTOR: Improve Structure While Green

Only after GREEN:

- Remove duplication.
- Improve names and boundaries.
- Extract helpers that clarify intent.

Do not add behavior during refactoring. Re-run the smallest project-declared check that exercises the behavior after each meaningful change.

### Repeat

Start the next behavior with a new failing test.

## Why the Order Matters

Tests written after implementation pass immediately and are biased toward what was built. They may encode the implementation, omit forgotten edge cases, or prove only that the test double behaves as configured. Test-first establishes the desired behavior before the solution can influence the expectation.

Manual exploration can be useful, but it is not a repeatable regression test. Throw away exploratory implementation and restart from RED.

## Common Rationalizations

| Excuse | Reality |
|---|---|
| "The change is too small to test." | Small behavior can regress; a focused test states its contract. |
| "I will add tests afterward." | A test that never demonstrated failure has not proved it can catch the break. |
| "Manual checking is faster." | It is not repeatable and leaves no regression protection. |
| "Deleting earlier work wastes time." | Keeping unproven implementation preserves uncertainty. |
| "I need the implementation as a reference." | That turns test-first into tests-after. |
| "The existing area has no tests." | Add the first focused test around the behavior you change. |
| "Testing is hard here." | Treat that as design feedback and simplify the boundary. |

## Red Flags: Stop and Start Over

- Production implementation exists before its test.
- The new test passes on the pre-change behavior.
- You cannot explain the RED failure.
- The test asserts source wording or a test double instead of behavior.
- Expected data is computed by the code under test.
- A production method exists only to support tests.
- You are calling tests-after "equivalent" or "pragmatic."

Outside the explicit-request exception, any of these means return to RED. Remove implementation that preceded the test and begin again.

## Before Finishing

- Every changed behavior has a focused test when warranted. Outside the explicit-request exception, it failed first for the expected reason.
- The implementation is limited to the requested behavior and any relevant test expectations.
- Tests exercise real behavior and use independently derived expectations.
- The mutation check in [writing-good-tests.md](writing-good-tests.md) identifies a test that fails for each realistic regression.
- Fresh output from the relevant project-declared checks supports any completion claim.

## Final Rule

```
Self-directed production behavior -> test existed and failed first
Explicit user change request -> implement first, then verify and add proportionate tests
```
