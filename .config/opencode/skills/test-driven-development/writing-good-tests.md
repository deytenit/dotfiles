# Writing Good Tests

**Read this reference when:** writing or changing tests, adding test doubles, or adding helpers used only by tests.

## Core Principles

```
1. Every test names the break it catches.
2. Every test exercises real observable behavior.
```

Strict test-first development supports both: the test proves it can fail before implementation exists, and a test double is introduced only at a boundary that genuinely needs isolation.

## Name the Break

Before writing a test body, answer: **What production change would make this test fail, and would that change be a defect rather than an intentional redesign?**

A useful test catches a wrong branch, missing side effect, invalid argument, boundary error, or broken contract. If no realistic defect can make it fail, redesign the test around an observable behavior.

### Derive Expectations Independently

Expected values must not reuse the code under test, its builders, or its decision logic. Use hand-checked literals or fixtures whose expected outcome was derived independently.

Pseudocode:

```
bad:  expected = production_builder(input)
      assert production_builder(input) equals expected

good: assert production_builder(input) equals hand_checked_literal
```

A shared mistake on both sides of an assertion creates a tautology.

### Test Behavior, Not Text

Do not treat exact source wording, private structure, or a constant's raw value as the behavior. Exercise the artifact with controlled input and assert observable output, side effects, or status. Instructional documents are pressure-tested through the behavior of their consumer, not by asserting that a sentence exists.

Test your boundary contract, not mechanics owned by a dependency. Trivial forwarding earns a test only when it validates, normalizes, defaults, derives, enforces, or causes a consumer-visible effect.

## Exercise the Real Thing

### Real Behavior, Not Test-Double Behavior

An assertion that merely proves a test double is present says nothing about the real component. Assert the production behavior. If the double itself is the subject of the assertion, use the real dependency or remove that assertion.

### Choose the Correct Boundary

Before replacing a dependency:

1. Identify the real operation's side effects.
2. Keep every side effect the test depends on real.
3. Isolate only the slow, external, nondeterministic, or destructive boundary below them.
4. When uncertain, observe the real path first and then introduce the smallest suitable double.

When arguments, call counts, or ordering are part of your code's contract, make the double specific enough that the wrong branch cannot satisfy the test.

### Use Complete Realistic Data

Test data must mirror the complete documented structure that downstream code may consume, not only the fields used by the immediate assertion. Partial data hides structural assumptions and can let a unit test pass while integration fails.

Give success, error, malformed, and boundary cases distinct fixtures when they represent distinct behavior.

### Keep Test-Only Methods Out of Production

Production types expose production behavior only. Cleanup, setup, or inspection needed solely by tests belongs in test utilities. Before adding a method, ask whether production calls it and whether the type owns that resource's lifecycle. If either answer is no, do not add the method to the production interface.

Prefer real components when test-double setup becomes larger than the behavior being tested or cannot faithfully reproduce the real interface.

## Gate Before Writing a Test

```
Name the realistic defect this test catches.
Confirm the expected value is independently derived.
Identify the consumer-visible behavior being asserted.
List real dependency side effects before isolating a boundary.
Use complete realistic data for every test double.
Keep test-only support outside production interfaces.
```

## The Mutation Check

Before finishing, mentally mutate the production behavior. At least one test should fail for each realistic mutation:

- Wrong value or argument.
- Wrong branch or handler.
- Missing state change or side effect.
- Empty or default result.
- Missing validation for empty, absent, unauthorized, malformed, or boundary input.

If no test catches a realistic mutation, the behavior is unprotected or the test is tautological.

## Warning Signs

- The same helper computes setup and expected output.
- The test can fail only through a crash or missing selector.
- Intentional source wording changes fail the test, but behavioral defects do not.
- An assertion checks the presence of a test double.
- Test data omits documented fields.
- A method is called only from tests.
- Test-double setup dominates the test or its boundary cannot be explained.
- The test exists only for coverage and asserts no outcome.
