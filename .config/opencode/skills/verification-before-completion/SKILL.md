---
name: verification-before-completion
description: Use when about to claim work is complete, fixed, or passing, before declaring changes ready or ending a task
---

# Verification Before Completion

## Overview

**Core principle:** Evidence before claims, always.

**Violating the letter of this rule is violating the spirit of the rule.**

## The Iron Law

```
NO COMPLETION CLAIM WITHOUT FRESH VERIFICATION EVIDENCE
```

An earlier run, expectation, or second-hand report cannot support a current claim.

## The Evidence Gate

Before claiming completion, correctness, a fix, readiness, or passing checks:

1. **Define the claim.** State exactly what must be true.
2. **Discover the evidence source.** Consult applicable project instructions and declared project capabilities to identify the relevant check; do not rely on a remembered command.
3. **Run it fresh.** Use the scope that actually exercises the claim.
4. **Inspect current output.** Read the complete result available, including exit status, failure count, warnings, and skipped work relevant to the claim.
5. **Compare evidence with the claim.** If the output does not prove the claim, report the actual status and limitation.
6. **Only then state success.** Cite the fresh result that supports it.

Skipping any step is not verification.

## Match Evidence to the Claim

| Claim | Required evidence | Not sufficient |
|---|---|---|
| A check passes | Fresh output from that project-declared check with no relevant failures | A previous run or a different check |
| A defect is fixed | The original reproduction and its regression case now pass | A code change that appears plausible |
| A regression test works | Observed RED failure for the intended reason, then GREEN success | A test that has only passed |
| A build artifact is valid | Fresh output from the declared build or validation capability | Static analysis alone |
| Requirements are met | Each requested requirement inspected against the result and relevant evidence | A passing check that covers only part of the request |
| Delegated work is complete | Independent inspection and relevant checks | A completion report from another worker |

## Scope Correctly

Verification must be relevant and proportionate. Start with the narrowest project-declared check that proves the behavior, then run any broader declared check required by applicable project instructions or by the risk of the change.

Do not invent a universal project-wide checklist. The closest applicable project instructions define what evidence is required.

## Red Flags

Stop before claiming success if you notice:

- "It should work now."
- "The change looks correct."
- Confidence based on an earlier run.
- A partial check being used to imply unrelated properties.
- Ignored warnings, skipped cases, or truncated output.
- Trust in a delegated report without independent inspection.
- Fatigue or urgency being used to skip the fresh run.
- Different wording being used to imply success without evidence.

## Reporting

When evidence supports the claim, report the check, its fresh result, and any meaningful scope limits. When it does not, report the failure or missing capability plainly and do not imply completion.

## Final Rule

Run the relevant project-declared check. Inspect its current output. Then—and only then—make the claim.
