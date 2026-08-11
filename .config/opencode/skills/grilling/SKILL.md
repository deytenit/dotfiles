---
name: grilling
description: Use when the user asks to be grilled or wants a plan, decision, or idea exhaustively stress-tested before action.
---

Map the subject as a design tree: each unresolved decision branches into decisions that depend on it.

Work in rounds. The frontier is every question whose prerequisites are already settled. Ask the current frontier as numbered questions, and include your recommended answer for each. Then wait for the user's answers before recomputing the frontier.

Find environmental facts yourself. When a factual investigation is independent and delegation is available, use the configured `researcher` role or the client's equivalent; otherwise inspect the environment directly. Ask the user for decisions and preferences, not facts available from their environment.

The workflow ends only when every reachable branch has been resolved and the user confirms shared understanding. Do not implement the result inside this workflow.
