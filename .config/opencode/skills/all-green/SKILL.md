---
name: all-green
description: Use when the user requests $all-green or asks to fix both review findings and CI failures and update the PR with this workflow.
---

Use the workspace's applicable code review tool to review the current PR and collect existing issues, and its CI diagnostics tool to inspect failing checks. Discover the capabilities from the workspace rather than assuming a provider; report unavailable capabilities instead of inventing results. Follow additional context and scope supplied with the invocation.

1. Check review findings against the code, fix every substantiated issue in scope, and record why any finding is declined. Diagnose CI failures and fix those caused by the PR, using the workspace's CI-fixing skill (such as `fix-ci-issues`, when available). Respect its check-selection rules and report unrelated failures separately.
2. Verify the affected behavior. Use `finishing-a-development-branch` in delivery mode with the evidence to update the existing PR. Commit fixes with the exact title `Fix PR issues`; amend instead if the branch's top commit already has that exact title and belongs to this PR. Preserve unrelated changes and history, use safe synchronization, and create no empty commit. This title and amendment rule overrides the finishing skill's defaults. Keep the existing PR title, description, and publication state.
3. After the fixes are verified and synchronized to the PR, delete a fixed issue's draft only when it belongs to the user; resolve a fixed posted issue silently, without a reply. Leave other people's drafts untouched. For a declined review finding, leave a draft explanation starting with `🤖`; keep the issue unresolved and never publish the draft. If drafts are unavailable, show the explanation in chat.
4. Recheck the PR's CI for the updated revision. If it reveals new failures caused by these changes, fix and verify them and update the same top fix commit. Limit retries to the applicable project rule, or three attempts per issue if none is declared; then report the blocker. Report pending checks as pending and unrelated failures separately; claim all green only when the current revision's relevant checks have passed and no actionable review findings remain.

Keep CI progress, failure, and completion reports in chat, without any CI-related PR comments, including drafts. Apply this restriction to delegated skills, permission checks, and error handlers too: skip comment-producing helpers and use a read-only alternative or report the capability gap in chat. The only comment writes in this workflow are the review-draft handling described above.

A direct request to run this workflow authorizes the PR update and review-issue cleanup above. Creating or editing this skill does not run it. Finish with a concise chat report of fixed, declined, pending, and blocked items.
