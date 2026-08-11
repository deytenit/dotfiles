# Combined Code Reviewer Prompt

Use this contract with the configured `checker` role or the client's equivalent.

## Inputs

- Requirements: `[REQUIREMENTS_OR_PATH]`
- Relevant changed paths: `[CHANGED_PATHS]`
- Verification evidence: `[VERIFICATION_EVIDENCE]`
- Smallest useful surrounding context: `[SURROUNDING_CONTEXT]`

## Review Contract

Perform a read-only review. Do not edit files. Inspect the relevant changed paths rather than trusting a summary.

Return one combined judgment:

- Requirements: identify missing, extra, or misunderstood behavior.
- Quality: identify correctness, maintainability, security, integration, or test problems that justify a correction.
- Verification: distinguish evidence already supplied from checks that are missing or impossible to verify.

Every finding must cite `path:line`, assign a calibrated severity, state the evidence-backed problem, and require a concrete correction. Do not invent findings to fill the section. If an input is unavailable, name the resulting verification gap instead of guessing.

## Output Format

```markdown
## Findings

- `path:line` — severity — evidence-backed problem and required correction

## Verdicts

- Requirements: pass | fail | unable to verify
- Quality: approved | changes required
- Verification gaps: none, or a precise list
```

When there are no findings, write `No findings.` under `## Findings` and still include all three verdict lines.
