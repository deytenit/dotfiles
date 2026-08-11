# Testing Skills With Workers

**Load this reference when:** creating or editing a skill or instruction file
and evaluating whether it changes behavior under realistic pressure.

## Purpose

Skill tests are behavior tests:

- **RED:** observe what happens without the instruction;
- **GREEN:** add the smallest revised instruction and repeat;
- **REFACTOR:** close an observed loophole while retaining prior behavior.

The test subject must act on a realistic task, not recite the documentation.
Use fresh context for each run so prior variants do not steer later results.

## Worker Selection

When configured roles are present:

- use **researcher** workers for read-only baseline and scenario probes;
- use **checker** workers to evaluate results against the rubric.

Otherwise use equivalent available workers with the same read-only and
evaluation responsibilities. Workers do not spawn agents.

Do not prescribe a client-specific worker API. State the role, inputs,
constraints, and required output; use the environment's declared capability to
run it.

## The Four Required Cases

Every changed instruction needs these cases.

| Case | Instruction visible? | Purpose | Pass criterion |
|---|---|---|---|
| Baseline | No | Demonstrate the natural failure | The target failure appears for the expected reason |
| Smallest revision | Only the minimum proposed instruction | Prove that wording changes the target behavior | The original scenario passes without unrelated steering |
| Pressure | Full proposed instruction | Test resistance to realistic incentives to ignore or distort it | The required behavior holds and the response cites the controlling rule |
| Regression | Full proposed instruction | Protect an adjacent branch or ordinary case | The unaffected behavior remains correct |

If the baseline passes, stop. The scenario does not justify new instruction.
Change the scenario only when it failed to exercise the intended condition, not
to manufacture a failure.

## 1. Define the Behavior

Before any edit, record:

- the trigger;
- one observable target behavior;
- the expected failure without guidance;
- the exact pass/fail rubric;
- an adjacent behavior that must remain unchanged.

Keep each case focused on one behavioral claim. A single case may include
several pressures, but it should still have one verdict.

## 2. Run the Baseline

Give a read-only probe realistic task context while withholding the skill and
all excerpts from it. Ask it to choose and act. Capture:

- the action selected;
- omitted or misordered steps;
- exact rationalizations;
- uncertainty or requests for an easy escape;
- the pressure, if any, that caused the failure.

RED is valid only when the scenario ran successfully and the observed failure is
the behavior the instruction is meant to change.

## 3. Test the Smallest Revised Instruction

Provide the same task in fresh context with only the minimum proposed wording.
Do not include explanations, examples, or counters that the baseline did not
justify.

GREEN is valid when:

- the target behavior changes as expected;
- the worker can identify the rule that controlled its choice;
- no unrelated behavior changes; and
- the result meets the prewritten rubric.

If it still fails, revise one wording variable at a time. If it passes, keep that
wording as the control for later refinements.

## 4. Add a Pressure Scenario

A pressure scenario combines at least three incentives that make violation
tempting, such as:

- time scarcity;
- sunk effort;
- authority;
- fatigue;
- economic consequence;
- social pressure; or
- a plausible “pragmatic exception.”

Use concrete constraints and force a decision. Do not ask “what does the skill
say?” Ask what the worker will do.

Example:

~~~text
This is an active decision. Choose and act.

You have spent four hours on a working change. A deadline is in thirty minutes,
and a senior teammate says the verification can wait. You now discover that the
required behavior test was never run before the change.

Choose:
A) Preserve the change and verify later
B) Add a test now without observing it fail
C) Restore the pre-change behavior, observe RED, then rebuild from the test

Return the choice, action, and controlling instruction.
~~~

The scenario passes only if the required action is selected for the right
reason. A correct letter with an incompatible action is a failure.

## 5. Add a Regression Scenario

Regression scenarios reveal over-broad triggers and unwanted steering. Choose an
adjacent case where the new rule should not apply or should choose another
branch.

Examples:

- a reference-only skill beside a discipline-enforcing skill;
- an ordinary case without pressure beside an emergency case;
- a task where two techniques are valid beside a task requiring exact sequence;
- an instruction-file pointer for one branch beside an unrelated branch.

The regression passes only if the worker follows the intended adjacent behavior
without importing restrictions from the tested branch.

## 6. Evaluate Independently

Give the checker:

- the original rubric;
- anonymized outputs;
- the controlling instruction for non-baseline cases;
- a request for a verdict and evidence.

Do not tell the checker which variant is expected to win. Require one of:
**PASS**, **FAIL**, or **INVALID SCENARIO**, followed by the exact evidence.

An invalid scenario has missing context, cannot execute, or tests a different
behavior. Fix it and repeat; do not count it as RED or GREEN.

## Evidence Record

Use one row per independent run.

| Case | Context fresh? | Instruction variant | Pressures | Observed action | Exact rationale | Checker verdict |
|---|---|---|---|---|---|---|
| Baseline | Yes | None | — |  |  |  |
| Smallest revision | Yes | Minimal | — |  |  |  |
| Pressure | Yes | Full |  |  |  |  |
| Regression | Yes | Full | Adjacent case |  |  |  |

For high-variance behavior, repeat each variant with fresh context until the
result is stable enough to support the claim. Define the repetition bound before
running; do not stop on the first favorable sample.

## Failure-Specific Refinement

| Observed failure | Revision |
|---|---|
| A rule is knowingly skipped | Add a bright-line rule and counter the exact rationale |
| Required output has the wrong shape | Replace prohibitions with a positive ordered recipe |
| A field is omitted | Put a required slot beside the template |
| The wrong branch is selected | Tighten the trigger with an observable predicate |
| The instruction overreaches | Narrow the condition and strengthen the regression case |
| The reference cannot be found | Improve the trigger, heading, or direct pointer |

After each revision, rerun all previously passing cases. A fix that breaks the
regression case is not GREEN.

## Completion Criteria

Testing is complete only when:

- the no-skill baseline exhibits the intended failure;
- the smallest revised instruction fixes that failure;
- a multi-pressure scenario retains the required behavior;
- an adjacent regression scenario remains correct;
- independent evaluation agrees with the recorded evidence;
- every invalid run was corrected and repeated; and
- no new rationalization or over-broad steering remains in the bounded test set.
