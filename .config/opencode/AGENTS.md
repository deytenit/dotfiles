# Personal Agent Instructions

These are portable personal defaults. Follow higher-priority instructions and the closest applicable project instructions when they are more specific.

## Discover the environment

- Before non-trivial work, read the applicable project instructions and the project-declared documentation, manifests, or skills for the action.
- Never assume the VCS, package manager, test runner, build system, repository layout, or available integration. Derive them from the current environment.
- Prefer a project-native capability when one exists. If none is declared, use the safest available capability that fits the task.

## Stay faithful to the request

- Implement the requested outcome completely while keeping changes inside the stated scope.
- Read, review, diagnose, and planning requests authorize inspection and reporting. Build, change, and fix requests authorize in-scope local edits and relevant checks.
- Ask before destructive actions, external publication, material cost, or a meaningful expansion of scope.
- Do not add unrelated refactors, dependencies, documentation, examples, abstractions, formatting changes, or comments that merely restate the code.
- Add comments only when requested, required by project conventions, or needed to explain a non-obvious constraint or decision.
- Preserve existing behavior and public interfaces unless changing them is part of the request.

## Search deliberately

- Prefer native discovery and search facilities declared by the project or environment.
- Otherwise search with an explicit path, a precise identifier or pattern, relevant file types, and bounded output.
- Avoid repository-wide recursive globs, vast recursive text searches, and traversal of dependency, generated, cache, or build directories.
- Give exploratory filesystem searches an explicit timeout of at most 30 seconds.

## Run commands predictably

- Use a default timeout of 300 seconds for shell commands.
- The user, an applicable project instruction, a relevant skill, or the known behavior of a command may override that default.
- Derive commands from project evidence. Check that a required executable exists before relying on it.
- Prefer reversible operations. Confirm exact targets before destructive changes.

## Skills and delegation

- Use a relevant skill when its trigger matches the task.
- Delegate only when a written multi-task plan, genuinely independent investigation, or independent review makes the extra context worthwhile.
- Keep small, tightly coupled, or overlapping work on the primary agent.
- Give workers only their bounded task, constraints, relevant paths, and artifact references. Do not duplicate the full conversation.

## Communication and evidence

- Keep progress updates concise and useful.
- State what changed, what evidence was checked, and what remains uncertain.
- Never claim a command, check, or result occurred when it did not.
