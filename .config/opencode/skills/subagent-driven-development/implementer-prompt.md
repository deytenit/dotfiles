# Implementer Prompt Contract

Use this bounded contract with the configured `implementer` role or the client's equivalent.

## Inputs

- Task brief path: `[TASK_BRIEF_PATH]`
- Scope: `[SCOPE]`
- Writable paths: `[WRITABLE_PATHS]`
- Inherited constraints: `[INHERITED_CONSTRAINTS]`
- Earlier interfaces consumed by this task: `[EARLIER_INTERFACES]`
- Report path: `[REPORT_PATH]`

The dispatcher must include `[REPORT_PATH]` in `[WRITABLE_PATHS]` or state it as an explicit additional writable allowance.

## Instructions

1. Read the task brief and inherited constraints before editing.
2. Implement the complete task within the stated scope and writable paths.
3. Follow discovered project-native conventions and run the smallest project-native verification that exercises the change.
4. Self-review the implementation against every requirement in the brief.
5. Write the detailed result to the report path.

Do not write outside the declared writable paths and additional report allowance. Do not spawn agents. If essential context or capability is missing, report that status instead of guessing or expanding scope.

## Report Contract

Return exactly one status:

- `DONE`: complete, verified, and ready for review.
- `DONE_WITH_CONCERNS`: complete and verified, with named correctness or scope concerns.
- `NEEDS_CONTEXT`: missing information prevents safe completion.
- `BLOCKED`: a concrete constraint or unavailable capability prevents completion.

The report must include the status, paths changed, implementation summary, project-native verification commands and results, self-review findings, and any missing context or blocker. For every correction round, the controller supplies a fresh, uniquely named report path following the task report pattern with `-correction-<R>` before `.md`. Write the addressed findings and fresh verification evidence there. Never append to or replace an earlier report.
