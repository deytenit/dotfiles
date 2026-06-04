# AGENTS.md

This document defines the operating contract for any AI coding agent working in this repository. Follow it strictly. When in doubt, **learn before you act** — never assume, never default.

---

## 1. Core Principles

1. **MCP is your knowledge base, not a toolbox.** The connected MCP servers expose **guides, docs, runbooks, and skills** that describe *how things are done here*. They are the first place you look to learn the local way of doing anything — VCS, testing, building, releasing, debugging, onboarding a feature, etc.
2. **No defaults. No muscle memory.** Do not reach for `git`, `npm`, `pytest`, `make`, or any other "standard" tool because it is standard. The local stack may use something entirely different. **You must look it up.**
3. **Evidence over assumption.** Every non-trivial action must be backed by a guide you read, a doc you consulted, or a script you inspected in this session. If you cannot point to the source, you are guessing — stop and read.
4. **Smallest viable action.** Narrowest read, most targeted edit, most scoped command.
5. **Determinism and reversibility.** Prefer actions you can predict and undo. Destructive operations require explicit user confirmation.
6. **NEVER query from repository root** - you may only and only work within allowed-by-user workspace. All the commands must be run from this workspace. You don't need to run any VCS commands from repository root.

---

## 2. The MCP Mental Model

Treat MCP servers as **a library of institutional knowledge**, not as a set of executors. A typical interaction looks like:

> "I need to do X."
> → Search MCP for a guide/skill/doc about X.
> → Read it.
> → Follow the procedure it describes, using the tools *it* names.

Concrete examples of how this replaces defaults:

| You want to… | ❌ Do **not** assume | ✅ Instead |
|---|---|---|
| Commit / branch / view history | `git ...` | Search MCP for the VCS guide (e.g. an Arcanum / Mercurial / Sapling / custom workflow doc) and follow it. |
| Add a test | `pytest` / `jest` / `go test` | Read the "writing tests" guide in MCP; use the runner and conventions it specifies. |
| Add a new feature | Start coding | Read the relevant feature/architecture doc or skill in MCP first. |
| Run a typecheck | `tsc` / `mypy` | Inspect the project's package scripts / task definitions; run the declared command. |
| Lint / format | `eslint` / `ruff` / `prettier` | Same — find the declared script. |
| Build / release | `npm run build` | Same — find the declared script or release runbook. |
| Query a service, DB, or API | Guess endpoints | Read the service's doc/skill in MCP. |

**If a guide does not exist for what you need, ask the user before improvising.**

---

## 3. Discovery Protocol (Do This First, Every Session)

### 3.1 Enumerate MCP content
- List the connected MCP servers and the resources/skills/guides they offer.
- Skim the index. Build a mental map: "VCS is documented here, testing here, deployment here."
- **Do not** assume an MCP server exposes executable tools. Most expose **knowledge**. Read it.

### 3.2 Read what the repo declares about itself
Open these (when present) with direct, targeted reads — not recursive scans:
- `README*`, `CONTRIBUTING*`, `AGENTS.md` (this file), `.editorconfig`
- Manifest files at the repo root (existence is not assumed; check first): e.g. `package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`, `BUILD`, `Makefile`, etc.
- CI configuration in conventional locations for canonical lint/test/build commands.

### 3.3 Derive every command from evidence
- The test command, build command, lint command, typecheck command, and release command are **discovered**, never recalled.
- Read them from the manifest's scripts/tasks, or from an MCP guide that names them.
- If both sources exist and disagree, prefer the MCP guide and flag the discrepancy to the user.

---

## 4. No Assumed Tools — Including VCS

- **Do not invoke `git` on a first call, or any call, unless you have confirmed via an MCP guide that `git` is the local VCS.** This project may use Arcanum, Sapling, Mercurial, Fossil, or a custom workflow. The right command is whatever the guide says.
- The same applies to package managers, test runners, container tools, cloud CLIs, and editors.
- Before invoking any binary, do **two** things:
  1. Confirm from an MCP guide or repo manifest that this is the correct tool for the task here.
  2. Verify the binary exists with a fast, bounded probe (e.g. `command -v <tool>` ≤ 5s). Remember the result for the session.
- If step 1 fails, **read more MCP first.** If step 2 fails, ask the user.

---

## 5. Search and Navigation Rules

Searching the filesystem is the most common source of wasted context. Apply these rules without exception.

### 5.1 Forbidden patterns
- ❌ Recursive globs like `**/*` over the whole repo.
- ❌ `grep -r` / ripgrep over the whole repo without a path scope.
- ❌ `find . -name ...` without a depth limit or path prefix.
- ❌ Listing known-large directories (`node_modules`, `vendor`, `dist`, `build`, `target`, `.venv`, `__pycache__`, `.git`, etc.).
- ❌ Reading lockfiles, generated files, or minified bundles unless directly asked.

### 5.2 Required patterns
- ✅ Prefer the MCP knowledge index over filesystem search when the question is "how do we do X here."
- ✅ Constrain every search by **path prefix**, **file extension**, and **max results**.
- ✅ Prefer exact identifiers (symbol names, error strings) over fuzzy substrings.
- ✅ When exploring unfamiliar territory, list **one directory at a time** and drill down.
- ✅ Cap output; paginate only when necessary.

### 5.3 Reading files
- Read targeted ranges when you know the symbol; read the whole file only when it is small or the structure is unknown.
- Do not re-read a file already in context without a reason.

---

## 6. Command Execution Rules

### 6.1 Universal 30-second timeout
**Every shell command must declare an explicit timeout of ≤ 30 seconds.** If a command might legitimately take longer (full test suite, full build, large install), you must:
1. State the expectation to the user,
2. Get confirmation, **or**
3. Scope the command down (single test file, single package, incremental build) so it fits within 30s.

No exceptions. A runaway command burns the session.

### 6.2 Safe-by-default behavior
- Use non-interactive flags only when the project's own scripts already use them. Do not force-install or auto-upgrade.
- Never pipe network content into a shell.
- Never `rm -rf`, `chmod -R`, `chown -R`, force-push, rewrite history, or change global config without explicit user instruction for that specific action.
- Never run presumably long output commands without limiter. Commands such as 'log' or 'cat' must be run with explicit limits set.

### 6.3 Working directory and environment
- Run from the repo root unless a script says otherwise.
- Do not export env vars, alter `PATH`, or mutate shell state in a persistent way.
- Do not write outside the repository unless the task requires it.

---

## 7. Editing Rules

1. **Read before you write.** Never edit a file you have not read this session.
2. **Match local style.** Indentation, quoting, naming, imports, comments — follow what is in the file, not your defaults.
3. **Minimal diffs.** Change only what the task requires. No opportunistic refactors or reformatting.
4. **No drive-by dependency changes.** If a dependency change is required, use the package manager the project declares (discovered, not assumed).
5. **Preserve public interfaces** unless changing them is the task.
6. **No new files unless needed.** Never create READMEs, docs, or examples unprompted.
7. **No commented-out code, no ownerless TODOs, no dead code.**

---

## 8. Verification

After making changes:

1. **Re-read the modified regions** to confirm the edit landed correctly.
2. **Run the project's declared checks**, scoped to the affected area, using the commands you discovered in §3.3.
3. If a check fails, fix the cause — do not loosen the check, disable the rule, or delete the failing test.
4. If you cannot run a check (tool missing, env unavailable), say so explicitly. Do not claim it passed.

---

## 9. Version Control (Restated, Because This Is the #1 Failure Mode)

- **Do not run `git` reflexively.** It may not be the VCS. It may not be installed. The correct workflow is whatever the MCP VCS guide describes.
- Do not commit, branch, push, tag, merge, rebase, stash, or reset unless explicitly asked **and** you have read the local VCS guide.
- Never amend or force-push.
- Never modify VCS internals (`.git/`, `.hg/`, `.sl/`, etc.) directly.
- Do not configure user identity, remotes, or hooks.

---

## 10. Secrets, Network, and Data

- Treat anything that looks like a credential, token, key, or connection string as sensitive. Do not print, log, or summarize it.
- Do not exfiltrate file contents to network endpoints.
- Do not make outbound network calls except through MCP tools designed for it or commands the user has approved.
- Do not read files outside the repository (home dotfiles, OS keychains, cloud credential files) unless explicitly required.

---

## 11. Communication With the User

- **Be concise.** Report what you did, what you found, what is left. Skip preamble.
- **Cite specifics.** Reference file paths, symbol names, and the guides you consulted.
- **Surface uncertainty.** If you guessed, say so. If a check did not run, say so. If a result is partial, say so.
- **Ask when blocked.** If MCP discovery does not yield an answer, ask one focused question instead of improvising.
- **Do not fabricate** file contents, command output, API signatures, or test results.

---

## 12. Task Lifecycle

For any non-trivial task:

1. **Restate** the goal in one sentence.
2. **Plan** in 3–7 concrete steps. Keep the plan visible; update it as you go.
3. **Learn**: search MCP for guides/skills covering each step.
4. **Discover** the project's declared commands (§3.3).
5. **Execute** the smallest step, verify, then proceed.
6. **Verify** per §8.
7. **Summarize**: files changed and why, what was verified, what was not, follow-ups.

---

## 13. Stop Conditions

Stop and ask the user when:
- An MCP guide for the action does not exist.
- A required tool or capability is missing.
- The task would require a destructive or irreversible action not explicitly requested.
- Two or more reasonable interpretations of the request exist.
- A check fails in a way that suggests the task definition itself is wrong.
- You are about to run a command that violates §5, §6, or §9.

---

## 14. Pre-Action Checklist

Before **every** tool call, confirm:

- [ ] Have I checked MCP for a guide/skill covering this action?
- [ ] Have I confirmed the tool I'm about to use is actually the one this project uses (not a default I assumed)?
- [ ] Is the scope as narrow as possible (path, extension, symbol, line range)?
- [ ] Does every shell command have a ≤ 30s timeout?
- [ ] Have I verified the binary exists?
- [ ] Am I about to read or change something I have not yet seen?
- [ ] Is this action reversible, or do I need confirmation?

If any answer is "no," revise before issuing the call.

