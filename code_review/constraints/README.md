Guide: Writing a CONSTRAINTS.md File
====================================

What
----

The `CONSTRAINTS.md` file is a high-leverage context document designed to prevent "invisible" regressions - system failures caused by changes that look safe in isolation but break external dependencies, timing windows, or infrastructure assumptions.

Why
---

This document is **not** a replacement for unit tests, integration tests, or types. It addresses the "Knowledge Gap" that occurs when code is technically correct but contextually breaking.

### It is NOT:

-   **A Test Plan**: If you can assert a behavior with `expect(a).toBe(b)` within the repository, do it in code, not here.

-   **API Documentation**: Don't list every endpoint. Only list the ones with "fragile" external dependencies.

-   **A Technical Spec**: It shouldn't describe *how* a feature works, only the *boundaries* it must stay within.

### It IS a safeguard for:

-   **The "Network Blindspot"**: Unit tests pass when you rename a field, but the mobile app 3 versions back suddenly crashes.

-   **The "Side-Effect Surprise"**: A database optimization is logically sound but accidentally starves a legacy reporting tool that connects via a read-replica.

-   **The "Temporal Trap"**: Code works in staging but causes a race condition in production because it misses a hard 2:00 AM data-sync window.

How
---

## Core Principles

1.  **Plain English Only**: No code snippets, JSON schemas, or YAML. It must be readable by humans and LLMs as a set of rules.

2.  **Beyond Tests**: Focus on cross-service contracts, network dependencies, and "hidden" side effects.

3.  **Impact-First**: Every entry must explicitly state what breaks if the constraint is ignored.

4.  **Contextual Links**: Reference external tickets (Jira/Linear) or ADRs only if deeper history is required.

## The Document Structure

### 1\. Header Metadata

Start with the service identity and ownership so the AI/Developer knows the scope.

-   **Service**: The specific component this file governs.

-   **Owner**: The team responsible for these constraints.

### 2\. Constraint Blocks

Each block must use a **Typed Prefix** to help AI agents filter relevant context.

#### Kinds of Constraints:

-   **`CONTRACT`**: External APIs, Webhooks, or Shared Libraries. Focus on the "shape" of data moving across boundaries.

-   **`TIMING`**: Race conditions, TTLs, Cron windows, and latency requirements.

-   **`SCHEMA`**: Database columns or Event Bus envelopes shared with other systems (ETLs, BI tools).

-   **`INFRA`**: Environment variables, hardcoded ports, queue names, or cloud resource assumptions.

The Template
------------

```
CONSTRAINTS for: [service-name]
Last updated: [YYYY-MM-DD]
Owned by: [team-name]

---

[KIND]: [Short Descriptive Title]
  [Description of the constraint in plain English. Explain the "Why".]
  Status: [Permanent | Temporary - migration in progress]
  Affects: [List specific external services, teams, or dashboards]
  Safe changes: [What can you do without fear?]
  Unsafe changes: [What are the specific "red lines"?]
  Link: [Optional link to Jira/ADR for historical context]

[KIND]: [Next Title]
  ...

```

Checklist for a Good Constraint
-------------------------------

-   [ ] **Is it non-obvious?** (If a junior dev wouldn't know it by looking at the code, put it here).

-   [ ] **Does it mention an "Affected" party?** (e.g., "The Finance Team's Excel Export").

-   [ ] **Is it "Frozen"?** If something is unchangeable (e.g., legacy queue name), mark as "No safe changes".

-   [ ] **Is it concise?** Keep descriptions to 3-4 sentences.

-   [ ] **Verification**: Mention how to manually verify this if automation is impossible.Guide: Writing a CONSTRAINTS.md File

