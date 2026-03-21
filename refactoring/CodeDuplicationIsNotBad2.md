Code Duplication Is Not Bad - The Hidden Cost of Tight Coupling
===============================================================
What
----
If you took away one thing from our [previous discussion](dry_abstraction.md), it was that duplication is cheaper than the wrong abstraction. Today, we are going to look at the most dangerous, insidious form of the "wrong abstraction."

**Duplication is FAR cheaper than the tight coupling of unrelated domains.**

Today's topic is about what happens when we let the shape of our code blind us to the actual *meaning* of our code. We are talking about **coincidental duplication**.

Why
---
The holy grail of programming for many developers is **DRY** (Don't Repeat Yourself). When we see two blocks of code that look identical, our fingers itch to extract them into a shared template, base class, or utility function.

But what if I told you that two pieces of code can be physically identical, yet completely unrelated?

Let's look at a C++ example from a robot arm controller. We have two distinct subsystems: `JointController` (low-level servo control) and `SafetyMonitor` (independent fault detection).

```cpp
#include <string>

// --- Domain: Motion Control ---
struct JointState { std::string joint_id; double torque_nm; };
class JointController {
public:
    void applyTorque(const JointState& state) {
        double scaled = applyGearRatio(state.torque_nm);
        Hardware::writeServo(state.joint_id, scaled);
        Logger::info("Torque applied to joint: " + state.joint_id);
    }
};

// --- Domain: Safety ---
struct FaultReading { std::string joint_id; double torque_nm; };
class SafetyMonitor {
public:
    void checkFault(const FaultReading& reading) {
        double scaled = applyGearRatio(reading.torque_nm);
        Hardware::writeServo(reading.joint_id, scaled);
        Logger::info("Fault check on joint: " + reading.joint_id);
    }
};
```

A well-meaning developer reviews this code and their DRY-senses start tingling. "Look at all that duplication!" they say. "Let's use C++ templates to create a unified, generic processor!"

So, they "fix" it:

```cpp
template <typename T>
class GenericJointProcessor {
public:
    void process(const T& item) {
        double scaled = applyGearRatio(item.torque_nm);
        Hardware::writeServo(item.joint_id, scaled);
        Logger::info("Processed joint: " + item.joint_id);
    }
};
```

Ah, beautiful, clean, DRY code. Right?

**Wrong. You just stepped into a massive architectural blunder.**

You have tightly coupled the **Motion Control** domain with the **Safety** domain just because their code *happened to look the same on a Tuesday*.

Fast forward six months. Hardware requirements change — because they always do.

1. The controls team says: *"Joint torque application now needs velocity feedforward compensation."*
2. The safety team says: *"Fault detection must use raw unscaled torque values to avoid masking sensor drift."*

To accommodate these completely separate requirements, your beautiful generic abstraction devolves into a nightmare of `if constexpr` type traits and domain bleeding:

```cpp
#include <type_traits>

template <typename T>
class GenericJointProcessor {
public:
    void process(const T& item) {
        double scaled = 0.0;
        // The horror begins: safety logic bleeding into motion control infrastructure
        if constexpr (std::is_same_v<T, FaultReading>) {
            // Safety must use raw values — do NOT apply gear ratio
            scaled = item.torque_nm;
        } else {
            // Motion control needs feedforward compensation
            scaled = applyGearRatio(item.torque_nm) + computeFeedforward(item);
            Hardware::writeServo(item.joint_id, scaled);
        }
        Logger::info("Processed joint: " + item.joint_id);
    }
};
```

By trying to avoid 3 lines of duplicated code, you have inextricably linked two subsystems that must remain independent by design. A bug introduced by a controls engineer modifying the torque scaling logic could silently corrupt the safety monitor's fault detection. In a robot arm, that is not a code quality issue — it is a safety incident.

This is the exact reason large monolithic systems collapse into unmaintainable spaghetti code. Michael Feathers documented this pattern extensively in [Working Effectively with Legacy Code](https://www.oreilly.com/library/view/working-effectively-with/0131177052/) — the cost of untangling coupled domains grows super-linearly with system size.

### The Ultimate Sin: Coupling Production to Simulation

If coupling two different production domains is bad, there is an even darker path driven by the obsession with DRY: **coupling production to simulation.**

Imagine you have a robust simulation test suite with a factory that creates synthetic sensor readings for unit tests:

```cpp
// --- tests/utils/SimDataFactory.h ---
struct SimDataFactory {
    static IMUReading createDummyIMU() {
        return IMUReading{
            .angular_velocity = {0.0, 0.0, 0.0},
            .linear_acceleration = {0.0, 0.0, 9.81},
            .timestamp_ns = 0,
            .source = DataSource::SIMULATION
        };
    }
};
```

Later, the product team requests a "Safe Mode" for field deployment — a degraded operating mode that runs when primary sensors are unavailable, using a last-known-good IMU estimate. A developer, determined not to duplicate the logic of creating a zeroed IMU reading, does the unthinkable:

```cpp
// --- src/production/SafeModeManager.cpp ---
#include "tests/utils/SimDataFactory.h" // CONGRATULATIONS! You played yourself.

class SafeModeManager {
public:
    IMUReading getFallbackReading() {
        // Production code now depends on simulation infrastructure!
        return SimDataFactory::createDummyIMU();
    }
};
```

Now all hell broke loose. Was it worth it?

**Why is this a disaster?**

1. **Different Lifecycles:** Simulation data is meant to be volatile and tuned per test scenario. If someone updates `createDummyIMU()` to inject artificial noise for a sensor drift test, they just made your production Safe Mode feed corrupted data to the motion planner.
2. **Dependency Bloat:** Your production binary might now link against simulation frameworks, Gazebo stubs, or mocking libraries — inflating binary size, adding attack surface, and potentially violating real-time scheduling budgets.
3. **Violated Boundaries:** Simulation verifies production. Production should not even *know* simulation exists. If your production logic knows about simulation and changes behavior based on execution context, your code behaves differently in the field than it does in testing — and that is a catastrophe on its own.

Simulation environments are a form of test infrastructure. The same firewall applies. Duplicating the 3 lines of code to create a specific `SafeModeFallbackFactory` in production would have been infinitely safer and cheaper than bridging the sacred boundary between `src/` and `tests/`.

How
---
Question of the day: **How do we avoid coupling unrelated domains?**

The answer is learning to differentiate between the *mechanics* of code and the *reason* for the code. Eric Evans calls this distinction foundational in [Domain-Driven Design](https://www.oreilly.com/library/view/domain-driven-design-tackling/0321125215/) — code that looks the same but belongs to different domains should stay separated.

### 1. Coincidental vs. Essential Duplication

Before extracting shared code, ask yourself: *"Do these two pieces of code change for the same business reason?"*

- **Essential Duplication:** Two modules both apply the same kinematic transform to convert joint angles to end-effector pose. If the robot's URDF changes, both must change. You *should* DRY this up into a shared kinematics library.
- **Coincidental Duplication:** The `JointController` and `SafetyMonitor`. They looked the same, but they change for completely different reasons, driven by entirely different engineering constraints. **Leave them separated.**

### 2. Respect Bounded Contexts

A bounded context is a logical boundary around a specific subsystem or domain. Never share business-logic abstractions across bounded contexts. It is perfectly acceptable — even encouraged — to duplicate a struct or a few lines of logic if it means keeping the motion control context physically isolated from the safety context. In safety-critical systems, this isolation is not just good practice — it is often a certification requirement.

### 3. The Copy-Paste Litmus Test

If you are about to create an abstraction, run this mental simulation: if the controls team asks for a radical change to torque scaling, will the safety monitor break because it shares the abstraction?

If the answer is yes, and the two teams work on fundamentally different concerns, you are building a cage, not an abstraction. Copy-paste the code and move on. Your future self — and your safety engineer — will thank you.

---
Sources
-------
- Metz, S. (2014). [All the Little Things](https://www.youtube.com/watch?v=8bZh5LMaSmE). RailsConf 2014. — Source of "duplication is far cheaper than the wrong abstraction."
- Feathers, M. (2004). *Working Effectively with Legacy Code*. Prentice Hall. — Documents the super-linear cost of untangling coupled domains in large systems; supports the spaghetti code argument.
- Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley. — Source of the bounded context concept and the principle that code belonging to different domains should remain separated even when structurally similar.
- Martin, R. C. (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall. — Single Responsibility Principle; foundational to the coincidental vs. essential duplication distinction.
