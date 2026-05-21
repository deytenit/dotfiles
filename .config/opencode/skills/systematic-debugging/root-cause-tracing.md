---
name: root-cause-tracing
description: Use when encountering side-effects or state changes that shouldn't happen (file creation in wrong location, env pollution, etc.) - requires tracing execution back to the original trigger
---

# Root-Cause Tracing

## Overview

Bugs often manifest deep in the call stack (file created in wrong location, database opened with wrong path, environment variable overwritten). Your instinct is to fix where the error appears, but that's treating a symptom.

**Core principle:** Trace the "bad value" back to its source.

## The Strategy

### 1. Identify the Symptom
Specifically what is wrong?
- File `config.json` created in `/tmp` instead of `/Users/user/project/.config`
- Environment variable `API_KEY` is empty

### 2. Identify the Immediate Execution Point
Which line of code actually performed the action?
- Use grep to find the call: `grep -r "fs.writeFile" .`
- Use stack trace if an error was thrown

### 3. Trace the Parameters Backwards
How did the function get that specific value?
- Add trace logging at the execution point
- Rerun and look at the stack trace
- Follow the value up the call stack to the previous caller

### 4. Find the Original Trigger
Where was the value first defined or derived?
- Often a configuration load, an environment variable read, or a default value used when a parameter was missing.

## Example: Accidental File Creation

**Symptom:** `config.json` created in the project root instead of `.config/`.

**Tracing:**

1. **Find execution point:**
   ```typescript
   // src/utils/fs.ts
   await fs.writeFile(path, content);
   ```

2. **Add logging:**
   ```typescript
   console.error('DEBUG writeFile:', { path, stack: new Error().stack });
   await fs.writeFile(path, content);
   ```

3. **Rerun tests and check logs:**
   ```bash
   npm test 2>&1 | grep 'DEBUG writeFile'
   ```
   *Output shows `path` is `config.json` and stack trace points to `ConfigManager.save()`.*

4. **Follow up the stack:**
   ```typescript
   // src/config.ts
   class ConfigManager {
     save() {
       const dir = this.getDir() || process.cwd(); // BAD DEFAULT
       return fs.writeFile(path.join(dir, 'config.json'), data);
     }
   }
   ```

**Root cause found:** Empty return from `getDir()` caused it to fall back to `process.cwd()`.

## Tools for Tracing

### Polluter Finding
If you don't know which test file is causing the side-effect, use `find-polluter.sh`:
```bash
./find-polluter.sh 'config.json' 'src/**/*.test.ts'
```

### Trace Logging
Always include the stack trace when logging for root-cause analysis:
```typescript
console.log('TRACE:', { value, stack: new Error().stack });
```

## Implementation Checklist

- [ ] Define the symptom clearly
- [ ] Find the line that performs the action
- [ ] Add stack trace logging
- [ ] Identify the caller that provided the bad value
- [ ] Repeat until you find where the value was first defined
- [ ] Fix the source, not the symptom
