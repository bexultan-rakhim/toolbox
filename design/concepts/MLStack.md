Deep Stack: Application of ML Models in Robotics System Architecture
====================================================================
What
----
This is an article about how to think about ML and rule-based components in robotics software architecture. It is not an argument for one over the other. It is an argument that the choice is a tradeoff with precise consequences — and that conflating "learns from data" with "is better" is one of the more dangerous ideas currently circulating in robotics engineering.

The central claim: **Rules Fail at the Boundary. Models Fail in the Dark.**

A rule-based system fails loudly at known boundaries. A learned model fails quietly at unknown ones. Neither is safe. They are different failure modes, and choosing between them — or combining them — is an architectural decision with safety implications, not a philosophical stance on the future of AI.

Why
---
### The False Hierarchy

There is a narrative in robotics and autonomous systems that goes roughly like this: rule-based systems are brittle, hand-crafted, and old-fashioned; learned models are flexible, data-driven, and modern. The implication is that replacing rules with models is progress.

This is wrong, and it is worth being precise about why.

A rule-based system encodes explicit knowledge. `if obstacle_distance < 0.5m: emergency_stop()` is a statement about the world that an engineer wrote, a reviewer read, a tester verified, and a certifier signed off on. Its failure mode is also explicit: it does not handle cases outside what the engineer anticipated. When it fails, it fails at a boundary you can find, name, and reason about.

A learned model encodes implicit knowledge extracted from data. It generalizes across cases the engineer never explicitly considered, which is genuinely powerful. But its failure mode is the inverse: it fails in regions of the input space that were underrepresented in training data, and those regions are by definition the ones you did not anticipate. When it fails, it fails in the dark — in conditions you did not know to test for, producing outputs that look plausible and are wrong.

Neither of these is categorically better. They are different contracts with failure.

### What Rules Are Good At

Rule-based components encode hard constraints. In robotics, hard constraints exist. A joint has a physical range of motion. A vehicle has a maximum safe deceleration. A manipulator arm must not enter a defined exclusion zone regardless of what the planner requests. These are not probabilistic — they are invariants, and they should be enforced as invariants.

Rules are also auditable. You can read them, trace their logic, unit test them exhaustively, and formally verify bounded subsets of them. In safety-critical systems, auditability is not a nice-to-have. It is the mechanism by which you make a credible argument to a regulator, a customer, or yourself that the system behaves correctly. A rule that says `assert velocity < MAX_VELOCITY` is a contract you can point to. A neural network that has learned to generally respect velocity limits is a statistical tendency you cannot point to.

Rules fail predictably. A rule that does not cover a case will either trigger a default, raise an error, or produce an obviously wrong output. Failure is visible. This is the property that makes rule-based systems debuggable — and debuggability, as any engineer who has chased a non-deterministic fault knows, is not a luxury.

### What Models Are Good At

Rules cannot scale to the complexity of the real world. Writing explicit rules for every lighting condition, every sensor noise profile, every unexpected object geometry, every edge case in human behavior — this is not engineering, it is an infinite regress. The real world is continuous and high-dimensional. Rules are discrete and low-dimensional. At some point, the gap cannot be closed by writing more rules.

This is where learned models earn their place. Perception is the canonical example. Writing rules to detect a pedestrian from a point cloud in rain, at night, partially occluded by a parked van, is not feasible. Training a model on sufficient examples of exactly this condition is. The model generalizes in ways no rule system could.

Models are also better at handling graceful degradation across a continuous spectrum of input quality. A rule either fires or it does not. A model can produce a confidence-weighted output that downstream components can act on proportionally. This is valuable when the world does not cooperate with binary conditions.

### The Brain Argument

End-to-end proponents sometimes invoke biological intelligence as justification: the human brain is a unified learned model with no interpretability layer, and it navigates the world successfully. Why should a robot be different?

The analogy is instructive but breaks in one critical place. The brain is the survivor of a validation process running for hundreds of millions of years, paid for in the lives of every organism whose model was not good enough. Natural selection has no moral standing — physics does not care about failure. It runs the experiment, deletes the failures, and keeps the survivors.

We do not have that budget, and we do not have that indifference. When a robotics system fails in a public environment, the cost is not paid by natural selection — it is paid by a specific person who did not consent to be part of the optimization process. The brain does not need to be debuggable because its certification regime was mortality at civilizational scale. That is not a certification regime we can replicate or accept.

This is not an argument against learning. It is an argument that the brain's architecture cannot be justified by appealing to its success alone, because its success was purchased at a price that engineering ethics cannot pay.

How
---
### Three Architectures

Robotics systems generally fall into three architectural patterns for combining rules and learned components. Each has a distinct relationship with the rule-vs-model tradeoff.

A note before going further: no real production system is purely one of these. Every deployed robotics system is a combination — learned models wrapped in rule-based safety layers, classical planners consuming ML-produced world representations, end-to-end policies with hard-coded override logic on top. These are archetypes for thinking about tradeoffs, not a taxonomy of things that exist in the wild.

#### 1. Modular Architecture with ML Components

The system is decomposed into well-defined modules — perception, prediction, planning, control — with explicit interfaces between them. Some modules are rule-based; others are ML-based. The key property is that the interfaces are explicit contracts, and safety constraints are enforced at module boundaries by rule-based checks.

A typical pattern: a learned perception model produces detections with confidence scores; a rule-based filter enforces minimum confidence thresholds before passing objects to planning; a learned prediction model generates trajectory hypotheses; a rule-based safety layer vetoes any planned trajectory that violates hard constraints before commanding the actuators.

```rust
// Boundary check: rules enforce invariants at the interface
// between learned prediction and rule-based planning
fn validate_predicted_trajectory(traj: &Trajectory) -> Result<(), SafetyViolation> {
    assert!(traj.max_velocity() <= MAX_SAFE_VELOCITY,
        "Predicted trajectory exceeds velocity envelope");
    assert!(traj.min_clearance() >= MIN_OBSTACLE_CLEARANCE,
        "Predicted trajectory violates clearance constraint");
    Ok(())
}
```

The rule-based boundary checks are the system's immune system. They do not need to understand how the model works. They enforce the contract that any output, regardless of how it was produced, must satisfy before it is acted upon.

**Where it fails:** The boundary checks must be specified in advance. If the model produces an output that is wrong in a way the boundary check does not anticipate — plausible velocity, plausible clearance, subtly incorrect object classification — the error passes through unchallenged. And rules are not immune to bugs. A rule that was written incorrectly, or that does not cover a case the engineer did not anticipate, fails just as silently as a model. The difference is that rule failures are easier to find and reason about after the fact — not that they do not exist.

#### 2. Two-Stage Architecture

The system separates world understanding from behavior generation. Stage one — typically ML-heavy — builds a structured representation of the world: a semantic map, an object list with predicted states, a drivable space estimate. Stage two — typically more rule-based or classical — generates behavior from that representation.

This is the dominant architecture in production autonomous driving systems. The appeal is that the two stages have different validation requirements: stage one is validated statistically against ground truth labels; stage two is validated against formal behavioral specifications. You can argue about each independently.

The weakness is the interface between stages. Stage one produces a world representation; stage two consumes it. If the representation is wrong in a subtle way — a misclassified object type, a slightly incorrect velocity estimate, a missed detection with low confidence — stage two will produce behavior that is locally rational given the representation and globally wrong given the world. The error is invisible to stage two because stage two trusts the representation.

```cpp
// Stage 1 output: world representation from ML perception + prediction
struct WorldModel {
    std::vector<TrackedObject> objects;  // ML-estimated states
    OccupancyGrid drivable_space;        // ML-segmented
    EgoState ego;                        // sensor-fused
};

// Stage 2: rule-based + classical planning consuming the representation
// If WorldModel is subtly wrong, this produces subtly wrong behavior.
// There is no second check.
Trajectory plan(const WorldModel& world, const Goal& goal) {
    return rrt_star(world.drivable_space, world.objects, ego, goal);
}
```

**Where it fails:** Silently, at the seam. The most dangerous failure mode is a world model that is confident and wrong — the model did not output a low confidence score, so no alarm raised, and planning proceeds from false premises.

#### 3. End-to-End Architecture
 
A single learned model — or a tightly coupled set of learned models — takes raw sensor input and outputs behavior directly, with no explicit intermediate representation. The model learns whatever internal structure is useful; the engineer does not specify it.
 
The argument for this architecture is genuine and should not be dismissed. The modular pipeline loses information at every interface — a perception module that outputs bounding boxes has already discarded raw sensor data that might have been relevant to planning. An end-to-end model preserves that information and jointly optimizes across what modular systems solve sequentially. In practice, well-trained end-to-end models have demonstrated behavior that is probabilistically reliable across a wide range of conditions — not deterministically guaranteed, but statistically compelling in ways that matter. Waymo's EMMA (2024), built on a multimodal LLM foundation, achieved state-of-the-art motion planning on nuScenes while jointly handling perception and road graph tasks — with measured improvements across all three domains when co-trained, something modular systems structurally cannot do. UniAD (CVPR 2023 Best Paper) demonstrated that planning-oriented end-to-end training, where gradients flow back through perception during training, produces measurably better planning outcomes than training stages independently. Trajectory prediction error on that line of work dropped from 1.03m L2 in 2022 to 0.22m by late 2024 — a roughly 5x improvement driven largely by end-to-end training methodology, not hardware.
 
```python
# End-to-end: raw sensor input → behavior output
# No intermediate representation. No explicit contract. No boundary checks.
action = policy_network(camera_frames, lidar_points, ego_state)
command_actuators(action)
```
 
Reliability can also be argued probabilistically. Ablation studies — systematically degrading inputs or perturbing conditions and observing how behavior changes — provide a form of behavioral characterization even without interpretability. You cannot audit a single decision, but you can build a statistical profile of how the model behaves across a distribution of conditions, including reconstructed versions of failure scenarios. This is not the same as deterministic certification, but it is not nothing either.

No practical system is truly end-to-end. Reason is that you still need to put safety checks at the output of the model. It can be even a redundant system that is more conservative, for example and safety case is made that if model output disagrees with redundant system, then be at alarm.
 
The honest tradeoff is this: end-to-end models trade auditability and certifiability for expressiveness and information preservation. That tradeoff may be acceptable in contexts where statistical performance across a wide distribution is the primary requirement and formal certification is not. It is not acceptable where a regulator requires a traceable safety argument, or where a failure investigation needs to isolate cause.
 
**Where it fails:** In conditions underrepresented in training, without warning. The model has no mechanism to signal that it is operating outside its reliable envelope. A rule-based system that encounters an unhandled case produces a visible error. An end-to-end model produces a confident output. Whether that output is correct is a function of training coverage, not of anything the model communicates at inference time.

### On Attempting to Fix Structural Properties
 
There is a common response to the observability critique of end-to-end and heavily ML-based architectures: companies point to interpretability research, attention visualizations, saliency maps, and uncertainty quantification as evidence that the problem is being worked on. The implication is that effort toward a property is equivalent to having it.
 
It is not. Attempting to fix a structural shortcoming is not the same as not having it.
 
To be fair: mechanistic interpretability as a field has matured significantly since the saliency map era. Anthropic, DeepMind, and academic groups have produced work on circuit analysis, sparse autoencoders, and attribution graphs that goes meaningfully beyond "which pixels did the model look at." Anthropic's circuit-tracing tools, open-sourced in 2025, have been applied to production models. DeepMind's Gemma Scope has scaled sparse autoencoder analysis to 27B parameters. This is real progress, and it would be dishonest to dismiss it.
 
But there is a critical distinction between interpretability as a research program and observability as an architectural property. A saliency map or attribution graph tells you something about one decision, analyzed after the fact, under controlled conditions, by a researcher with significant tooling investment. An observable architecture gives you a traceable audit trail for every decision, at inference time, without a research team. These are not the same thing, and conflating them is the error. As the field itself acknowledges, SAE-reconstructed activations currently cause 10–40% performance degradation on downstream tasks — interpretability tools are still imposing significant costs on the models they analyze. The gap between "we can sometimes understand why a model made a specific decision" and "we can certify this model's behavior against a formal specification" remains wide.
 
This is the olympics analogy applied to engineering: a competitor who attempts the jump and does not clear the bar has not cleared the bar. Announcing that you are working hard on clearing it, that you have a research team studying the jump, that your attempts are getting closer — none of this changes the result. The bar is either cleared or it is not. Observability is either a designed property of the architecture or it is not. An unobservable system with an active interpretability research program is still an unobservable system today.
 
The honest position is to treat current interpretability tooling as what it is: research that is advancing and may eventually change the calculus, not a present-day substitute for architectural observability. If your safety argument depends on "we are working on making this interpretable," your safety argument is not complete.

### Cost Profile

Implementation cost is one of the most misunderstood dimensions of this decision. End-to-end architectures look cheap at the start and become expensive in ways that are hard to budget for. Modular architectures look expensive at the start and become cheaper to maintain over time. Neither is free — the cost is just distributed differently across the project lifecycle.

**Initial implementation cost.** A modular architecture requires significant upfront investment in interface design. Before writing a line of ML code, you need to define what perception hands to prediction, what prediction hands to planning, and what contracts those interfaces enforce. This is hard, slow work that does not produce visible features. End-to-end architectures sidestep this entirely — the interface is implicit, learned by the model, and the engineer never has to specify it. This makes end-to-end look dramatically cheaper at project kickoff. It is a deferral, not a saving.

**Data cost.** End-to-end models are data-hungry in ways that are easy to underestimate at the start. Because the model must jointly learn perception, prediction, and behavior from raw sensor input, it requires coverage across the full combination of conditions — not just each condition independently. Edge cases that a modular system could handle by fixing one component require full end-to-end retraining with new data covering that case. Modular architectures allow targeted dataset collection: if perception degrades in rain, you collect rain data and retrain the perception module. The scope of data collection is bounded by the module boundary.

**Maintenance cost.** In a modular architecture, components can be updated, replaced, or retrained independently. Improving the prediction model does not require touching the planner. Fixing a boundary check does not require retraining anything. In an end-to-end architecture, the model is monolithic — changing behavior in one aspect of the task requires retraining the whole model, with the risk of degrading performance on aspects you were not trying to change. This is the catastrophic forgetting problem, and it makes maintenance of end-to-end systems significantly more expensive over time than initial development suggests.

**Failure investigation cost.** This is the cost that end-to-end architectures defer most aggressively and that modular architectures pay upfront through interface discipline. When a modular system fails, you have a structured search space: which module produced the bad output, which boundary check did not catch it, which invariant was violated. When an end-to-end system fails, you have a bad output and an opaque model. Reproducing the failure requires reconstructing the exact input conditions. Ablation testing can characterize behavior statistically, but isolating the cause of a specific failure is expensive and often inconclusive. In safety-critical systems, failure investigation is not optional — it is how you determine whether the system is safe to redeploy. The cost of this investigation should be in your budget from day one.

**Certification cost.** Modular architectures have a known certification path under standards like ISO 26262 and the more recent ISO 21448 (SOTIF — Safety of the Intended Functionality, 2022), which specifically addresses safety hazards arising from ML-based perception limitations rather than hardware failures. Expensive, but bounded and methodology-exists. End-to-end architectures currently have no established certification path. ISO PAS 8800:2024 (Safety and Artificial Intelligence) is an emerging standard that acknowledges the problem, but the methodology for certifying a fully learned model against a formal safety specification does not yet exist in practice. The cost is not just high — it is unbounded. Organizations pursuing end-to-end architectures in safety-critical domains are implicitly betting that a certification path will be established before they need one. That is a program risk, not just a technical one.

### Tradeoff Table

| Dimension | Modular + ML components | Two-stage | End-to-end |
|---|---|---|---|
| **Failure visibility** | High — boundary checks catch known violations | Medium — seam failures are silent | Low — no intermediate state to inspect |
| **Debuggability** | High — isolate by module | Medium — isolate by stage | Low — ablation studies provide partial behavioral characterization |
| **Rule correctness** | Rules can be wrong too — but failures are traceable | Same — stage 2 rules are auditable, stage 1 is not | N/A — no explicit rules |
| **Certification path** | Feasible — verify modules independently | Partial — stage 2 verifiable, stage 1 statistical | No deterministic path; probabilistic arguments possible |
| **Handling complexity** | Medium — rules cannot cover all edge cases | Medium — same limitation at stage 2 | High — jointly optimizes across full input space |
| **Information preservation** | Medium — interfaces are lossy by design | Low — significant information lost at stage 1 output | High — no forced intermediate representation |
| **Statistical reliability** | Depends on ML component quality | Depends on world model quality | Can be high with sufficient training coverage |
| **Safety constraint enforcement** | Strong — explicit rules at boundaries | Weak at seam, strong in stage 2 | None explicit — requires external safety layer |
| **Initial implementation cost** | High — interface design is expensive upfront | Medium | Low — deceptively cheap to start |
| **Data cost** | Targeted — retrain affected module only | Medium — stage 1 data-hungry, stage 2 bounded | High — full condition coverage required; edge cases are expensive |
| **Maintenance cost** | Low — components updated independently | Medium — stage 1 retraining affects stage 2 inputs | High — monolithic retraining risk; catastrophic forgetting |
| **Failure investigation cost** | Low — structured search space | Medium — seam failures harder to isolate | Very high — opaque model, expensive to reproduce and isolate |
| **Certification cost** | High but bounded — established methodology exists | Partial — stage 2 bounded, stage 1 open | Unbounded — no established methodology currently |

### Choosing the Right Mix

The right architecture is not a universal answer — it depends on where in the system you are and what the failure modes cost.

**Use rule-based enforcement wherever the constraint is hard.** Velocity limits, joint ranges, exclusion zones, emergency stops — these are invariants. They should be encoded as invariants, not learned. A model that has statistically learned to respect a joint limit is not the same as a constraint that enforces it. One is a tendency; the other is a guarantee.

**Use ML where the input space is too complex for rules.** Raw sensor interpretation — detecting objects, estimating states, segmenting scenes — is where learned models have a genuine advantage that rules cannot replicate. Accept this. Put the ML here.

**Enforce rules at every boundary between ML components.** Every time a learned model hands off to another component, there should be a rule-based check that validates the output against known constraints before it propagates. This does not catch every failure. It catches failures that violate known invariants, which is exactly the class of failure that is most dangerous because it looks locally plausible.

**Be honest about what end-to-end cannot give you.** If your system must be auditable, certifiable, or explainable to a regulator or to yourself after a failure, end-to-end is the wrong architecture for the safety-critical path. Use it for research. Use it to discover what information matters. Do not use it as a production architecture in a system where failure has physical consequences and you need to understand why.

```rust
// The pattern that survives contact with reality:
// ML where complexity demands it, rules where invariants demand it,
// explicit contracts at every boundary.

let raw_detections = perception_model.infer(&sensor_data);       // ML
let validated = boundary_check(raw_detections)?;                  // Rule
let predictions = prediction_model.infer(&validated);             // ML
let safe_predictions = safety_filter(predictions)?;               // Rule
let trajectory = planner.plan(&safe_predictions, &goal);          // Classical
let command = safety_layer.validate(trajectory)?;                 // Rule
actuators.command(command);
```

Each `?` is a hard stop. If a rule fires, execution does not continue. The ML components handle complexity. The rule-based components hold the contracts. Neither pretends to do the other's job.

We are seeing this happen in coding agents with tool use: they can validate their output by compiling code and reading the compiler errors.

---
Not every architecture needs to be end-to-end. A good architecture knows which failure it can afford.

Sources
-------
- Bojarski, M., et al. (2016). End to End Learning for Self-Driving Cars. NVIDIA. arXiv:1604.07316. — The original end-to-end AD architecture reference; historical baseline.
- Hu, Y., et al. (2023). Planning-oriented Autonomous Driving (UniAD). *CVPR 2023 Best Paper*. arXiv:2212.10156. — Representative two-stage end-to-end architecture; source of trajectory error improvement figures cited in the end-to-end section.
- Hwang, J-J., et al. (2024). EMMA: End-to-End Multimodal Model for Autonomous Driving. Waymo. arXiv:2410.23262. — Waymo's multimodal LLM-based end-to-end architecture; demonstrates state-of-the-art motion planning and positive cross-task transfer; source of co-training performance claims.
- Paden, B., Čáp, M., Yong, S. Z., Yershov, D., & Frazzoli, E. (2016). A survey of motion planning and control techniques for self-driving urban vehicles. *IEEE Transactions on Intelligent Vehicles*, 1(1), 33–55. — Provides the modular pipeline structure used as the architectural baseline.
- Seshia, S. A., Sadigh, D., & Sastry, S. S. (2018). Formal specification for deep neural networks. *ATVA 2018*. — On the difficulty of formally specifying and verifying learned model behavior.
- Amodei, D., et al. (2016). Concrete Problems in AI Safety. arXiv:1606.06565. — Frames distributional shift as a structural failure mode of learned systems; supports the "fails in the dark" characterization.
- ISO 26262. (2018). Road Vehicles — Functional Safety. International Organization for Standardization. — Automotive functional safety standard; basis for modular certification arguments.
- ISO 21448. (2022). Road Vehicles — Safety of the Intended Functionality (SOTIF). International Organization for Standardization. — Addresses safety hazards from ML-based perception limitations specifically; extends ISO 26262 to cover correct-but-insufficient system behavior.
- ISO PAS 8800. (2024). Road Vehicles — Safety and Artificial Intelligence. International Organization for Standardization. — Emerging standard for AI safety in automotive systems; acknowledges the certification gap for learned models.
- Bereska, L. & Ebrahimi Kahou, S. (2024). Mechanistic Interpretability for AI Safety — A Review. arXiv:2404.14082. — Comprehensive review of mechanistic interpretability methodology and its relevance to safety; source of framing around circuit analysis, sparse autoencoders, and the gap between interpretability research and production observability.
- IntuitionLabs. (2025). Mechanistic Interpretability in AI Models. — Source of SAE performance degradation figures (10–40% on downstream tasks) and summary of 2025 progress including Anthropic attribution graphs and Gemma Scope scaling results.
- Leveson, N. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press. — Foundational text on safety engineering and explicit specification requirements.
