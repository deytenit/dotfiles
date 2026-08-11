# Combined Task Reviewer Prompt Contract

Use this contract with the configured `checker` role or the client's equivalent.

## Inputs

- Requirements path: `[REQUIREMENTS_PATH]`
- Implementer report path: `[REPORT_PATH]`
- Relevant changed paths: `[CHANGED_PATHS]`
- Verification evidence: `[VERIFICATION_EVIDENCE]`

## Instructions

Perform a read-only review. Do not edit files. Read the requirements and relevant changed paths; treat the implementer report and verification evidence as claims to validate.

Review both axes in one pass:

- Requirements: missing, extra, or misunderstood behavior.
- Quality: correctness, maintainability, security, integration, and whether tests protect the changed behavior.

Do not broaden the review without a concrete risk. If the supplied material cannot establish a requirement or verification result, name the exact gap rather than guessing.

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
