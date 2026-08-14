# Shared Agent Skills

This directory contains portable, manually maintained skills shared by OpenCode, Codex, and Antigravity.

## Codex workflow

Codex uses the primary agent as the controller and exposes three focused roles. Their source manifests live in the repository at `.codex/agents`; the **Codex agents** strap deploys them to `~/.codex/agents`:

| Role | Responsibility |
|---|---|
| `implementer` | Complete one bounded implementation task, make only its allowed edits, and return focused verification evidence. |
| `researcher` | Perform bounded read-only codebase exploration or primary-source research, separating verified facts from inference. |
| `checker` | Independently review completed work for requirements, correctness, tests, and maintainability without editing it. |

The main feature workflow has an optional autonomous entry:

```text
`solve`(ticket or text)
  -> preserve prior state when needed
  -> low ambiguity: `writing-plans` -> `continuous-driven-development`
  -> high ambiguity: `brainstorming` -> `writing-plans` -> `subagent-driven-development`
  -> `finishing-a-development-branch`
  -> terminal manifest and optional Goal completion
```

`solve` is the lifecycle controller for an authorized ticket or text assignment. It preserves pre-existing work before task preparation, routes from recorded ambiguity evidence, and receives artifacts and verification evidence from downstream skills. Missing optional tracker, remote, or review-publication capability permits an explicitly recorded local completion; missing correctness evidence remains a blocker.

`brainstorming` remains a supported direct, user-invoked design and planning entry. After the design artifact is approved, it may transition to `writing-plans`. When `solve` records high ambiguity, `brainstorming` is the sole stage that may ask the user questions. Planning then selects the recorded execution mode:

- `continuous-driven-development` keeps tightly coupled work in the primary agent's context and runs the plan continuously in dependency order.
- `subagent-driven-development` lets the controller work directly on a small slice or assign bounded slices to `implementer`; each delegated task receives an independent `checker` review, correction and scoped re-review when needed, and durable progress artifacts.

`finishing-a-development-branch` finalizes branch state in preservation or delivery mode through semantic commits, safe synchronization, and a draft unassigned review request when supported. It never runs project verification or judges correctness; `solve`, the execution skills, `requesting-code-review`, and `verification-before-completion` own those decisions and evidence.

The controller may use `researcher` for an independent read-only question without granting edit scope. Substantial completed work uses `requesting-code-review` for combined requirements and quality review, and every completion claim passes through `verification-before-completion` with fresh project-declared evidence. A Codex Goal is an optional outer continuation contract: `solve` evaluates and marks an active Goal complete only after the terminal manifest, required verification, and durable intended state are present. Without Goal support, the terminal manifest and final report define the result.

For bug fixes, `systematic-debugging` establishes the cause before `test-driven-development` drives the repair. `grill-me`, `research`, `handoff`, and `to-questionnaire` provide focused entry points for decisions, durable investigation, context transfer, and missing external knowledge.

Durable designs, plans, research, handoffs, task reports, and reviews follow `_shared/artifact-policy.md`.

## Credits and sources

- The general engineering lifecycle—design, planning, execution, debugging, test-driven development, review, verification, and skill authoring—is adapted from [obra's Superpowers](https://github.com/obra/superpowers), baseline `v6.2.0` (`3dcbd5c`).
- `grill-me`, `grilling`, `handoff`, `research`, and `to-questionnaire` are adapted from [Matt Pocock's skills](https://github.com/mattpocock/skills), snapshot 2026-08-11.

Where the sources overlap, Superpowers remains the baseline; Matt Pocock's work is included for distinct capabilities. Both sources were adapted to this bundle's portable artifact, tool-discovery, delegation, and review contracts.

## Portability and maintenance

- VCS terms in skills name provider-neutral semantic roles, not required native primitives: a branch is a named line of work, a commit is a durable revision, a remote is a synchronization peer, and detached state is a workspace without a named line. Skills map those roles to discovered project-native capabilities and record unsupported roles as unavailable instead of assuming a named VCS, client, command, workspace mechanism, package manager, or presentation method.
- Updates are manual three-way reviews between the local copy, its recorded upstream baseline, and the local portability contract.
- Private and project-specific skills are installed separately and never linked into this public directory.
- Project checkout paths, internal project or service names, private hooks, credentials, and personal data do not belong in this bundle.
