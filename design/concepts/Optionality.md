Architectural Optionality in Robotics Systems
==============================================

In options trading, you pay a small premium today to keep a decision open tomorrow. You are not committing to the trade — you are buying the right to act once uncertainty resolves. Architectural optionality works the same way. The structures you put in place now are not about solving today's problem; they are about preserving your right to change your mind later without paying a catastrophic rewrite cost. Then the analogy ends, and the engineering begins.

What
----

Architectural optionality is the property of a system that can absorb change in one area without cascading rewrites elsewhere. In robotics, that means a new sensor, a new planning algorithm, or a new target platform does not require touching code that has nothing to do with that change.

The operative word is *absorb*. The change lands, the boundary contains it, the rest of the system does not notice.

For embedded and bare-metal robotics systems, recompiling the full stack is cheap — CMake + Ninja or Bazel can turn a million-line codebase around in minutes. That is a feature, not a constraint. It means flexibility lives at compile time, not runtime. Virtual dispatch, heap allocation, and deep call chains are not optionality — they are indirection debt. The right tools are templates, concepts, `std::variant`, and `constexpr`. The compiler resolves everything; the engineer reads the execution model directly from the source.

Why
---

Robotics hardware has a short and brutal product lifecycle. The IMU you designed around gets end-of-lifed. The motor driver available last quarter is now backordered, and procurement found a compatible alternative with a different SPI register map. If your firmware reached directly into vendor SDK calls at every layer, that is a three-week porting effort. If it called a typed, compile-time-bound interface, it is a day and a recompile.

Algorithm churn is equally relentless. MPPI has displaced many classical planners for outdoor mobile robots. New localization approaches emerge every conference cycle. A codebase that hardcodes a specific algorithm cannot experiment. In robotics, running controlled comparisons between algorithm variants without restructuring the codebase is the difference between a team that ships and one that rewrites.

The deeper problem with runtime polymorphism is cognitive. Virtual dispatch means the engineer reading the code cannot statically determine which implementation executes. On a system where timing guarantees matter and debugging tools are limited, that indirection is a liability. Compile-time binding means what you read is what runs.

How
---

### 1. Data & State Optionality

**Event Sourcing.** Instead of storing current robot state, store the append-only log of every event that produced it — every encoder tick, every sensor reading, every command issued. The pattern was introduced by Martin Fowler in ["Event Sourcing"](https://martinfowler.com/eaaDev/EventSourcing.html) (2005), where he established that stored events can be replayed to reconstruct any past state. The optionality: when you deploy a new localization algorithm, you replay the log through it rather than re-driving every test route. The raw sensor stream is the source of truth; derived state is always recomputable. MCAP is the production-grade format for this in robotics, used across several autonomous vehicle stacks.

**CQRS (Command Query Responsibility Segregation).** Split the path that writes robot state from the path that reads it. The pattern was coined by Greg Young and documented by Martin Fowler in ["CQRS"](https://martinfowler.com/bliki/CQRS.html) on his bliki. A fleet management system that writes mission commands and the analytics dashboard that reads telemetry history have different consistency and latency requirements. Separating them lets each be optimized independently — a time-series store for queries, a strongly consistent store for commands — without either compromising the other.

**Change Data Capture (CDC).** Stream every state change from your primary robot database to downstream consumers — ML training pipelines, digital twins, monitoring dashboards — without polling or modifying application code. [Debezium](https://debezium.io/), an open-source CDC platform founded by Randall Hauch at Red Hat in 2016, monitors the transaction log directly. Adding a new consumer requires zero changes to the robot firmware or fleet software.

### 2. Code-Level & Domain Optionality

**Dependency Injection / Inversion of Control.** Components receive their dependencies from the outside rather than constructing them internally. The pattern was formalized by Martin Fowler in ["Inversion of Control Containers and the Dependency Injection Pattern"](https://martinfowler.com/articles/injection.html) (January 2004). In embedded C++, this means template parameters and constructor injection rather than a DI framework. The optionality: inject a `MockImu` in tests that returns deterministic readings without touching hardware, and inject the real `Bmi088` in production. Same code path, verified at compile time via Concepts.

```cpp
template<ImuDriver Imu>
class MadgwickFilter {
    Imu& imu_;
public:
    explicit MadgwickFilter(Imu& imu) : imu_(imu) {}
    Quaternion update();
};

// Production
Bmi088 imu{};
MadgwickFilter<Bmi088> filter{imu};

// Test — no hardware needed
MockImu mock{preloaded_readings};
MadgwickFilter<MockImu> filter{mock};
```

**Strategy Pattern.** A family of algorithms, each encapsulated (more examples [here](../patterns/Strategy/)), selectable without changing the calling code. First described in *Design Patterns: Elements of Reusable Object-Oriented Software* (Gamma, Helm, Johnson, Vlissides, 1994) — the "Gang of Four" book that catalogued 23 foundational object-oriented patterns. In robotics: swap between a PID and an MPC controller, or between MPPI and TEB planners, as a build-time choice rather than a structural rewrite. `std::variant` + `std::visit` gives you this with zero heap allocation and a closed type set the compiler can fully reason about.

```cpp
using Controller = std::variant<PidController, AdaptiveMpcController>;

Torque run_controller(Controller& c, const StateError& e, float dt) {
    return std::visit([&](auto& ctrl) {
        return ctrl.compute(e, dt);
    }, c);
}
```

**Anti-Corruption Layer (ACL).** When integrating with a legacy vendor SDK, a poorly-designed third-party sensor API, or an inherited firmware module, build a thin translation layer between their interface and your clean domain types. The pattern originates with Eric Evans in *Domain-Driven Design: Tackling Complexity in the Heart of Software* (2003), where it is described as an isolating layer that prevents external semantics from corrupting an internal domain model. The optionality: when the vendor changes their API or you replace the sensor, you rewrite the translation layer only. The rest of your codebase never knew the vendor existed.

```cpp
// Vendor SDK speaks its own types
VendorImuData raw = vendor_sdk_read();

// ACL translates at the boundary — your domain never sees VendorImuData
ImuReading to_domain(const VendorImuData& raw) {
    return { .accel = { raw.ax * kVendorScale, raw.ay * kVendorScale, raw.az * kVendorScale },
             .gyro  = { raw.gx, raw.gy, raw.gz } };
}
```

### 3. Infrastructure & Deployment Optionality

**Containerization & Orchestration.** Package your robot software stack and its OS dependencies into a Docker image. The optionality: the same image runs on a developer's workstation, in a Gazebo or Isaac Sim loop, and on the production compute board — without diverging codebases. For ARM targets like the Jetson or a Raspberry Pi, multi-arch builds with `buildx` cover cross-compilation without a separate toolchain setup per machine.

**Infrastructure as Code (IaC).** Define your fleet management servers, message brokers, and telemetry infrastructure in Terraform or Pulumi rather than clicking through cloud consoles. The optionality: spinning up an identical staging environment for a new robot variant takes minutes. Rolling back a broken infrastructure change is a Git revert, not a guesswork restore.

### 4. Evolution Optionality

**Consumer-Driven Contract Testing.** Each service that consumes a robot API defines the exact shape of data it expects; those contracts run against the provider's CI pipeline. The pattern was introduced by Ian Robinson in ["Consumer-Driven Contracts: A Service Evolution Pattern"](https://martinfowler.com/articles/consumerDrivenContracts.html) (2006), published on martinfowler.com, and operationalized by the [Pact](https://docs.pact.io/) framework (created 2013). The optionality: when you refactor a sensor driver's message format or deprecate a telemetry field, the build tells you immediately which consumers break — before anything ships to the fleet. It eliminates the fear of evolving interfaces that downstream teams depend on.

**Expand/Contract Pattern (Parallel Change).** When a robot's telemetry schema needs to evolve — renaming a field in the MCAP log format, splitting a combined `ImuReading` struct into separate `AccelReading` and `GyroReading` messages — a direct rename breaks every consumer simultaneously. The expand/contract pattern sequences the migration: expand (add the new field alongside the old, write both), transition (shift all readers to the new field), contract (drop the old field and its write path). Described by Martin Fowler as [Parallel Change](https://martinfowler.com/bliki/ParallelChange.html) and elaborated in *Refactoring* (2nd ed.). The optionality: you decouple schema migrations from firmware deployments. A fleet running mixed firmware versions — some still writing the old field, some writing the new — coexists safely during the transition window without a coordinated cutover.

**API Versioning (URI, Headers, or Content Negotiation).** A robot fleet exposes HTTP or gRPC interfaces to mission planners, dashboards, and third-party logistics integrations. Designing those interfaces with explicit versioning from the start — `/api/v1/mission` and `/api/v2/mission` coexisting, or version negotiation via `Accept` headers — means a breaking change does not become a forced synchronous migration across every client. Documented extensively in the [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines) and Roy Fielding's original REST constraints from his 2000 doctoral dissertation, *Architectural Styles and the Design of Network-based Software Architectures*. The optionality: you gain the right to introduce structural changes for new integrations while giving existing clients a controlled deprecation window. In a fleet where edge compute, cloud backend, and third-party systems update on independent release cycles, that decoupling is operational safety, not a convenience.

**Schema Registries.** In event-driven robotics architectures — Kafka-backed telemetry pipelines, ROS 2 DDS middleware, or fleet management buses — every producer and consumer holds an implicit contract about message shape. A schema registry (Confluent Schema Registry for Kafka; analogous type enforcement for ROS 2 `.msg` definitions) makes that contract explicit and enforces compatibility rules: backward, forward, or full. The design is documented in the [Confluent Platform documentation](https://docs.confluent.io/platform/current/schema-registry/index.html) and the broader Apache Avro specification. The optionality: robot firmware can add new fields to a telemetry message without breaking a cloud consumer that has not yet been updated to handle them. ML training pipelines, digital twins, and monitoring dashboards each evolve at their own pace. The registry is the boundary that prevents a malformed payload from propagating a crash across the entire pipeline.

### The Cost of Options

Optionality is not free. Every pattern above carries a premium that must be weighed honestly.

| Pattern                    | What you pay                                      | When it's worth it                                    |
|----------------------------|---------------------------------------------------|-------------------------------------------------------|
| Template abstraction       | Binary size growth, longer compile times          | Hardware or algorithm with 2+ real swap candidates    |
| `std::variant`             | Visitor boilerplate, closed type set              | Fixed set of strategies known at design time          |
| `constexpr` config         | Type system complexity                            | Per-variant hardware fixed at build time              |
| Event sourcing / MCAP logs | Storage cost, replay infrastructure               | Any system that does post-mortem analysis or retrains |
| CQRS                       | Two data paths to maintain                        | Read and write loads have genuinely different shapes  |
| CDC                        | Broker infrastructure, ops knowledge              | Multiple consumers need the same state changes        |
| ACL                        | Translation code to maintain                      | Vendor API is unstable or likely to be replaced       |
| Containerization           | Image build complexity, cross-compile setup       | Stack runs in more than one environment               |
| IaC                        | Upfront authoring cost                            | Infrastructure is replicated or frequently changed    |
| Contract testing           | Test infrastructure, contract maintenance         | Multiple teams consuming shared interfaces            |
| Expand/Contract            | Migration coordination, dual-write period         | Schema change with consumers on independent release cycles |
| API versioning             | Multiple versions to maintain simultaneously      | External or cross-team consumers with independent release cycles |
| Schema registry            | Registry infrastructure, schema authoring discipline | Event-driven architecture with multiple producers or consumers |

The heuristic runs through all of them: if you can name two concrete implementations, integrations, or environments today that you will need to support, the abstraction pays for itself. If you are building the interface on speculation alone, you are paying a complexity premium you will almost certainly never redeem. The CUPID **Unix philosophy** applies — each component does one thing well, and optionality is added where the abstracted thing actually changes. Do not abstract your coordinate frame arithmetic. After all, ["All problems in computer science can be solved by another level of indirection, except for the problem of too many layers of indirection"."](https://en.wikipedia.org/wiki/Fundamental_theorem_of_software_engineering) - David Wheeler.
