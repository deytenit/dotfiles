# Shared Agent Skills

This directory contains portable, manually maintained skills shared by OpenCode, Codex, and Antigravity.

## Codex workflow

Codex uses the primary agent as the controller and exposes three focused roles from `../agents/codex`:

| Role | Responsibility |
|---|---|
| `implementer` | Complete one bounded implementation task, make only its allowed edits, and return focused verification evidence. |
| `researcher` | Perform bounded read-only codebase exploration or primary-source research, separating verified facts from inference. |
| `checker` | Independently review completed work for requirements, correctness, tests, and maintainability without editing it. |

The main feature workflow is:

```text
user invokes `brainstorming`
  -> approved design artifact
  -> `writing-plans`
  -> approved plan artifact
     -> `continuous-driven-development` for inline execution by the primary agent
     -> `subagent-driven-development` for bounded implementation and review tasks
```

`brainstorming` is entered only when the user explicitly invokes it. After the design artifact is approved, it may transition to `writing-plans`. Planning then offers two execution modes:

- `continuous-driven-development` keeps tightly coupled work in the primary agent's context and runs the plan continuously in dependency order.
- `subagent-driven-development` lets the controller work directly on a small slice or assign bounded slices to `implementer`; each delegated task receives an independent `checker` review, correction and scoped re-review when needed, and durable progress artifacts.

The controller may use `researcher` for an independent read-only question without granting edit scope. Substantial completed work uses `requesting-code-review` for combined requirements and quality review, and every completion claim passes through `verification-before-completion` with fresh project-declared evidence.

For bug fixes, `systematic-debugging` establishes the cause before `test-driven-development` drives the repair. `grill-me`, `research`, `handoff`, and `to-questionnaire` provide focused entry points for decisions, durable investigation, context transfer, and missing external knowledge.

Durable designs, plans, research, handoffs, task reports, and reviews follow `_shared/artifact-policy.md`.

## Credits and sources

- The general engineering lifecycle—design, planning, execution, debugging, test-driven development, review, verification, and skill authoring—is adapted from [obra's Superpowers](https://github.com/obra/superpowers), baseline `v6.2.0` (`3dcbd5c`).
- `grill-me`, `grilling`, `handoff`, `research`, and `to-questionnaire` are adapted from [Matt Pocock's skills](https://github.com/mattpocock/skills), snapshot 2026-08-11.

Where the sources overlap, Superpowers remains the baseline; Matt Pocock's work is included for distinct capabilities. Both sources were adapted to this bundle's portable artifact, tool-discovery, delegation, and review contracts.

## Portability and maintenance

- Skills describe outcomes and discover project-native capabilities instead of prescribing a VCS, command, package manager, worktree, client API, or presentation method.
- Updates are manual three-way reviews between the local copy, its recorded upstream baseline, and the local portability contract.
- Private and project-specific skills are installed separately and never linked into this public directory.
- Project checkout paths, internal project or service names, private hooks, credentials, and personal data do not belong in this bundle.
