# LLMs Belong at the Generic Layer

*This article assumes familiarity with Domain-Driven Design. If you are not, [start here](../../design/concepts/Domain.md).

---

## Opinion

I believe LLMs are structurally mismatched with the core domain. The three-domain taxonomy from DDD — core, supporting, generic — gives us a precise framework for understanding why. The argument is not that LLMs are generally weak. They are genuinely useful in supporting and generic domains. The argument is that their architecture puts them in direct conflict with what the core domain actually requires.

I see this intuited constantly by experienced engineers who pull back from LLM use on the parts of their systems that matter most, without always being able to say why. Here is the explicit reasoning.

---

## Rationale

**LLMs are trained on the generic and the published.** Large language models are trained on text that exists publicly: documentation, tutorials, Stack Overflow answers, open-source repositories, research papers, and textbooks. This corpus is dense with generic domain knowledge. It contains almost no core domain knowledge, because core domain knowledge is by definition proprietary, unpublished, and not written down in any form that reaches a training corpus. A company's differentiating planning algorithm, its specific approach to edge-case handling, its internally developed domain model — none of this is there. The model is systematically uninformed about exactly the part of the system that matters most.

This is not a theoretical concern. A 2024 study by researchers at Microsoft examined LLM performance on proprietary C# and C++ codebases — code that had never appeared in any public dataset. The framing of the paper captures the problem precisely: these projects use specific naming standards, coding conventions, and proprietary APIs, making their code "substantially different from the publicly available code that LLMs were trained on." [1] The implication is structural, not incidental.

**The averaging effect destroys precision at the boundary conditions that matter.** Even where core domain knowledge has been partially published — in research papers or open-source reference implementations — a general-purpose model learns it averaged across many sources, many interpretations, and many levels of quality. The core domain requires the opposite: the exact semantics of a concept as *this team* has defined it, the exact constraint that applies in *this system* and not others, the exact tradeoff that was made and why. Averaging produces a plausible approximation that looks correct at the surface and fails precisely at the boundary conditions where core domain logic is actually exercised.

**LLMs have no access to the ubiquitous language.** The ubiquitous language — one of DDD's foundational tools — is developed over time through collaboration between domain experts and engineers. It is specific to one organisation's model of one problem. A general LLM has not participated in that process. Even with RAG or fine-tuning that injects proprietary schemas and wikis into the model's context, the LLM still lacks the dynamic, lived understanding of the domain. Reading a dictionary does not make one fluent in a culture.

The model may use the right words — *Trajectory*, *Obstacle*, *PlanningHorizon* — while violating the invariants those words encode within a specific bounded context. The vocabulary is surface. The invariants are substance. LLMs have reliable access to the former and no reliable access to the latter.

**LLMs cannot hold bounded context discipline.** A well-designed system enforces explicit boundaries between contexts. An LLM has no internal equivalent: it is one undifferentiated model trained on all domains simultaneously. When asked to reason about a core domain problem, it draws on everything it has seen — including patterns from adjacent domains, generic solutions that do not apply, and similar-looking problems with different constraints. The output conflates contexts in ways a domain expert would immediately identify as wrong, but that a less experienced engineer might not catch.

There is an inversion here worth stating directly. In robotics and autonomous systems, I find that the expert-as-implementer pattern — where the same person who understands the physics also writes the code — can be a liability to bounded-context discipline. Someone who understands perception, planning, and control simultaneously is tempted to paper over the boundary in their head, because they can see through it informally. That temptation is why the explicit interface never gets drawn.

LLMs take this to the extreme. They are the most multi-domain fluent entity in the room, which sounds like an advantage until you realise that fluency was built by collapsing distinctions that domain experts spent careers drawing carefully. A model trained on perception research, planning literature, and control theory simultaneously has no incentive to maintain the boundaries between them — nothing in its training rewarded that discipline. It will reach for unified representations naturally, not because it is wrong about the physics, but because the boundary was never a constraint it had to respect.

**A brief observation on DSLs.** Domain experts frequently build Domain Specific Languages — a precise vocabulary and constraint system for navigating the problem space far more efficiently than natural language allows. I have not yet seen a language model build its own DSL to solve a problem. That gap may narrow; I am uncertain. But even if it does, I doubt it changes the fundamental argument. DSLs are invented for domain experts to communicate and reason about problems *with other domain experts*. The artefact is social as much as technical. An LLM that generates a DSL-like structure has not participated in the social and epistemic process that gives the DSL its authority within the team.

**AI-generated core domain code is replicable by any competitor.** This is the point I find most structurally damaging, and it is not primarily a code quality concern. The core domain is the source of strategic advantage. That argument depends on the core domain encoding knowledge that is specific, accumulated, and hard to reproduce. When the core domain is built substantially by an AI model inventing or deriving the logic, that assumption breaks down. Any competitor with access to the same model and a similar prompt can produce equivalent code. The moat shifts upstream to the proprietary constraints and system design you feed the AI — not the generated code itself.

Generic domain code is supposed to be replicable — DDD explicitly says to buy it rather than build it. Core domain code is supposed to be irreproducible. An LLM inverts this property. It makes core domain code as replicable as generic domain code, while carrying none of the reliability guarantees of a well-maintained open-source library. The result is code that is neither differentiated nor dependable.

**These failures are structural, not a matter of prompting.** They follow from the fundamental design of current LLMs: domain-agnostic training, statistical pattern matching, no persistent model of a specific system's invariants. Writing better prompts or providing more context does not resolve them; it may paper over them in individual interactions. The appropriate response is not to avoid LLMs entirely. Apply them where their strengths align with the domain taxonomy. They are genuinely useful at the generic domain layer — boilerplate, tooling, documentation, test scaffolding — and useful with oversight at the supporting domain layer, where the organisation's specific context can be provided explicitly and the cost of a wrong assumption is recoverable. At the core domain layer, they are a liability if treated as authoritative.

Vernon's advice maps cleanly: the core domain is where the most experienced people should work, where the most explicit modelling effort should go, and where off-the-shelf solutions are inappropriate. LLMs, for now, are an off-the-shelf solution.

---

## Updates

*Nothing yet.*

---

## References

[1] Studying LLM Performance on Closed- and Open-source Data. arXiv:2402.15100 (2024). https://arxiv.org/html/2402.15100v1
