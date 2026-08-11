---
name: dispatching-parallel-agents
description: Use when two or more independent tasks can proceed without shared mutable state or unresolved dependencies
---

# Dispatching Parallel Agents

## Overview

Parallel delegation is safe only when tasks are genuinely independent. Classify the work before dispatch, give every worker a bounded contract, and integrate only after all required results arrive.

## Decision Rule

Delegate only when two or more tasks can proceed without shared mutable state or unresolved dependencies. Prefer the configured `researcher` role for independent reading. Use `implementer` workers in parallel only when a written plan proves their file ownership does not overlap. Otherwise run implementation sequentially. Use the available client delegation capability; if none exists, perform the tasks inline. Give each worker a bounded prompt and wait for all required results before integrating them.

## Workflow

1. Separate the work into problem domains.
2. Identify dependencies, shared state, shared resources, and writable paths.
3. Choose `researcher` for independent inspection or `implementer` for an isolated change.
4. Give each worker one objective, exact scope, applicable constraints, allowed paths, required evidence, and a clear return contract.
5. Wait for every result needed by the integration.
6. Check results for incompatible assumptions or overlapping changes, then run the project-native verification for the combined result.

## Do Not Delegate in Parallel When

- One task depends on another task's result or interface.
- Workers would write the same file or mutate the same resource.
- The problem is still exploratory and its domains are not understood.
- Correctness depends on a single shared sequence of observations.

## Common Mistakes

- Treating different filenames as proof of independence while they share state or an interface.
- Sending broad prompts that permit workers to expand scope.
- Integrating the first result before required sibling results arrive.
- Delegating a tightly coupled implementation that should stay sequential.
