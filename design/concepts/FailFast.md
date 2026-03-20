Fail Fast: Why Defensive Programming Is Unsafe
==============================================
What
----

This is an article on why "defensive programming" - the practice of adding guards and null-checks everywhere - often makes systems more dangerous, not less.

If you take anything from this article, let it be this: **Defensive programming makes programs less brittle, but it does not make them fail safe.**

In automation and robotics, we are taught to be defensive. We check for nulls, we catch all exceptions, and we provide default values to "keep the loop running." But this is a misunderstanding of safety. Defensive programming doesn't prevent failure. It makes software less brittle by trading with "diagnosability". It allows a "poisoned" state to travel through your call stack like a ghost, only causing a wreck five modules downstream where the trail has gone cold.

> [!NOTE]
> A bit of trivia: Defensive Programming has traces all the way back to NASA's Apollo project and Margaret Hamilton.

To be clear: there is one place where defensive programming is correct — at the dirty edges of your system (parsing raw JSON, reading CAN bus packets, deserializing untrusted input). Validate there, convert to trusted types, and then never check again. Everything in this article is about what happens *inside* those boundaries.

Why
---

Defensive programming is often a mask for a lack of confidence in your system's invariants. It creates a "soft" failure mode that is significantly harder to debug than a "hard" crash.

### 1. It Hides the Source of Infection

When you add guards everywhere - returning `null`, swallowing exceptions, or providing silent default values - you allow corrupt state to propagate.

```rust
// The Defensive Way (Anti-pattern)
fn get_joint_angle(sensor_id: u32) -> f64 {
    match registry.get(&sensor_id) {
        Some(sensor) => sensor.read(),
        None => 0.0, // Silent default: Is the sensor missing or is the ID wrong?
    }
}
```

If the `sensor_id` is invalid, the robot gets `0.0`. It doesn't know why it got zero. It just continues execution with incorrect data. The error doesn't blow up where it originated; it quietly poisons downstream logic. By contrast, a "fail fast" approach would `panic!` or return a strict `Error` immediately, providing a clear cause.

### 2. It Creates False Confidence in Invariants

In many languages, developers defensively check for null everywhere like `if (sensor != null)`. In Rust, the type system eliminates the "null" problem, but the defensive mindset persists through over-using `unwrap_or_default()`.

If a function requires a valid `User` to proceed, and you provide a "guest" default just to avoid a crash, you have essentially told the system that the identity of the user doesn't actually matter. A system designed around strong invariants trains developers to maintain them. If the system crashes (panics) when it encounters an impossible state, you are forced to fix the logic at the call site rather than papering over it.

### 3. Error-Handling Code is a Major Source of Bugs

The more defensive checks you write, the more branches you create. These "unhappy paths" are rarely exercised in testing. A classic example is the C++ "wildcard" catch (`catch (...)`), which swallows everything from memory errors to logic violations.

```cpp
// The Defensive Way (Anti-pattern): Swallowing the problem
try {
    hardware_driver->initialize();
} catch (...) {
    // We caught an unspecified error. Now the driver is uninitialized,
    // but the program continues as if nothing happened.
    log("Something went wrong, but let's keep going!");
}
```

By the time this catch block executes, the driver is in an unknown state. But because you've "handled" the error, the rest of the system continues, eventually crashing because it tries to use a null pointer or an unconfigured bus. Studies of catastrophic production failures found that a large proportion of failures were caused by incorrect error-handling code like this ([source](https://www.usenix.org/system/files/conference/osdi14/osdi14-paper-yuan.pdf), Section 4 on catastrophic failures.), not the primary logic.

### 4. It Couples Components via Implicit Contracts

Defensive code at module boundaries means each layer is compensating for the potential misbehavior of its neighbors. This creates invisible coupling. Component A starts depending on Component B's quirky defensive behavior (e.g., "I know B returns an empty string if the hardware is disconnected, so I'll check for length 0"). When B is eventually fixed to return a proper `Err`, A breaks in a way that makes no sense. Clean interfaces with explicit contracts keep components truly decoupled.

### 5. It Ruins Recovery Logic

Fault-tolerant systems like Erlang/OTP are built on the "Let it Crash" philosophy. They separate doing work from handling failure. Defensive programming conflates these two. When business logic is littered with defensive checks, it becomes impossible to see the "happy path," and even harder to implement a clean, high-level recovery strategy (like a supervisor restart).

### 6. It Kills Real-Time Performance
 
In general-purpose software, redundant validation is annoying. In real-time systems, it is a correctness violation.
 
Every layer defensively re-validates the same inputs — null checks, bounds checks, type assertions, sanity checks on values. In a deep call stack, the same data might be validated a dozen times. Each check is a branch. Branches mean branch mispredictions. Mispredictions mean pipeline flushes. In a tight control loop running at 1 kHz, this is not overhead — it is jitter, and jitter breaks deadlines.
 
It gets worse. Defensive checks scattered across hot paths destroy instruction cache locality. Your CPU was about to execute contiguous, predictable code; instead it is jumping into error-handling branches that are cold, rarely-taken, and sitting in a completely different cache line. You have now paid the cost of that check even when nothing is wrong.
 
In an RTOS context, bloated execution time in a high-priority task delays every lower-priority task behind it. Enough of this and you have de-facto priority inversion — not from a mutex, but from accumulated defensive slop. And if your execution budget is tight enough, a watchdog will fire not because anything failed, but because you spent too long checking that nothing failed.
 
```rust
// Defensive: re-validates on every call, every loop iteration
fn update_joint(position: f64, velocity: f64, torque: f64) {
    if position < 0.0 || position > 1.0 { return; }
    if velocity < -MAX_VEL || velocity > MAX_VEL { return; }
    if torque < -MAX_TORQUE || torque > MAX_TORQUE { return; }
    hardware.write(position, velocity, torque);
}
 
// Fail-fast: validation happens once at the boundary, on ingress.
// Inside the loop, the type guarantees the invariant — no checks needed.
fn update_joint(cmd: ValidatedCommand) {
    hardware.write(cmd.position, cmd.velocity, cmd.torque);
}
```
 
The `ValidatedCommand` newtype is not just cleaner — it is faster. The invariant is proven at the boundary, encoded in the type, and trusted everywhere after. Zero runtime cost inside the loop.

### Why people write defensive programming

Here is why people write defensive programming: **It is a technical debt for failure strategies**. Listen, I know we have been there. We have to ship this program and there is one more branch from happy path, we don't want to think about too deeply. The main path logic is hard enough already. We often write defensive code because it is the path of least resistance. Designing a robust recovery or shutdown strategy takes time and architectural foresight, that maybe no one in your team has. Your system engineering team will be half-year or more late before they can give meaningful requirements for a sensical failure strategy, while this code needs to be shipped and it needs to be shipped now. "Best is enemy of better", we say and implement logic for swallowing an error or providing a sentinel value to bypass that work, essentially saying, "it is not my problem anymore."

Then, clueless junior dev sees this, and now it is the main strategy for error handling. It is the only error handling they have seen in the codebase. They come to another team and start proselytizing these error handling methods.

But you know it, deep in your heart, that this is a tech debt. By opting for a "soft failure" now, you are offloading the cost of debugging a much more complex, non-deterministic failure onto your future self (or your on-call team that have no clue how this logic works). No one understands why there is some non-deterministic error that happens once in a half month under the weirdest conditions ever now, and maybe no one will know.


How
---

**1. Write Tests** → Instead of guessing the error handling, it's better to just write tests to check if the condition you are trying to guard against will be possible to handle with well-behaved logic. Don't just test the "happy path." Write tests that verify your invariants actually cause a crash when violated. In Rust, you can use `#[should_panic]`:

```rust
#[test]
#[should_panic(expected = "Invalid position")]
fn test_actuator_out_of_bounds() {
    // This test ensures the code fails fast as expected
    move_actuator(1.5);
}
```

**2. Use assertions for internal invariants** → If a condition must be true for the code to make sense, use `assert!`. If it fails, the program is in an undefined state; stop immediately.

```rust
fn move_actuator(position: f64) {
    // If this fails, the logic upstream is fundamentally broken.
    assert!((0.0..=1.0).contains(&position), "Invalid position: {}", position);
    hardware.write(position);
}
```

**3. Use explicit error types for predictable errors** → In modern C++, prefer `std::expected` over broad exception handling for failures that are part of normal operation.

```cpp
#include <expected>
#include <exception>
std::expected<void, std::string> init_hardware() {
    if (!bus.is_ready()) return std::unexpected("Bus Offline");
    return {};
}
void main_loop() {
    auto result = init_hardware();
    if (!result) {
        // Handle expected failure at the boundary
        report_and_shutdown(result.error());
        return;
    }
    // Logic error? Fail hard.
    if (critical_invariant_violated()) {
        std::terminate();
    }
}
```

**4. Return Result types, not sentinels** → Avoid returning `0.0` or `-1` to signal failure. Use Rust's `Result` type to force the caller to acknowledge the possibility of failure at the call site. FYI, this is not good for all languages — for example, you should prefer exceptions in Python still.

**5. Define "Safe States" at the boundary** → Be defensive only at the "dirty" edges (e.g., parsing JSON or reading raw CAN bus packets). Convert raw data into validated types (Newtypes). Once data is in a `ValidatedReading` struct, the rest of the system can trust it without re-checking.

**6. Implement deliberate fault isolation** → Build your system in isolated units. If a thread panics due to a violated invariant, a watcher thread should catch the panic, log the state, and restart the worker from a clean state.

**7. Avoid swallowing errors** → Never write `if let Err(_) = result { }`. If you do not know exactly how to fix the error, let it propagate using the `?` operator. Let it bubble up to a level that has a recovery strategy.

---

Defensive programming is an attempt to achieve safety through politeness. But in engineering, politeness is a vulnerability.
