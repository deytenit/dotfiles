# Persuasion Principles for Instruction Design

## Purpose

Clear instructions must sometimes hold under pressure. Persuasion principles can
strengthen legitimate, user-serving rules, but they must not manufacture urgency,
hide trade-offs, or override user authority.

Use this reference only after a baseline shows that an agent understands a rule
but rationalizes it away. For output shape, missing fields, or branch selection,
use a positive recipe, structural slot, or observable conditional instead.

## Relevant Principles

### Authority

Use direct, unambiguous language for established safety or quality constraints:
“must,” “never,” and “no exceptions.” This reduces negotiation where the rule is
genuinely non-negotiable.

Avoid authority language when several approaches are valid.

### Consistency

Ask for an explicit choice, criterion, or evidence record before action. A
visible decision makes later deviations detectable.

Useful forms:

- announce which rule governs the task;
- choose among concrete options;
- record pass/fail criteria before testing;
- track required steps in a visible checklist.

### Scarcity

Use sequence boundaries such as “before editing” or “immediately after the
failure” when delay would invalidate evidence. Do not invent deadlines or
consequences.

### Social Proof

State a universal norm only when it is actually universal. Pair it with the
failure mode it prevents.

### Unity

Frame collaboration around shared outcomes and honest technical judgment.
Unity should support candid disagreement, never liking or flattery.

### Reciprocity and Liking

Do not use reciprocity or liking to enforce compliance. They add social pressure
without improving the technical basis of a rule and can encourage sycophancy.

## Choosing the Form

| Instruction need | Useful principles | Avoid |
|---|---|---|
| Discipline under pressure | Authority, consistency, truthful scarcity | Soft suggestions, invented urgency |
| Collaborative judgment | Unity, explicit criteria | Flattery, status pressure |
| Technique guidance | Moderate authority, clear conditions | Absolute language |
| Reference lookup | Clarity only | Persuasive framing |
| Output shape | Positive recipe | Prohibition-heavy wording |

## Bright-Line Rules

Bright-line wording works when the baseline agent knows the correct rule but
seeks an exception. It should:

1. state the required action;
2. identify the observable trigger;
3. close only rationalizations seen in testing;
4. state a checkable completion criterion.

Example:

~~~markdown
If implementation exists before its behavior test, restore the prior behavior
and begin from a failing test. Keeping the implementation as a reference does
not satisfy test-first.
~~~

This is stronger than “prefer tests first,” but remains scoped to an observable
condition.

## Ethical Boundary

Use persuasive language only when all are true:

- the rule serves the user's stated interests;
- the trigger is factual and observable;
- the action remains within granted authority;
- the consequence is not exaggerated;
- the wording is no stronger than the tested failure requires.

If any condition fails, use neutral guidance and surface the trade-off.

## Research Foundation

These principles adapt established work on persuasion and instruction
compliance:

- Cialdini, R. B. (2021), *Influence: The Psychology of Persuasion*.
- Meincke, L., Shapiro, D., Duckworth, A. L., Mollick, E., Mollick, L., and
  Cialdini, R. (2025), *Call Me A Jerk: Persuading AI to Comply with
  Objectionable Requests*.

Research describes influence, not permission. The user's interests and explicit
constraints remain the boundary.

## Quick Check

Before strengthening an instruction, ask:

1. Did the baseline show rationalization rather than confusion?
2. Which exact pressure caused the violation?
3. Is a bright-line rule the right form for that failure?
4. Is every strong claim true and scoped?
5. Does a pressure scenario pass?
6. Does an adjacent regression scenario remain unchanged?
