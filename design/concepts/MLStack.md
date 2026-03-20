Rules Fail at the Boundary. Models Fail in the Dark.
=====================================================
What
----
This is an article about how to think about ML and rule-based components in robotics software architecture. It is not an argument for one over the other. It is an argument that the choice is a tradeoff with precise consequences — and that conflating "learns from data" with "is better" is one of the more dangerous ideas currently circulating in robotics engineering.

The central claim: **ML does not reduce failure. It changes where failure hides.**

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

The analogy is instructive but breaks in one critical place. The brain is the survivor of a validation process running for hundreds of millions of years, paid for in the lives of every organism whose model was not good enough. Natural selection has no moral standing — physics does not care about failure. It runs the experiment, deletes the failures, and keeps the survivors. Think about all the organisms sacrificed in order to get you to be here.

We do not have that budget, and we do not have that indifference and we cannot afford such failure. When a robotics system fails in a public environment, the cost is not paid by natural selection — it is paid by a specific person who did not consent to be part of the optimization process experiment. The brain does not need to be debuggable because its certification regime was mortality at civilizational scale. That is not a certification regime we can replicate or accept.

This is not an argument against learning. It is an argument that the brain's architecture cannot be justified by appealing to its success alone, because its success was purchased at a too high price that engineering ethics cannot pay.

How
---
### Three Architectures

Robotics systems generally fall into three architectural patterns for combining rules and learned components. Each has a distinct relationship with the rule-vs-model tradeoff.

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

**Where it fails:** The boundary checks must be specified in advance. If the model produces an output that is wrong in a way the boundary check does not anticipate — plausible velocity, plausible clearance, subtly incorrect object classification — the error passes through unchallenged.

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

The argument for this architecture is that the modular pipeline loses information at every interface. A perception module that outputs bounding boxes has already discarded raw sensor information that might have been relevant to planning. An end-to-end model can in principle preserve and use everything.

```python
# End-to-end: raw sensor input → behavior output
# No intermediate representation. No explicit contract. No boundary checks.
action = policy_network(camera_frames, lidar_points, ego_state)
command_actuators(action)
```

There is no rule between the sensor and the actuator. There is no contract to inspect, no intermediate state to audit, no failure boundary to characterize. When it works, it works elegantly. When it fails, you have a bad actuator command and nothing between the input and the output to examine.

**Where it fails:** Everywhere you did not train for, invisibly. The model has learned a compressed representation of the world that is not accessible to the engineer. You cannot ask it why it made a decision. You cannot write a test that covers a specific failure mode you are worried about. You cannot certify it against a formal specification because there is no formal specification — there is a loss function and a dataset.

### On Attempting to Fix Structural Properties

There is a common response to the observability critique of end-to-end and heavily ML-based architectures: companies point to interpretability research, attention visualizations, saliency maps, and uncertainty quantification as evidence that the problem is being worked on. The implication is that effort toward a property is equivalent to having it.

It is not. Attempting to fix a structural shortcoming is not the same as not having it.

A saliency map tells you which input regions the model weighted most heavily for a given decision. It does not tell you whether that reasoning was correct. It does not tell you whether the model will make the same decision under slightly different sensor noise. It does not tell you whether the behavior generalizes beyond the conditions you happened to test. It is a partial, post-hoc, single-decision window into a system that produced thousands of decisions before you looked and will produce thousands more before you look again.

Imagine you are competing in Olympics: a competitor who attempts the jump and does not clear the bar has not cleared the bar. Announcing that you are working hard on clearing it, that you have a research team studying the jump, that your attempts are getting closer — none of this changes the result. The bar is either cleared or it is not. Observability is either a designed property of the architecture or it is not. An unobservable system with an active interpretability research program attached to it is still an unobservable system.

The honest position is to treat current interpretability tooling as what it is: research that may eventually change the calculus, not a present-day substitute for architectural observability. If your safety argument depends on "we are working on making this interpretable," your safety argument is not complete.

### Tradeoff Table

| Dimension | Modular + ML components | Two-stage | End-to-end |
|---|---|---|---|
| **Failure visibility** | High — boundary checks catch violations | Medium — seam failures are silent | Low — no intermediate state to inspect |
| **Debuggability** | High — isolate by module | Medium — isolate by stage | Very low — black box |
| **Certification path** | Feasible — verify modules independently | Partial — stage 2 verifiable, stage 1 statistical | No credible path currently |
| **Handling complexity** | Medium — rules cannot cover all edge cases | Medium — same limitation at stage 2 | High — generalizes across edge cases |
| **Information preservation** | Medium — interfaces are lossy | Low — most information lost at stage 1 output | High — no forced intermediate representation |
| **Safety constraint enforcement** | Strong — explicit rules at boundaries | Weak at seam, strong in stage 2 | None explicit |
| **Development cost** | High — interface design is expensive | Medium | Low initially, very high at failure investigation |
| **Suitable for safety certification** | Yes | Partially | Not currently |

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

---
Rules fail at the boundary. Models fail in the dark. A good architecture knows which failure it can afford.

Sources
-------
- Seshia, S. A., Sadigh, D., & Sastry, S. S. (2018). Formal specification for deep neural networks. *International Symposium on Automated Technology for Verification and Analysis*. — On the difficulty of formally specifying and verifying learned model behavior; basis for certification arguments.
- Paden, B., Čáp, M., Yong, S. Z., Yershov, D., & Frazzoli, E. (2016). A survey of motion planning and control techniques for self-driving urban vehicles. *IEEE Transactions on Intelligent Vehicles*, 1(1), 33–55. — Provides the modular pipeline structure (perception, prediction, planning, control) used as the architectural baseline.
- Bojarski, M., et al. (2016). End to End Learning for Self-Driving Cars. NVIDIA. arXiv:1604.07316. — The canonical end-to-end architecture reference; basis for the end-to-end section.
- Hu, Y., et al. (2023). Planning-oriented Autonomous Driving. *CVPR 2023*. arXiv:2212.10156. — UniAD; representative of modern two-stage architectures that use learned world models as an intermediate representation.
- Amodei, D., et al. (2016). Concrete Problems in AI Safety. arXiv:1606.06565. — Frames specification gaming and distributional shift as structural failure modes of learned systems; supports the "fails in the dark" characterization.
- ISO 26262. (2018). Road Vehicles — Functional Safety. International Organization for Standardization. — The automotive functional safety standard; basis for certification and auditability requirements referenced throughout.
- Leveson, N. (2011). *Engineering a Safer World: Systems Thinking Applied to Safety*. MIT Press. — Foundational text on safety engineering and the relationship between explicit specification and system safety.
