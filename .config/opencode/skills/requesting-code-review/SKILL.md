---
name: requesting-code-review
description: Use when completing a task, implementing a substantial change, or preparing to claim that work meets its requirements
---

# Requesting Code Review

## Overview

Use the configured `checker` role, or the client's equivalent, for one read-only review that covers both requirements and quality. Give the reviewer evidence and the smallest useful context, not the session history.

## Reviewer Package

Supply all four inputs:

- The requirements or their precise path.
- The relevant changed paths.
- Fresh verification evidence for those changes.
- The smallest useful surrounding context needed to judge concrete risks.

Use [code-reviewer.md](code-reviewer.md) as the prompt contract.

## Review Loop

1. Dispatch one `checker` after the scoped implementation and verification are complete.
2. Validate each finding against the requirements, changed files, and evidence.
3. Correct evidence-backed problems; push back on unsupported findings with technical evidence.
4. Re-review the correction before claiming completion.

Do not substitute self-review for an independent checker. Do not ignore a failed requirements verdict, a quality verdict that requires changes, or a named verification gap.

## Required Output

```markdown
## Findings

- `path:line` — severity — evidence-backed problem and required correction

## Verdicts

- Requirements: pass | fail | unable to verify
- Quality: approved | changes required
- Verification gaps: none, or a precise list
```

An empty review says `No findings.` under `## Findings` and still supplies all three verdict lines.
