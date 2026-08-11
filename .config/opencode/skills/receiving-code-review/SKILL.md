---
name: receiving-code-review
description: Use when receiving code review feedback, before implementing suggestions, especially when feedback is ambiguous or technically questionable
---

# Receiving Code Review

## Overview

Review feedback is a technical claim to evaluate, not an instruction to accept blindly or an occasion for performative agreement.

**Core principle:** Understand, verify, and evaluate before implementing. Technical correctness and the user's intent take priority over social comfort.

## Response Pattern

For each review item:

1. **Read** the complete feedback and its context.
2. **Understand** the requested outcome in your own words.
3. **Clarify** any ambiguity before changing related code.
4. **Verify** the claim against current code, behavior, tests, and applicable project instructions.
5. **Evaluate** correctness, compatibility, scope, and necessity for this project.
6. **Respond** with a technical acknowledgment, a focused question, or reasoned pushback.
7. **Implement** one accepted item at a time.
8. **Check** the smallest project-declared check that exercises that item before continuing.

## Ambiguous Feedback

If an item can reasonably mean more than one thing, stop before implementation and ask a specific question. When several items depend on the same unclear assumption, clarify that assumption before implementing any of them.

Example:

```
I understand items 1, 2, and 5. Items 3 and 4 could mean either
<interpretation A> or <interpretation B>; which outcome is intended?
```

Partial understanding produces partial or contradictory fixes.

## Technical Evaluation

Before accepting a suggestion, determine:

- Is the claim true in the current code?
- Does the suggestion preserve existing behavior and supported environments?
- Why does the current implementation exist?
- Does the suggestion conflict with a user decision or applicable project instruction?
- Is the requested generality actually used, or is it speculative?
- What evidence would confirm the suggestion is safe?

If evidence is unavailable, state what cannot be verified and ask whether to investigate further or proceed with an explicitly named risk.

## Reasoned Pushback

Push back when a suggestion is technically incorrect, breaks supported behavior, adds unused scope, ignores a compatibility constraint, or conflicts with an established decision.

Effective pushback:

- States the relevant evidence.
- Explains the concrete consequence.
- Asks a focused question or offers a scoped alternative.
- Avoids defensiveness and status arguments.

Example:

```
The current compatibility check shows this path is still required for the
supported environment. Removing it would break <behavior>. Should the support
requirement change, or should I address the narrower issue in <location>?
```

Expertise and authority are reasons to inspect a suggestion carefully, not substitutes for verification.

## Implement One Item at a Time

For multi-item feedback:

1. Resolve ambiguities and conflicts first.
2. Prioritize correctness and safety issues, then independent simple items, then larger structural items.
3. Implement one item.
4. Run the relevant project-declared check and inspect current output.
5. Continue only when the result is understood.

This preserves traceability between feedback, change, and evidence. Do not batch unrelated suggestions into one untestable change.

## Correct Feedback

When feedback is supported, act or acknowledge it technically:

```
Confirmed: <specific issue>. Changed <behavior or location>; <check> now shows <result>.
```

Do not claim the reviewer is correct until you have verified the claim. If earlier pushback was wrong, state the new evidence and corrected understanding directly.

## Common Mistakes

| Mistake | Better response |
|---|---|
| Immediate agreement | Restate and verify the technical claim |
| Implementing an unclear item | Ask a focused clarification first |
| Assuming authority proves correctness | Check current code and behavior |
| Avoiding justified pushback | Present evidence and concrete consequences |
| Accepting speculative scope | Search for actual use and ask whether it is required |
| Implementing several items together | Change and check one item at a time |
| Proceeding when verification is unavailable | State the limitation and request direction |

## Final Rule

Feedback is input to evaluate. Understand it, verify it, then implement or push back with evidence.
