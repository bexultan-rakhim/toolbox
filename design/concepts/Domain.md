Domain: A Concept in Software and Knowledge
===========================================

What
----

I like to think about software in different types of expertise needed to build complex system. Rarely remarkable software requires one type of expertise.

A **domain** is the subject-matter area a piece of software is built to serve. It is the problem space — the real-world activity, rules, and knowledge that software must model in order to be useful. In banking, the domain includes accounts, transactions, and interest rules. In autonomous driving, it includes perception, motion planning, and vehicle dynamics.

The term has two related but distinct meanings that are often used together:

**1. Knowledge domain** — the field of expertise that a specialist works within. A structural engineer operates in the civil engineering domain. A controls engineer in robotics operates in the dynamics and control domain. The knowledge domain is pre-software: it exists in the real world and is encoded in textbooks, standards, and expert intuition before a single line of code is written.

**2. Domain in Domain-Driven Design (DDD)** — a software-design concept introduced by Eric Evans in *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003). Here, the domain is the primary organizing principle of a software system. Code is structured around the vocabulary, rules, and boundaries of the problem space rather than around technical layers (database, API, UI). The software model is a direct reflection of how domain experts understand the world.

The two meanings converge on a single idea: **code should be shaped by the real-world problem it solves, and the people who understand that problem most deeply should have authority over how it is modeled.**


Why
---

### The Core Problem DDD Solves

Before DDD, software was typically organized around technical concerns: a database layer, a service layer, a presentation layer. This structure is intuitive to engineers but is invisible to the people who actually understand the problem — the domain experts. The result is a translation gap. A business analyst says "an order can only be fulfilled after payment clears"; the developer encodes this as a conditional in a service method buried in a package called `com.app.services`. The rule exists in the code, but nobody can find it, read it, or verify it without understanding the implementation.

Evans' central argument is that this gap is the primary source of complexity in enterprise software. When the code does not reflect the domain model, every change requires translation in both directions — from business language into code, and back again when diagnosing bugs. Over time, the model drifts and the translation becomes unreliable.

DDD's solution is to make the domain model the first-class artifact of the system. Code is written in the language of the domain — classes, methods, and variables use the same terms that domain experts use — so that the software and the expert's mental model stay in alignment.

### The Three Domain Types

Evans and subsequent practitioners, particularly Vaughn Vernon in *Implementing Domain-Driven Design* (2013), distinguish three types of domains within a system:

**Core domain** is the part of the system that delivers the primary competitive or functional value. It is unique to the organization and cannot be bought off the shelf. In an autonomous vehicle, the motion planning stack — how the vehicle decides its path given a scene — is a core domain. It is the source of differentiation. It should receive the most design investment, the most experienced engineers, and the most explicit modeling effort.

**Supporting domain** assists the core but is not itself the differentiator. It is specific to the organization but could, in principle, be built more simply or outsourced. In an AV system, the data labeling pipeline or the scenario database tooling might be supporting domains — necessary but not the product.

**Generic domain** contains problems that are common across many organizations and are best solved with existing solutions. Logging, authentication, time-series storage, and message queuing are generic domains. DDD explicitly recommends not designing these from scratch. Use a library, a framework, or a managed service. Generic domain code is not where intellectual effort should be concentrated.

This classification matters because it guides resource allocation and design depth. Applying the full complexity of DDD modeling to a generic domain is waste. Treating a core domain as if it were generic — by buying an off-the-shelf solution that does not fit — destroys differentiation.

### Ubiquitous Language

One of DDD's most important practical tools is the **ubiquitous language**: a shared vocabulary, agreed upon by engineers and domain experts, that is used consistently in both conversation and code. If a domain expert calls something a "waypoint" and the codebase calls it a `PathNode`, there is a translation layer in every conversation and every code review. The ubiquitous language eliminates this by requiring that the code use the same terms as the domain.

In practice, this means that naming in code is not a purely technical decision. A class named `Trajectory` in an AD system carries a specific physical meaning — a time-parameterized sequence of states — and should not be renamed `Path` simply because a developer preferred it. The name belongs to the domain, not to the implementation.

### Bounded Contexts

As systems grow, a single unified domain model becomes difficult to maintain. Evans introduces the **bounded context** as the solution: a clearly defined boundary within which a particular domain model applies and is consistent. Outside that boundary, a different model may use different terms or different rules for the same concept.

In an AV system, the perception bounded context may define an `Object` as a detected entity with a bounding box and a confidence score. The planning bounded context may define an `Obstacle` as an entity with a predicted trajectory and a risk weight. These are not the same model, and they should not be forced into one. The bounded context makes the boundary explicit and defines how the two models communicate at their interface.

### Tradeoff Analysis

| Dimension | Domain-first design (DDD) | Technology-first design |
|---|---|---|
| **Alignment with experts** | High — code mirrors the mental model | Low — translation required constantly |
| **Initial cost** | High — requires deep domain modeling upfront | Low — start with familiar tech patterns |
| **Long-term maintainability** | High — changes are localized to bounded contexts | Low — changes propagate across layers |
| **Suitable for generic problems** | Poor — over-engineering for commodity concerns | Good — generic solutions fit generic problems |
| **Team structure** | Teams organized around domains | Teams organized around technical layers |
| **Onboarding domain experts** | Easier — code is readable to non-engineers | Harder — domain logic is buried in tech concerns |
| **Risk** | Misjudging domain boundaries is expensive to fix | Technology debt is more visible and addressable |

The core tradeoff is upfront investment against long-term alignment. DDD imposes a higher modeling cost early in order to avoid a translation tax paid on every change thereafter. It is most justified when the domain is complex, the business rules are volatile, and the team has access to domain experts who can participate in modeling.

### Domains in Robotics and Autonomous Driving

Robotics and autonomous driving present an especially important case because the domain experts — controls engineers, perception researchers, planning specialists — are often also the implementers. A controls engineer writing a model-predictive controller does not need to explain the physics to a software generalist like in traditional businesses; they are the authority on both the domain and the implementation.

This has two consequences. First, the ubiquitous language comes more naturally: there is no translation gap between business analyst and developer because they are the same person. An engineer who understands vehicle dynamics will name a class `LateralController` without being told to, because that is what it is. Second, and more dangerously, the bounded context discipline is harder to enforce. When the same expert understands perception, planning, and control, they are tempted to build a monolithic model that conflates all three. The physical world is continuous; the software model should not be.

**Subdomains in AD systems** map clearly onto the DDD taxonomy:

The **core domain** is motion planning and decision-making — the algorithms that determine what the vehicle should do in a given scene. This is where differentiation lives. Waymo, Cruise, and Mobileye have different core domains even though they use similar sensors, because their planning approaches differ fundamentally.

The **supporting domain** includes perception pipelines, sensor calibration, and simulation infrastructure. These are specific to the organization's hardware and data, but they support the core rather than being it. A perception model trained on a proprietary dataset is a supporting domain artifact.

The **generic domain** includes OS drivers, communication middleware (ROS 2 is a widely-adopted generic solution), logging, and hardware abstraction. These are industry-wide solved problems and are treated accordingly. Although some companies may implement their own solutions, this does not make it core domain necessarily. To promote it to supporting or core domain, a solution should give company strategic edge over generic solutions, in other words - significant advantage. 

The bounded context discipline is particularly important at the interface between perception and planning. Perception outputs a representation of the world — detected objects, their positions, their classifications. Planning consumes a representation of the world — obstacles, predicted behaviors, drivable space. These are related but not identical models, and the translation between them (the prediction module, in most architectures) is an explicit bounded context interface. Treating it as implicit causes exactly the kind of semantic drift Evans described in enterprise software: a `DetectedVehicle` in perception becomes silently reinterpreted as a `PlanningObstacle` in planning, carrying assumptions that were never stated.

The expert-as-implementer pattern in robotics engineering is an asset when it keeps the ubiquitous language precise and technically grounded. It is a liability when it causes domain boundaries to be ignored because the expert sees through them. The discipline of DDD — explicit bounded contexts, ubiquitous language, domain type classification — is valuable here not despite the technical depth of the team, but because of it.


How
---

**Identify the core domain first.** Before modeling anything, determine what the software does that is genuinely unique. Everything else is supporting or generic. Do not apply the same design depth to all three.

**Establish the ubiquitous language with domain experts.** In a robotics team, this means sitting with controls engineers, perception researchers, and systems architects and agreeing on a glossary. The glossary becomes the naming standard for code. Deviations require justification.

**Draw bounded context boundaries before writing interfaces.** Identify where one model ends and another begins. In an AD system, the perception-to-prediction interface and the prediction-to-planning interface are bounded context boundaries. Define them explicitly, with contracts, before building across them.

**Use context maps to document relationships.** Evans describes several integration patterns between bounded contexts (shared kernel, customer-supplier, anticorruption layer). In AD systems, the anticorruption layer pattern is particularly important: when consuming a third-party perception library or an off-the-shelf map service, wrap it in an adapter that translates the external model into the system's ubiquitous language. Do not let the external terminology leak into the core domain.

**Apply DDD proportionally.** For generic domains, adopt existing solutions and resist the temptation to model them. For supporting domains, apply lightweight modeling. Reserve the full DDD toolkit — aggregates, domain events, repositories, value objects — for the core domain.

**In expert-as-implementer teams, enforce context discipline deliberately.** When the same engineer works across multiple subdomains, establish explicit review gates at bounded context interfaces. The interface contract should be readable by someone who understands only one side of the boundary.

---

#### Age of LLM's and Domain Types

I believe that LLM's are fundamentally can not work well with core domains, although we see success at supporting and generic domains. Many engineers understand this intuitively but let me reason this explicitly.

The three domain types provide a precise framework for understanding where LLM's are useful and where they are not. The argument is not that LLM's are generally weak — it is that they are structurally mismatched with the core domain, for reasons that follow directly from how they are built.
 
**LLM's are trained on the generic and the published.** Large language models are trained on text that exists publicly: documentation, tutorials, Stack Overflow answers, open-source repositories, research papers, and textbooks. This corpus is dense with generic domain knowledge — standard algorithms, common patterns, widely-used frameworks — and contains some supporting domain knowledge in the form of published research. It contains almost no core domain knowledge, because core domain knowledge is by definition proprietary, unpublished, and not written down in a form that ends up in training data. A company's differentiating planning algorithm, its specific approach to edge-case handling, its internally developed domain model — none of this reaches a training corpus. The model is therefore systematically uninformed about exactly the part of the system that matters most.
 
**The averaging effect destroys precision.** Even where core domain knowledge has been partially published — in research papers, conference proceedings, or open-source reference implementations — a general-purpose model learns it averaged across many sources, many interpretations, and many levels of quality. The core domain, by contrast, requires precise and specific knowledge: the exact semantics of a concept as the team has defined it, the exact constraint that applies in this system and not others, the exact tradeoff that was made and why. Averaging across sources does not produce precision; it produces a plausible approximation that looks correct at the surface level and fails at the boundary conditions where core domain logic is actually exercised.
 
**LLM's have no access to the ubiquitous language.** The ubiquitous language of a core domain is developed over time through collaboration between domain experts and engineers. It is specific to one organization's model of one problem. A general LLM model has not participated in that process. It may use the same words — `Trajectory`, `Obstacle`, `PlanningHorizon` — but it does not carry the agreed-upon semantics those words encode within a specific bounded context. Code generated by an LLM model may use the right vocabulary while violating the domain's invariants, because the model learned the words from the literature but not the rules from the team.
 
**LLM's cannot hold bounded context discipline.** A well-designed system enforces explicit boundaries between contexts. An LLM model has no internal equivalent of a bounded context: it is one undifferentiated model that has learned from all domains simultaneously. When asked to reason about a core domain problem, it draws on everything it has seen — including patterns from adjacent domains, generic solutions that do not apply, and similar-looking problems with different constraints. The result is output that conflates contexts in ways that a domain expert would immediately recognize as wrong, but that a less experienced engineer might not catch.
 
**The implication is structural, not a matter of prompting.** These failures cannot be resolved by writing better prompts or providing more context in a conversation. They follow from the fundamental design of current LLM's: domain-agnostic training, statistical pattern matching, no persistent model of a specific system's invariants. The appropriate response is not to avoid LLM's entirely, but to apply them where their strengths align with the domain taxonomy. They are genuinely useful at the generic domain layer — boilerplate, standard patterns, commodity tooling — and useful with oversight at the supporting domain layer, where the organization's specific context can be provided explicitly. At the core domain layer, they are a liability if treated as authoritative, and a weak aid at best when treated as a drafting tool under strict expert review.

**AI-generated core domain code is replicable by any competitor.** The core domain is the source of strategic advantage. Evans is explicit that it is the reason the software exists and the part that cannot be bought. That argument depends on the core domain encoding knowledge that is specific, accumulated, and hard to reproduce. When a core domain is built substantially with an AI model, that assumption breaks down. Any competitor with access to the same model and a similar prompt can produce equivalent code. The moat — the accumulated domain knowledge encoded in the software — is replaced by a capability that is available to everyone equally. This is not a minor concern about code quality; it is a structural erosion of the reason to invest in a core domain at all. Generic domain code is supposed to be replicable — that is why DDD says to buy it rather than build it. With LLM's trick you to think that it is cheaper to build it instead of buying it. Core domain code is supposed to be irreproducible. An AI model inverts this property: it makes core domain code as replicable as generic domain code, while carrying none of the reliability guarantees of a well-maintained open-source library. The result is the worst of both positions — code that is neither differentiated nor dependable.

This maps cleanly onto Vernon's advice about the core domain: it is where the most experienced people should be working, where the most explicit modeling effort should go, and where off-the-shelf solutions are inappropriate. LLM's, for now, are an off-the-shelf solution. They belong at the generic layer.

Sources
-------

- Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley. — The foundational text; source of domain types, ubiquitous language, and bounded context.
- Vernon, V. (2013). *Implementing Domain-Driven Design*. Addison-Wesley. — Practical elaboration of Evans; source of supporting/generic domain classification and context map patterns.
- Vernon, V. (2016). *Domain-Driven Design Distilled*. Addison-Wesley. — Concise reference for core/supporting/generic domain taxonomy.
- Fowler, M. (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley. — Contextual background on layered architecture and why domain modeling emerges as a corrective.
- Newman, S. (2015). *Building Microservices*. O'Reilly Media. — Extends bounded context concept to service boundaries; relevant to AD system decomposition.
- Quigley, J. & Kelly, J. (2018). *A Practical Guide to ROS (Robot Operating System)*. Apress. — Background on ROS 2 as a generic domain solution in robotics.
- Paden, B., Čáp, M., Yong, S. Z., Yershov, D., & Frazzoli, E. (2016). A survey of motion planning and control techniques for self-driving urban vehicles. *IEEE Transactions on Intelligent Vehicles*, 1(1), 33–55. — Provides the subdomain structure of AD systems (perception, prediction, planning, control) that maps onto the DDD taxonomy used in this document.
