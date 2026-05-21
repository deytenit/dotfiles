---
name: defense-in-depth
description: Use when building critical systems, security-sensitive features, or preventing destructive side-effects - requires layering multiple independent checks at different levels
---

# Defense-in-Depth

## Overview

A single failure shouldn't cause a disaster.

**Core principle:** Multiple independent layers of protection.

## The Strategy

Instead of one complex check, use several simple checks at different layers. If one fails, others catch it.

### Layer 1: Input Validation
Validate parameters at the entry point.

### Layer 2: Business Logic
Check invariants before executing the core logic.

### Layer 3: Environment Guards
Refuse to perform dangerous operations in sensitive environments (e.g., tests, production).

### Layer 4: Monitoring/Logging
Log what you're about to do so you can trace what happened if things go wrong.

## Example: Preventing Accidental Directory Creation

**Problem:** A bug caused `mkdir -p` to run in the wrong directory during tests.

**Layered Protection:**

```typescript
// Layer 1: Explicit parameter (no defaults)
async function setupWorkspace(directory: string) {
  if (!directory) throw new Error('directory is required');

  // Layer 2: Refuse suspicious locations
  if (directory.startsWith('/etc') || directory === '/') {
    throw new Error(`Refusing to setup workspace in sensitive directory: ${directory}`);
  }

  // Layer 3: In tests, refuse operations outside temp directories
  if (process.env.NODE_ENV === 'test' && !directory.includes('/tmp')) {
    throw new Error(`Refusing to create directory outside temp dir during tests: ${directory}`);
  }

  // Layer 4: Traceability
  logger.debug('About to mkdir -p', { directory });
  
  await fs.mkdir(directory, { recursive: true });
}
```

## Why This Works

If someone passes an empty string (Layer 1 fails), the parameter check catches it.
If a relative path resolves to a sensitive location (Layer 1 passes), Layer 2 catches it.
If logic is correct but environment is wrong (Layers 1 & 2 pass), Layer 3 catches it.
If all checks fail, Layer 4 provides the breadcrumbs to find the root cause.

## Red Flags

- Single point of failure
- Trusting input without validation
- Hardcoding sensitive paths
- "It works on my machine"

## Implementation Checklist

- [ ] Identify the most destructive outcome (e.g., data loss, accidental file creation)
- [ ] Add input validation (Layer 1)
- [ ] Add invariant checks (Layer 2)
- [ ] Add environment guards (Layer 3)
- [ ] Add trace logging (Layer 4)
- [ ] Verify each layer independently
