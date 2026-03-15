Architectural Decision Records (ADR)
====================================

An Architectural Decision Record (ADR) is a specialized document that captures a significant design choice, the context in which it was made, and the consequences it imposes on the system. It serves as a permanent record of the "why" behind an architecture, preventing knowledge loss and reducing technical debt.

What
----

In architecture, a **Decision** is a high-stakes commitment that is difficult or expensive to reverse. Unlike day-to-day coding tasks, these choices define the fundamental structure and constraints of the system.

An ADR is characterized by:

-   **Scope:** It affects the system's "fitness for purpose" (performance, scalability, reliability).

-   **Permanence:** It is intended to last for a significant portion of the project lifecycle.

-   **Complexity:** It involves navigating conflicting requirements and making explicit trade-offs.

Why
---

Maintaining a repository of ADRs provides several strategic advantages:

-   **Institutional Memory:** It prevents "Cargo Cult" engineering where teams follow patterns without understanding the original rationale.

-   **Onboarding Velocity:** New engineers can read the ADR log to understand the current state of the system without requiring hours of meetings.

-   **Transparency in Trade-offs:** It forces stakeholders to acknowledge that every benefit comes with a cost (e.g., choosing speed over absolute data consistency).

-   **Auditability:** It provides a clear trail of accountability for regulatory compliance or safety-critical reviews, which is essential in fields like robotics and medical software.

How
---

Every ADR must follow a standardized structure to remain searchable and useful. Use the following fields to document your decisions:

1.  **Title:** `[ID]. [Short Descriptive Title]` (e.g., `005\. Use WebRTC for Low-Latency Teleop`).

2.  **Status:** `Proposed`, `Accepted`, or `Superseded by [ID]`.

3.  **Context:** Describe the technical environment and the specific problem or pressure that triggered the need for a decision.

4.  **Decision:** Use the phrase **"We shall..."** followed by a clear action. Explain the "why" and detail the trade-offs.

5.  **Alternatives:** Briefly list other options considered and the specific reasons they were rejected.

6.  **Consequences:** A list of positive, negative, and neutral impacts resulting from the decision. This section should be updated over time.

7.  **Governance:** Identify the decision-makers and the team responsible for implementation.

### Example Decision Record: [Example](004_ADR_Example.md)
