---
description: Fix in-scope CI failures for the given PR
agent: build
---

You are already on the correct branch for the given PR.

Your task is to fix the failing CI checks for **direct-modules**, **components**, **uac** but **only** the failures that can be resolved by changing files in the repository.

## First: inspect CI via MCP tools
1. Call `list_pull_request_ci_flows` for PR.
2. Find the relevant failed flow(s), especially those related to **direct-modules**.
3. For each relevant failed flow, call `list_ci_flow_tasks`.
4. Use the attached task resources/logs to identify the exact causes of failure before making changes.

## Scope: fix only file-based issues
You may fix:
- unit tests
- typecheck failures
- lint / eslint issues
- formatting / prettier issues
- stylelint issues
- unused code / imports / exports
- dependency-cruiser issues
- documentation issues
- coverage issues that can be fixed by editing source code, tests, or docs

## Explicitly out of scope
Do **not** spend time on or modify anything related to:
- e2e tests
- Hermione / Storybook / screenshot-based tests
- Tanker
- anything that requires:
  - updating screenshots
  - recording or re-recording fixtures
  - updating visual baselines
  - pushing translation keys to a backend
  - manual external system changes
  - infra/environment-only fixes outside the repo

If a failure belongs to one of the categories above, **skip it** and move on.

## Working rules
- Make the **smallest targeted changes** needed to fix the failing checks
- Unless stated otherwise, treat production code as complete from logical standpoint - update test assertions, mocks...
- Do not do broad refactors or unrelated cleanup.
- Prefer fixing the root cause over suppressing errors.
- Do not switch branches.
- Do not modify CI config unless it is clearly necessary for an in-scope fix and can be validated from the repo itself.
- Ignore Hermione-related failures even if they are red; they will be handled manually later.

## Execution plan
1. Inspect failed CI flows/tasks with the MCP tools.
2. Classify failures into:
   - **in scope**
   - **out of scope**
3. Reproduce the **in-scope** failures locally with targeted commands.
4. Apply fixes.
5. Re-run the relevant checks locally until they pass.
6. Stop once all in-scope issues are fixed or no further progress can be made without entering out-of-scope work.

## Expected result
Deliver a commit-ready working tree that fixes all **in-scope** failures for direct-modules in PR `12719937`.

At the end, provide a short summary:
- which CI failures were investigated
- which ones were fixed
- what commands/checks were run
- which failures remain and why they were skipped as out of scope
