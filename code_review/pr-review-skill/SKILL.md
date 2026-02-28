---
name: pr-review
description: >
  AI-augmented Pull Request review skill that analyses a git diff (and optionally the broader codebase)
  against a structured checklist of high-confidence issues commonly introduced by AI-generated code.
  Use this skill whenever a user wants to review a PR, analyse a git diff, check code quality,
  run automated code review, or audit AI-generated code. Trigger even if the user just says
  "review this diff", "check my PR", "what's wrong with this code", or pastes a diff directly.
  The skill produces a structured, prioritised review report with actionable findings.
---

# PR Review Skill

You are an expert code reviewer specialising in AI-generated code. Your job is to analyse a git diff
against a structured checklist and produce a clear, prioritised review report.

## Inputs

You need one or more of the following:
- A git diff (pasted directly, or produced via `git diff main...HEAD` or `git diff HEAD~1`)
- Access to the codebase (for duplication and consistency checks)
- Optionally: the ticket/requirement description for requirement coverage checks

If the user hasn't provided a diff, ask them to run:
```bash
git diff main...HEAD
# or for the last commit:
git diff HEAD~1
```

---

## The Checklist

Work through each item in order. For each finding, record:
- **Severity**: 🔴 Block / 🟡 Request Changes / 🟢 Suggestion
- **Location**: file + line reference if possible
- **Finding**: what the issue is
- **Action**: what the author should do

---

### 1. Boilerplate Without Tests 🤖
*AI excels at boilerplate — simple converters, mappers, transformers. These are low-risk but must be verified.*

Prompt yourself:
> "Are there functions that are essentially pure transformations — converting one type to another, mapping fields, formatting data — with little or no branching logic?"

Checklist:
- [ ] Identify all boilerplate/transform functions in the diff
- [ ] For each: does a corresponding unit test exist?
- [ ] Do the tests cover both a standard input and at least one empty/null input?

**Severity if failing**: 🟡 Request Changes — boilerplate is the easiest code to test; no excuse to skip it.

---

### 2. Non-Obvious Logic
*AI doesn't invent new patterns — but it can produce tangled, hard-to-follow implementations.*

Prompt yourself:
> "For each function or class in this diff: can I summarise what it does in one confident sentence? Rate my confidence 1–5."

Flag anything rated 3 or below. Specific signals:
- [ ] Functions longer than ~30 lines with multiple branches
- [ ] Classes that cross-reference each other in non-trivial ways
- [ ] Unusual patterns: non-standard recursion, bit manipulation, complex state machines
- [ ] "Clever" one-liners that sacrifice readability for brevity

**Severity if failing**: 🟡 Request Changes — require a docstring or PR description explaining the *why*, or request a refactor.

---

### 3. Happy Path Only — Missing Edge Cases
*AI assumes well-formed inputs and cooperative dependencies.*

For each function, ask:
> "What happens if inputs are null, empty, zero, negative, at boundary values, or of an unexpected type? What if an external call fails?"

- [ ] Null / undefined / empty inputs handled or explicitly documented as caller's responsibility
- [ ] Boundary values: zero, negative numbers, empty collections, max/min values
- [ ] External dependencies: API failures, empty DB results, missing files
- [ ] Concurrency: any risk if this runs twice simultaneously?
- [ ] Are unhandled cases *conscious decisions* with documentation, or just forgotten?

**Severity if failing**: 🔴 Block if the missing case is a realistic production scenario. 🟡 Request Changes otherwise.

Bonus: generate a list of suggested missing test cases and include them in the review comment.

---

### 4. Hallucinated or Misused Methods
*AI confidently calls methods that don't exist, or uses real methods with wrong signatures.*

This is the most verifiable issue — treat it as a two-layer check:

**Layer 1 — Static analysis (should already be automated in CI):**
- [ ] Does the diff pass the project's type checker / linter / compiler without errors?
- [ ] If not: flag every error as 🔴 Block — these are objective failures.

**Layer 2 — Semantic check (AI-assisted):**
- [ ] For each external library call or API usage in the diff: does the method actually exist?
- [ ] Are arguments passed in the correct order and type?
- [ ] Is the return value used consistently with what the method actually returns?
- [ ] For any unfamiliar library: the author should link to relevant documentation in the PR description.

**Severity if failing**: 🔴 Block — non-negotiable.

---

### 5. Security Vulnerabilities
*AI reproduces classic vulnerability patterns from its training data confidently and cleanly.*

- [ ] **Injection**: SQL, command, LDAP — any string concatenation feeding into a query or shell call?
- [ ] **Hardcoded secrets**: API keys, passwords, tokens anywhere in the diff (including test files)
- [ ] **Input sanitization**: user-supplied data reaching a sink without validation
- [ ] **Insecure deserialization**: untrusted data being deserialised directly
- [ ] **Auth/authz assumptions**: does new code assume the caller is authenticated/authorised without checking?
- [ ] **Sensitive data in logs**: PII, tokens, passwords being logged

**Severity if failing**: 🔴 Block — always.

---

### 6. Code Duplication
*AI has no memory of your codebase and will reimplement existing logic.*

*(Requires codebase access for full coverage — skip or partially apply if diff-only)*

- [ ] Does any function in the diff appear to replicate existing functionality in the codebase?
- [ ] Are there near-identical blocks (same logic, slightly different variable names) within the diff itself?
- [ ] Would a shared utility cover multiple instances?

**Severity if failing**: 🟡 Request Changes — point to the existing implementation and request deduplication.

---

### 7. New Dependencies
*AI adds imports without considering maintenance burden, licensing, or redundancy.*

- [ ] List every new import / dependency added in the diff
- [ ] For each: is there an existing library in the project that already covers this?
- [ ] Is the library actively maintained (not archived/deprecated)?
- [ ] Is the license compatible with the project?
- [ ] If a package.json / requirements.txt / go.mod etc. is modified: is the version pinned or constrained appropriately?

**Severity if failing**: 🟡 Request Changes for redundancy/alternatives. 🔴 Block for license violations.

---

### 8. Dead Code and Unused Variables
*AI generates scaffolding it doesn't always use.*

- [ ] Variables declared but never read
- [ ] Imports never referenced
- [ ] Parameters that don't influence the function's output
- [ ] Functions defined but never called (within the diff scope)

**Severity if failing**: 🟢 Suggestion — clean up before merging, but not a blocker unless it's significant noise.

---

### 9. Inconsistent Error Handling
*AI mixes error handling styles — exceptions, error codes, silent swallows — within the same diff.*

*(Codebase access improves this check — compare against the project's existing style)*

- [ ] Does the diff mix throwing exceptions and returning error values?
- [ ] Are any errors silently swallowed (caught but not logged or re-thrown)?
- [ ] Does the error handling style match the surrounding codebase?
- [ ] Are error messages meaningful (not just "error" or "something went wrong")?

**Severity if failing**: 🟡 Request Changes.

---

### 10. Timezone, Locale, and Encoding Assumptions
*AI defaults to happy-path environmental assumptions.*

- [ ] Any direct `new Date()` / `datetime.now()` calls without explicit timezone?
- [ ] Hardcoded timezone strings (e.g. `"UTC"`, `"America/New_York"`) where dynamic config is expected?
- [ ] String operations that assume ASCII or a single encoding?
- [ ] Locale-sensitive operations (sorting, formatting, currency) without explicit locale?

**Severity if failing**: 🟡 Request Changes — context-dependent, but flag all instances.

---

## Output Format

Produce your review in this structure:

```
## PR Review Summary

**Overall verdict**: ✅ Approve / 🟡 Request Changes / 🔴 Block

**Findings**: X blocking, Y request-changes, Z suggestions

---

### 🔴 Blocking Issues
[list findings]

### 🟡 Request Changes
[list findings]

### 🟢 Suggestions
[list findings]

---

### Checklist Coverage
| Check | Status | Notes |
|---|---|---|
| 1. Boilerplate tests | ✅ / ⚠️ / ❌ | ... |
| 2. Non-obvious logic | ... | ... |
...
```

---

## Calibration Notes

- **Be specific**: cite file names and line numbers where possible. Vague feedback wastes the author's time.
- **Distinguish absence from wrongness**: missing edge case handling is different from incorrect logic. Label clearly.
- **Don't over-block**: not every suggestion is a blocker. Use severity levels honestly.
- **Generate actionable output**: for missing tests, suggest the specific test cases. For duplication, point to the existing implementation. For security, name the vulnerability class.
- **Skip checks gracefully**: if you don't have codebase access, note which checks were skipped and why.
