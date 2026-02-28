# AI-Augmented PR Review

## What
A Claude Code skill that analyses a git diff and produces a structured review report.

```bash
git diff main...HEAD  # paste into Claude and ask it to review
```

Output is findings sorted by severity:

| Symbol | Severity | Expectation |
| :--- | :--- | :--- |
| 🔴 | **Block** | Do not merge. Must be fixed. |
| 🟡 | **Request Changes** | Address before approval, or explicitly defer with justification. |
| 🟢 | **Suggestion** | Nice to have. No change required. |

## Why
This tool is **not a replacement for human review — it is an augmentation.** It handles the mechanical, pattern-based checks so your review budget goes toward what actually requires judgement.

## How
Ten automated checks run against every diff:

| # | Check | Catches |
| :--- | :--- | :--- |
| 1 | Boilerplate without tests | Transform/mapper functions with no unit tests |
| 2 | Non-obvious logic | Code the AI itself can't summarise in one sentence |
| 3 | Happy path only | Missing null checks, error states, boundary handling |
| 4 | Hallucinated methods | Calls to methods that don't exist or wrong signatures |
| 5 | Security vulnerabilities | Injection, hardcoded secrets, unsanitised input |
| 6 | Code duplication | Logic that already exists in the codebase |
| 7 | New dependencies | Unflagged imports — redundancy, maintenance, licence |
| 8 | Dead code | Declared but unused variables, imports, parameters |
| 9 | Inconsistent error handling | Mixed exception/return styles, silent swallows |
| 10 | Timezone & locale assumptions | Implicit UTC, ASCII, or locale where config is expected |

## What AI Cannot Check — Human Eyes Required

- **Requirement coverage** — does the code actually do what the ticket asked?
- **Architectural fit** — is this the right approach for *this* codebase?
- **The 30% gap** — domain-specific edge cases, integration contracts, non-functional requirements
- **Ownership** — can the author explain what they submitted? If not, it shouldn't merge.
- **Degraded AI output patterns** — an author consistently failing multiple checks simultaneously is a workflow problem, not a code problem. Have the conversation.

## Examples

**[🔴 Block]** `fetchUser` makes no attempt to handle a failed db call or an empty result set. The caller receives `undefined` silently. Add error handling and an explicit not-found response before merging.

**[🟡 Request Changes]** `toUserDTO` is a pure transform with no tests. Add a unit test covering a standard input and a null input.

**[🟢 Suggestion]** This helper already exists in `src/utils/format.ts`. Consider importing rather than re-implementing.

## Install

```
.claude/skills/pr-review/SKILL.md
```
