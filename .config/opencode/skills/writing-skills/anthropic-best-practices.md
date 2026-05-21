# Skill authoring best practices

> Learn how to write effective Skills that Gemini can discover and use successfully.

Good Skills are concise, well-structured, and tested with real usage. This guide provides practical authoring decisions to help you write Skills that Gemini can discover and use effectively.

## Core principles

### Concise is key

The context window is a public good. Your Skill shares the context window with everything else Gemini needs to know, including:

* The system prompt
* Conversation history
* Other Skills' metadata
* Your actual request

Not every token in your Skill has an immediate cost. At startup, only the metadata (name and description) from all Skills is pre-loaded. Gemini reads SKILL.md only when the Skill becomes relevant, and reads additional files only as needed. However, being concise in SKILL.md still matters: once Gemini loads it, every token competes with conversation history and other context.

**Default assumption**: Gemini is already very smart

Only add context Gemini doesn't already have. Challenge each piece of information:

* "Does Gemini really need this explanation?"
* "Can I assume Gemini knows this?"
* "Does this paragraph justify its token cost?"

**Good example: Concise** (approximately 50 tokens):

````markdown  theme={null}
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

### Set appropriate degrees of freedom

Match the level of specificity to the task's fragility and variability.

**High freedom** (text-based instructions):

Use when:

* Multiple approaches are valid
* Decisions depend on context
* Heuristics guide the approach

Example:

```markdown  theme={null}
## Code review process

1. Analyze the code structure and organization
2. Check for potential bugs or edge cases
3. Suggest improvements for readability and maintainability
4. Verify adherence to project conventions
```

**Low freedom** (specific scripts, few or no parameters):

Use when:

* Operations are fragile and error-prone
* Consistency is critical
* A specific sequence must be followed

Example:

````markdown  theme={null}
## Database migration

Run exactly this script:

```bash
python scripts/migrate.py --verify --backup
```

Do not modify the command or add additional flags.
````

## Skill structure

### Naming conventions

Use consistent naming patterns to make Skills easier to reference and discuss. We recommend using **gerund form** (verb + -ing) for Skill names, as this clearly describes the activity or capability the Skill provides.

**Good naming examples (gerund form)**:

* "Processing PDFs"
* "Analyzing spreadsheets"
* "Managing databases"
* "Testing code"
* "Writing documentation"

### Writing effective descriptions

The `description` field enables Skill discovery and should include both what the Skill does and when to use it.

<Warning>
  **Always write in third person**. The description is injected into the system prompt, and inconsistent point-of-view can cause discovery problems.

  * **Good:** "Processes Excel files and generates reports"
  * **Avoid:** "I can help you process Excel files"
</Warning>

Effective examples:

**PDF Processing skill:**

```yaml  theme={null}
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Task Logging skill:**

```yaml  theme={null}
description: Generate descriptive task logs by analyzing file changes. Use when the user asks for help writing progress reports or reviewing local changes.
```

### Progressive disclosure patterns

SKILL.md serves as an overview that points Gemini to detailed materials as needed.

* Keep SKILL.md body under 500 lines for optimal performance
* Split content into separate files when approaching this limit

#### Pattern 1: High-level guide with references

````markdown  theme={null}
---
name: PDF Processing
description: Extracts text and tables from PDF files, fills forms, and merges documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
---

# PDF Processing

## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
**Examples**: See [EXAMPLES.md](EXAMPLES.md) for common patterns
````

### Avoid deeply nested references

**Keep references one level deep from SKILL.md**. All reference files should link directly from SKILL.md to ensure Gemini reads complete files when needed.

## Workflows and feedback loops

### Use workflows for complex tasks

Break complex operations into clear, sequential steps.

### Implement feedback loops

**Common pattern**: Run validator → fix errors → repeat

## Content guidelines

### Avoid time-sensitive information

Don't include information that will become outdated.

### Use consistent terminology

Choose one term and use it throughout the Skill.

## Common patterns

### Template pattern

Provide templates for output format.

### Examples pattern

For Skills where output quality depends on seeing examples, provide input/output pairs.

````markdown  theme={null}
## Task log format

Generate task logs following these examples:

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**Example 2:**
Input: Fixed bug where dates displayed incorrectly in reports
Output:
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```
````

## Evaluation and iteration

### Build evaluations first

**Create evaluations BEFORE writing extensive documentation.**

### Develop Skills iteratively with Gemini

The most effective Skill development process involves Gemini itself. Work with one instance of Gemini ("Gemini A") to create a Skill that will be used by other instances ("Gemini B").

## Anti-patterns to avoid

### Avoid offering too many options

Don't present multiple approaches unless necessary.

## Advanced: Skills with executable code

### Solve, don't punt

When writing scripts for Skills, handle error conditions rather than punting to Gemini.

### Provide utility scripts

Even if Gemini could write a script, pre-made scripts offer advantages: reliable, save tokens, save time, ensure consistency.

### Create verifiable intermediate outputs

When Gemini performs complex tasks, use the "plan-validate-execute" pattern to catch errors early.

### Runtime environment

Skills run in a code execution environment with filesystem access and bash commands.

* **File paths matter**: Use forward slashes (`reference/guide.md`), not backslashes.
* **Bundle comprehensive resources**: No context penalty until accessed.
* **Prefer scripts for deterministic operations**.

### MCP tool references

If your Skill uses MCP (Model Context Protocol) tools, always use fully qualified tool names: `ServerName:tool_name`.

## Checklist for effective Skills

* [ ] Description is specific and includes key terms
* [ ] Description includes both what the Skill does and when to use it
* [ ] SKILL.md body is under 500 lines
* [ ] Additional details are in separate files (if needed)
* [ ] Consistent terminology throughout
* [ ] Examples are concrete, not abstract
* [ ] File references are one level deep
* [ ] Workflows have clear steps
* [ ] Scripts solve problems rather than punt to Gemini
* [ ] Error handling is explicit and helpful
* [ ] Validation/verification steps for critical operations
* [ ] At least three evaluations created
