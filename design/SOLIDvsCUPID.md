SOLID? NO - CUPID!
==================

What
----

This is an article on why you should prefer CUPID over SOLID principles.

If you take anything from this article, let it be this: **For automation, a system that fails gracefully is worth more than a system that is easy to extend.**

Today's topic is CUPID---a set of properties for good code proposed by Dan North---and why it fits real-world engineering, especially in robotics, better than the more famous SOLID principles. This is not about dismissing SOLID entirely. It is about recognizing that SOLID was born from enterprise software, not from systems where a bug can stop a factory line or crash a robot arm.

Why
---

SOLID is the dominant mental model taught in software engineering. It gives you five principles:

-   **S**ingle Responsibility - a class should do one thing

-   **O**pen/Closed - open for extension, closed for modification

-   **L**iskov Substitution - subtypes must be substitutable for their base types

-   **I**nterface Segregation - keep interfaces narrow

-   **D**ependency Inversion - depend on abstractions, not concretions

These are not bad ideas. But there is a hidden cost, particularly with the **Open/Closed** principle. OCP encourages inheritance and polymorphism as the mechanism for extension. You close a class for modification by opening it for inheritance. And this is where the trouble begins.

### OCP - The Indirection Problem

Imagine you have a motor controller class. Following OCP, you build a `BaseMotorController`, then extend it into `StepperMotorController`, `BrushlessMotorController`, and `ServoController`. Each one overrides virtual methods. Each one might override methods from a class that itself extends something.

Now your robot fails at 3am on the production floor. You look at the stack trace. You see: `MotorController.execute() -> BaseController.execute() -> AbstractActuator.dispatch() -> ???`

Which `execute` ran? What was the concrete type at runtime? How many layers of override are between you and the actual behavior? You have to trace the entire inheritance tree to understand what the system actually did. This is not a theoretical concern. In automation, debuggability is a safety property. **A system you cannot understand under pressure is a system you cannot fix under pressure.**

### Liskov Substitution Principle

LSP is the most academically stated of the five principles, and I bet no one actually applies it correctly. It is quite theoretical stuff.

The formal definition is: if *S* is a subtype of *T*, then objects of type *T* may be replaced with objects of type *S* without breaking the program's correctness.

This sounds reasonable until you try to apply it to real code. The failure mode is subtle. You define a base class that makes implicit behavioral promises---not just in its method signatures, but in its *contracts*: what preconditions must hold, what postconditions are guaranteed, what invariants are maintained. A subclass that violates any of those contracts is an LSP violation, even if it compiles perfectly.

Consider the classic example:

```python
class Rectangle:
    def set_width(self, w): self.width = w
    def set_height(self, h): self.height = h
    def area(self): return self.width * self.height

class Square(Rectangle):
    def set_width(self, w):
        self.width = w
        self.height = w   # A square must keep sides equal
    def set_height(self, h):
        self.width = h
        self.height = h

```

A `Square` is mathematically a `Rectangle`. But if any code does this:

```python
def stretch(shape: Rectangle):
    shape.set_width(10)
    shape.set_height(5)
    assert shape.area() == 50  # Fails silently if shape is a Square

```

You have an LSP violation the compiler cannot catch, the type system cannot catch, and that surfaces only at runtime---possibly inside a physical system. The problem is that the behavioral contract of `Rectangle` (width and height are independent) was never written down. It was assumed. And assumptions in inheritance hierarchies become landmines.

The real issue is that LSP requires you to formally specify behavioral contracts, which almost no team does. Without that discipline, inheritance hierarchies quietly accumulate violations over time as requirements change. Each violation makes the system slightly less predictable. In robotics, slightly less predictable compounds into unpredictably failed.

The principle is not wrong---it is just unusable without a level of formal rigor that does not exist in most engineering teams. It describes a property your code should have, but gives you no practical tool to verify it. And a principle you cannot verify is a principle you will violate without knowing it.

### Dependency Inversion Principle - The Dark Side of Dependency Injection

DIP says high-level modules should not depend on low-level modules. Both should depend on abstractions. In practice, this becomes: inject everything through interfaces, and use a dependency injection container to wire it all together.

The promise is testability and flexibility. The reality, in systems of any meaningful size, is what I think of as the **dark side of dependency injection**: a codebase where you cannot answer the question "what actually runs here?" by reading the code.

```python
class RobotController:
    def __init__(self, motor: IMotorDriver, sensor: ISensorReader, logger: ILogger):
        self.motor = motor
        self.sensor = sensor
        self.logger = logger

```

This looks clean. But to understand what `RobotController` actually does at runtime, you have to find whatever wiring code assembles it---a DI container, a factory, a composition root, a test fixture. In large systems, this wiring is spread across configuration files, decorators, and auto-discovery frameworks. You are no longer reading code; you are reconstructing a runtime graph in your head.

I have seen this happen in real systems, and believe it or not, the names were roughly the same, too.

The test isolation argument also inverts in embedded and robotics contexts. You cannot mock a servo motor out of existence to test whether a joint angle command produces the right torque profile. At some point, you need real hardware in the loop, and DIP's abstraction layers become friction between you and that reality.

There is a subtler failure too: DIP encourages you to design interfaces before you understand the domain. You create `IMotorDriver` before you know everything a motor driver needs to do. Requirements change. The interface is wrong, but it is now referenced in forty places. You have traded concrete coupling for interface coupling---and the second kind is harder to change because it is spread wider. You went from one place to change to forty.

### Interface Segregation Principle - Abstractions for Abstractions' Sake

ISP says clients should not be forced to depend on interfaces they do not use. Split large interfaces into smaller, more focused ones.

This is probably the most outdated of the five principles. It was written for a world of statically compiled languages where an interface change triggered recompilation across every dependent module. In modern tooling, that cost barely exists.

What ISP encourages in practice is a proliferation of tiny single-method interfaces:

```python
class IReadable(ABC):
    @abstractmethod
    def read(self) -> bytes: pass

class IWritable(ABC):
    @abstractmethod
    def write(self, data: bytes) -> None: pass

class ICloseable(ABC):
    @abstractmethod
    def close(self) -> None: pass

class ISeekable(ABC):
    @abstractmethod
    def seek(self, pos: int) -> None: pass

```

Now your function signature looks like:

```python
def process(source: IReadable, sink: IWritable, closer: ICloseable) -> None:

```

While this pattern is actually idiomatic in languages like Go (e.g., `io.Reader`), applying it mechanically to object-oriented hardware abstractions creates mental overhead. You have replaced one concrete type with three abstract ones. Have you made the code more understandable? Almost certainly not. You have created **abstractions for their own sake**---the thing CUPID is designed to resist.

In a robotics context, a serial port is a serial port. It reads, writes, seeks, and closes. Splitting that into four interfaces does not reflect any real domain concept. It reflects a principle applied mechanically without asking whether the cost is worth paying. The abstraction exists to satisfy ISP, not to model the domain.

CUPID - A Different Set of Questions
------------------------------------

CUPID does not give you rules. It gives you properties that good code tends to have. Dan North's five are:

-   **C**omposable - Plays well with others. Think of ROS (Robot Operating System) nodes---small, single-purpose programs passing messages rather than rigid class hierarchies.

-   **U**nix philosophy - It is not same as Single Responsibility, which states that a module should have "Single Reason to Change". Its about a module that does one thing well. A module should do its job and report errors cleanly.

-   **P**redictable - Does what you expect. I can read this code and know what it will do. I can trace a failure directly to its cause without reconstructing a call graph.

-   **I**diomatic - Feels natural in its language. Using Rust's `match` or Go's explicit error handling *is* being idiomatic, whereas forcing Java-style OOP into Rust or Go violates this property.

-   **D**omain-based - Uses the language of the problem domain. Instead of `IActuatorManager`, call it `GripperController`.

The most important for a robotics engineer is **Predictability**. Predictability means I do not need to reconstruct a runtime call graph or an inheritance tree in my head.

### The Switch Statement Argument

SOLID treats `switch` statements as a code smell, because adding a new case modifies existing code---a violation of OCP. The preferred solution is polymorphism. But this trades a localized, visible change for a dispersed, invisible one.

Consider a robot with multiple sensor types arriving over a CAN bus.

The SOLID-approved way (Python):

```python
class SensorProcessor(ABC):
    @abstractmethod
    def process(self, reading: float) -> float:
        pass

class TemperatureSensor(SensorProcessor):
    def process(self, reading: float) -> float:
        return reading * 1.8 + 32

class PressureSensor(SensorProcessor):
    def process(self, reading: float) -> float:
        return reading * 0.000145

class ProximitySensor(SensorProcessor):
    def process(self, reading: float) -> float:
        return reading / 100.0

```

Now a packet arrives with `sensor_type = 3`. You need a factory to instantiate the right class---which is a hidden `switch` statement. You have not eliminated the branching; you have buried it.

The CUPID way (Go):

```Go
func processSensorReading(sensorType SensorType, reading float64) (float64, error) {
    switch sensorType {
    case Temperature:
        return reading*1.8 + 32, nil
    case Pressure:
        return reading * 0.000145, nil
    case Proximity:
        return reading / 100.0, nil
    default:
        return 0, fmt.Errorf("unknown sensor type: %v", sensorType)
    }
}

```

This is the full behavior, visible in one screen. The stack trace on failure points here directly. A new engineer understands it in thirty seconds. Adding a sensor type is a one-line change in a known, obvious location.

In Rust, the compiler enforces that every variant is handled. Forget to add a case and the code does not compile:

```Rust
fn process_reading(sensor: SensorType, reading: f64) -> f64 {
    match sensor {
        SensorType::Temperature => reading * 1.8 + 32.0,
        SensorType::Pressure    => reading * 0.000145,
        SensorType::Proximity   => reading / 100.0,
        // Omit a variant and the build fails. Safety at compile time, not runtime.
    }
}

```

You get the safety guarantee that SOLID's polymorphism promises, without the runtime indirection.

### Languages That Align With CUPID

SOLID was designed in a world dominated by Java and C++, where polymorphism was the primary tool for managing complexity. Three languages push back on that assumption structurally, enforcing CUPID properties:

-   **C** enforces flatness and explicit control flow, making it deeply **Predictable**. There is a reason why C still dominates the embedded world; its syntax simply resists the Enterprise mindset. It has no inheritance and no virtual dispatch. Error handling is explicit returns from functions. That said, the honest counterargument is that C gives you enough rope to hang yourself in other ways (pointer arithmetic, manual memory management). So the predictability argument cuts both ways: the control flow is transparent, but memory bugs can be deeply unpredictable.

-   **Go** has no inheritance at all. No `extends`, no virtual methods, no classes. It enforces **Composability** over inheritance through struct embedding and implicitly satisfied interfaces. Errors are explicit return values---the caller deals with failure at the call site, in the same file you are reading, which is highly **Idiomatic** and transparent.

-   **Rust** enforces **Domain-based** modeling via enums and exhaustive pattern matching. It turns the switch statement from a code smell into a compiler-enforced contract. The type system encodes domain variants directly, providing safety at compile time (**Predictable** and **Idiomatic**).

These languages push you toward code that is flat, explicit, and domain-shaped---which is exactly what CUPID asks for.

### The Robotics Priority Stack

In robotics and automation, the software priority hierarchy is different from enterprise software:

1.  **Does not fail** - uptime is a hard requirement, not a nice-to-have.

2.  **Fails loudly** - when failure happens, it must be obvious and fast to diagnose.

3.  **Easy to change** - modify behavior safely when the domain requires it.

Enterprise software often inverts this. Flexibility and extensibility are prized because business requirements shift rapidly and teams are large. Subtle failures are not always a big deal, because often it is a bit of inconvenience rather than a danger to human life. SOLID was designed for that world.

But a robot on a factory floor has a finite and well-understood set of sensors, actuators, and operating modes. These are *closed domains*. The cost of a production outage far exceeds the cost of touching a `switch` statement.

SOLID asks: *How do I extend this system without touching existing code?* CUPID asks: *How do I make this system obvious, so that when something goes wrong, anyone on the team can find the problem in minutes?*

These are different questions. In robotics, the second one keeps the line running.

How
---

**1\. Prefer Flat Over Deep** $\rightarrow$ Drives **P**redictability. Every layer of abstraction is a layer of indirection. Prefer structures you can read in one file over hierarchies that require tracing through multiple classes. If you are writing `super()` calls that chain three levels up, that is a signal to flatten. Keep interfaces narrower than underlying logic.

**2\. Use Enums and Match/Switch for Closed Domains** $\rightarrow$ Uses **I**diomatic language features. When your domain has a fixed set of known variants---sensor types, motor states, error codes, command types---express that with an enum and handle it with a switch or match. The explicitness is a feature. The exhaustiveness check is a safety net the compiler provides for free. Similarly, you can use a dispatch table instead of polymorphism.

**3\. Make Failure Visible** $\rightarrow$ Aligns with the **U**nix philosophy and **P**redictability. Prefer early returns and explicit error values over exceptions that unwind through polymorphic call stacks. A function that returns `(value, error)` forces the caller to confront the failure at the call site. An exception from deep inside an inheritance hierarchy forces you to reconstruct the full context of four layers before you can understand what failed.

**4\. Name Things After the Domain** $\rightarrow$ Literally **D**omain-based. CUPID's Domain-based property is underrated. Name your structs, functions, and modules after what they represent in the physical world---`MotorCommand`, `JointAngle`, `SafetyZone`. Code that maps directly to the problem domain is faster to read under pressure than code that maps to a design pattern.

**5\. Earn Every Abstraction** $\rightarrow$ Encourages **C**omposability over rigid inheritance. Before introducing an interface or base class, ask: does this abstraction reflect something real in the domain, or does it exist to satisfy a principle? If the answer is the latter, delete it. The best abstraction is often no abstraction. The second best is one that can be deleted in an afternoon without a four-hour refactor.

CUPID is not about abandoning discipline. It is about choosing the right discipline for the domain. For systems where uptime is a requirement and debuggability is a safety concern, predictable and flat beats flexible and abstract. Every time.
