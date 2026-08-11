---
name: root-cause-tracing
description: Use when an error, side effect, or invalid state appears far from the code that originally triggered it
---

# Root-Cause Tracing

## Overview

Failures often appear deep in an execution path. Fixing the line where the symptom becomes visible can leave the original trigger intact.

**Core principle:** Trace backward through the call and data chain until you find where the incorrect value, state, or action first originated; fix that source.

## The Backward-Tracing Process

### 1. Describe the Symptom Precisely

Record the incorrect value, state transition, side effect, location, and the smallest known reproduction. Avoid labels such as "broken" that do not identify an observable fact.

### 2. Find the Immediate Execution Point

Identify the operation that directly produced the symptom. Use project-discovered search, diagnostics, traces, or logs. At this point you have found where the failure surfaced, not necessarily its cause.

### 3. Ask What Supplied This Input

For each argument or piece of state involved:

```
current operation received bad_value
    <- which caller supplied it?
    <- where did that caller obtain or derive it?
    <- which earlier transition first made it incorrect?
```

Record the value and relevant context at each boundary. Compare with a successful path when available.

### 4. Continue Until the Original Trigger

Do not stop at an intermediate default, adapter, or fallback. Continue until you find the first incorrect assumption, input, initialization, ordering decision, or state transition.

Evidence that you reached the source:

- The earlier state is correct and the identified transition makes it incorrect.
- Changing only that source produces the predicted downstream result.
- The explanation accounts for the entire observed call or data chain.

### 5. Fix and Protect the Source

Add regression protection for the original trigger, implement the smallest source fix, and consider [defense-in-depth.md](defense-in-depth.md) for independent validation at downstream boundaries.

## Capability-Neutral Example

```
symptom: output written to unexpected_location

write(output_location, data)
    <- save() passed output_location
    <- configuration lookup returned empty_value
    <- initialization read configuration before it was ready

root cause: initialization order exposed empty_value
symptom-only patch: change the write operation's fallback
source fix: prevent access before configuration is ready
```

When static inspection is insufficient, add temporary diagnostic output immediately before the problematic operation. Include the value, caller context, and available execution trace. Use only the diagnostics supported by the current project, and remove temporary instrumentation after the cause is understood unless it provides lasting operational value.

## When the Trigger Is One of Many Tests or Actions

Use the project's declared focused-check capability to narrow the suspect set. Split the set, run the smallest group that still reproduces the side effect, and repeat until one trigger remains. Preserve isolation and cleanup rules declared by the project.

## Checklist

- Define the symptom as an observable fact.
- Find the operation that directly produces it.
- Trace every relevant value or state one caller backward.
- Repeat until the first incorrect transition or assumption.
- Confirm the source with one minimal prediction.
- Fix at the source and add regression protection.
- Add layered validation when downstream boundaries also need protection.
