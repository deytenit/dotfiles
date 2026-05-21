---
name: completing-task
description: Use when implementation is complete, all tests pass, and you need to decide how to integrate the work - guides completion of development work by presenting structured options for integration or cleanup
---

# Completing a Task

## Overview

Guide completion of development work by presenting clear options and handling chosen workflow.

**Core principle:** Verify tests → Present options → Execute choice → Clean up.

**Announce at start:** "I'm using the completing-task skill to complete this work."

## The Process

### Step 1: Verify Tests

**Before presenting options, verify tests pass:**

```bash
# Run project's test suite
npm test / cargo test / pytest / go test ./...
```

**If tests fail:**
```
Tests failing (<N> failures). Must fix before completing:

[Show failures]

Cannot proceed until tests pass.
```

Stop. Don't proceed to Step 2.

**If tests pass:** Continue to Step 2.

### Step 2: Determine Integration Target

Identify the main project directory where changes should be applied.

### Step 3: Present Options

Present exactly these 3 options:

```
Implementation complete. What would you like to do?

1. Apply changes to the main project
2. Keep the workspace as-is (I'll handle it later)
3. Discard this work

Which option?
```

**Don't add explanation** - keep options concise.

### Step 4: Execute Choice

#### Option 1: Apply Changes

```bash
# Copy changed files back to main project
# (Implementation depends on the environment, but conceptually:)
rsync -a --exclude="node_modules" --exclude=".workspaces" . <main-project-path>

# Verify tests in the main project
cd <main-project-path>
<test command>
```

Then: Cleanup workspace (Step 5)

#### Option 2: Keep As-Is

Report: "Keeping workspace at <path>."

**Don't cleanup workspace.**

#### Option 3: Discard

**Confirm first:**
```
This will permanently delete:
- All changes in the workspace at <path>

Type 'discard' to confirm.
```

Wait for exact confirmation.

If confirmed:
Then: Cleanup workspace (Step 5)

### Step 5: Cleanup Workspace

**For Options 1, 3:**

```bash
rm -rf <workspace-path>
```

**For Option 2:** Keep workspace.

## Quick Reference

| Option | Integrate | Keep Workspace | Cleanup Workspace |
|--------|-----------|----------------|-------------------|
| 1. Apply changes | ✓ | - | ✓ |
| 2. Keep as-is | - | ✓ | - |
| 3. Discard | - | - | ✓ |

## Common Mistakes

**Skipping test verification**
- **Problem:** Integrate broken code
- **Fix:** Always verify tests before offering options

**Open-ended questions**
- **Problem:** "What should I do next?" → ambiguous
- **Fix:** Present exactly 3 structured options

**Automatic workspace cleanup**
- **Problem:** Remove workspace when might need it (Option 2)
- **Fix:** Only cleanup for Options 1 and 3

**No confirmation for discard**
- **Problem:** Accidentally delete work
- **Fix:** Require typed "discard" confirmation

## Red Flags

**Never:**
- Proceed with failing tests
- Integrate without verifying tests on result
- Delete work without confirmation

**Always:**
- Verify tests before offering options
- Present exactly 3 options
- Get typed confirmation for Option 3
- Clean up workspace for Options 1 & 3 only

## Integration

**Called by:**
- **subagent-driven-development** - After all tasks complete
- **executing-plans** - After all batches complete

**Pairs with:**
- **isolating-workspace** - Cleans up workspace created by that skill
