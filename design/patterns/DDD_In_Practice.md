Three Patterns of Design - Refactoring Perception Obstacle Tracking Component with DDD
======================================================================================


What
----

This document is inspired by *Learning Domain-Driven Design* by Vlad Khononov. However, example in this book was too focused on business domain that is too distant from the field I am working on - Robotics. I wanted to write this document to have a clear illustrative example on how to apply DDD in practice.

The core idea of this document is that the same software problem can be implemented at different levels of structural maturity. This document uses a single task — **obstacle tracking in a perception system** — to illustrate three approaches: transactional scripts, the active record pattern, and Domain-Driven Design. The task does not change. The domain knowledge required to solve it does not change. What changes is how that knowledge is organized, where it lives, and how resistant the resulting code is to complexity over time.

The three approaches represent a progression, not a spectrum of equally valid choices. Each level addresses a failure mode of the one before it. Understanding the failure modes is what motivates the progression.

**The task:** an obstacle tracker receives sensor measurements over time and must maintain the state of each tracked object — its position, velocity, classification, and confidence. When a new measurement arrives, the tracker must associate it with an existing track or initialize a new one, update the track's state, and retire tracks that have not been observed recently.


Why
---

### The Three Approaches

I have seen people mixing these approaches and having debates which one is better without having clarity on what are the tradeoffs. Sometimes, people are not even aware that they are using one over another. In the wild, you will not see one approach fleshed out cleanly like in this example, and you most-likely see the blend of all three approaches. But putting them in distinct bins helps to reason about them in isolation. Let's conceptualize them. So said approaches are these:

**Transactional scripts** organize logic as procedures. Each operation is a function that reads inputs, performs work, and writes outputs. There is no object that owns the state; state is passed around as raw data structures. This is how most embedded and systems code begins — it is fast to write, easy to reason about in isolation, and has no conceptual overhead. It fails when the number of operations grows, because the rules of the domain — what makes a track valid, when it should be retired, how confidence is computed — are scattered across functions with no single place of authority. In this document, I will show example of implementation in C, because C fits this really well: it is a procedural language, does not support OOP and does not have overhead complexity of other languages.

**Active record / OOP** organizes logic into objects that own their state and expose methods. A `Track` object knows its own position and can update itself. This is the natural C++ approach and resolves the scattering problem: domain rules move closer to the data they govern. It fails when objects begin to take on infrastructure concerns — a `Track` that knows how to serialize itself to a database, or validate its own input format, is mixing domain logic with technical concerns. The domain model becomes entangled with the system around it. I will show implementation in C++, as it is best fit as OOP language. Example in this section will be the most familiar to many readers.

**Domain-Driven Design** separates the domain model from all infrastructure and application concerns. Entities encode identity and lifecycle. Value objects encode concepts with no identity of their own. The domain model has no dependencies on serialization, storage, or communication. It is a pure expression of the perception domain's rules, written in its ubiquitous language. This is the approach Rust's type system is particularly well suited to enforce: ownership semantics make value object immutability natural, and the type system can encode domain invariants that would be runtime checks in C or C++. That is why, for this section, I will demonstrate it using Rust, as it is, in my opinion, the best fit language. Although, you could implement it in C++ as well.

### Why the Progression Matters

The central claim of DDD — articulated by Evans (2003) and reinforced by Vernon (2013) — is that software complexity is primarily a modeling problem, not a technical one. Transactional scripts are not wrong because they use C; they are limited because they have no model. Active record is not wrong because it uses OOP; it is limited because its model is entangled with its infrastructure. DDD is not correct because it uses Rust; it is more capable because it isolates the model completely, making it possible to reason about the domain independently of how it is deployed.

For a perception system, this distinction is practical rather than theoretical. Obstacle tracking rules — how to associate a measurement to a track, when a track is considered confirmed, when it should be dropped — are the core domain. They encode the team's understanding of sensor behavior, object dynamics, and acceptable uncertainty. That knowledge should live in one place, be expressible without reference to ROS messages or shared memory buffers, and be testable without a running sensor stack.

### Tradeoff Analysis

| Dimension | Transactional Script (C) | Active Record / OOP (C++) | DDD (Rust) |
|---|---|---|---|
| **Initial speed** | Fastest — no abstractions to design | Moderate | Slowest — requires upfront modeling |
| **Domain rule locality** | Poor — rules scattered across functions | Moderate — rules near data, but mixed with infra | High — rules isolated in pure domain model |
| **Testability** | Low — functions tightly coupled to data layout | Moderate — objects testable in isolation | High — domain testable with no infrastructure |
| **Type safety** | Minimal — structs with no invariant enforcement | Partial — class encapsulation, runtime checks | Strong — invariants encoded in type system |
| **Scalability to complexity** | Poor — grows into spaghetti | Moderate — degrades as objects accumulate concerns | High — complexity stays in the model, not the glue |
| **Suitable for** | Firmware, hard real-time, prototypes | Mid-complexity systems, team familiar with OOP | Core domain in complex, long-lived systems |
| **Infrastructure coupling** | High — data layout tied to wire format | Moderate — objects often aware of persistence | None — domain has zero infrastructure dependencies |


How
---

Now, let's see some practical examples. The following three implementations all solve the same problem: update the state of a tracked obstacle given a new sensor measurement. The focus is on where the domain rules live, not on the full tracker architecture.

### Level 1 — Transactional Script in C

Logic lives in free functions. State is a plain struct. There is no object that owns the tracking rules — they are expressed as conditionals inside procedures. The domain knowledge (confidence decay, retirement threshold, velocity update) is implicit in the arithmetic.

```c
// This is a C code example:

#include <stdint.h>   /* uint32_t, uint64_t                                     */
#include <stdbool.h>  /* bool, true                                             */

#define TRACKER_MAX_TRACKS        (64U)
#define TRACKER_RETIREMENT_AGE_MS (500U)
#define TRACKER_MIN_DT_S          (1e-6F)   /* guard against near-zero dt       */
#define TRACKER_CONF_BLEND_PRIOR  (0.70F)
#define TRACKER_CONF_BLEND_MEAS   (0.30F)
#define TRACKER_CONFIRM_THRESHOLD (0.75F)

/* --- Types ----------------------------------------------------------------- */
typedef struct
{
    uint32_t id;
    float32_t x;
    float32_t y;
    float32_t vx;
    float32_t vy;
    float32_t confidence;   /* range [0.0, 1.0] — caller is responsible        */
    uint64_t  last_seen_ms;
    bool      active;
} Track_t;

typedef struct
{
    float32_t x;
    float32_t y;
    float32_t confidence;   /* range [0.0, 1.0] — validated before passing in  */
    uint64_t  timestamp_ms;
} Measurement_t;

/* Static storage: no heap allocation in safety-critical context               */
static Track_t s_tracks[TRACKER_MAX_TRACKS];

/* --- Forward declarations -------------------------------------------------- */
static void    track_update(Track_t * const p_track,
                             const Measurement_t * const p_meas,
                             float32_t dt_s);
static void    tracker_retire_stale(uint64_t now_ms);
static bool    track_is_confirmed(const Track_t * const p_track);

/* Implementation details ----------------------------------------------------- */
static void track_update(Track_t * const p_track,
                          const Measurement_t * const p_meas,
                          float32_t dt_s)
{
    if ((p_track != NULL) && (p_meas != NULL))
    {
        if (dt_s > TRACKER_MIN_DT_S)
        {
            p_track->vx = (p_meas->x - p_track->x) / dt_s;
            p_track->vy = (p_meas->y - p_track->y) / dt_s;
        } else {
            /* else: velocity unchanged — stale dt is a known sensor condition  */
        }

        p_track->x = p_meas->x;
        p_track->y = p_meas->y;

        /* Confidence blend — domain rule, implicit in arithmetic, not named    */
        p_track->confidence = (TRACKER_CONF_BLEND_PRIOR * p_track->confidence)
                            + (TRACKER_CONF_BLEND_MEAS  * p_meas->confidence);

        p_track->last_seen_ms = p_meas->timestamp_ms;
    } else {
        // uninitialized tracks can be skipped
        ;
    }

}

static void tracker_retire_stale(uint64_t now_ms)
{
    uint32_t i;
    for (i = 0U; i < TRACKER_MAX_TRACKS; i++)
    {
        if (s_tracks[i].active == true)
        {
            /* Subtraction safe: now_ms >= last_seen_ms by system invariant.   */
            /* If clock wraps, age is large and track retires — acceptable      */
            uint64_t age_ms = now_ms - s_tracks[i].last_seen_ms;

            if (age_ms > (uint64_t)TRACKER_RETIREMENT_AGE_MS)
            {
                s_tracks[i].active = false;
            } else {
                // track is not old enough to retire, do nothing
                ;
            }
        } else {
            // non-active tracks are ignored
            ;
        }
    }
}

static bool track_is_confirmed(const Track_t * const p_track)
{
    bool result = false;

    if (p_track != NULL)
    {
        result = (p_track->active == true)
              && (p_track->confidence >= TRACKER_CONFIRM_THRESHOLD);
    } else {
        // Track is not confirmed, return false
        ;
    }

    return result;
}
```
This tracker implementation gives you functionality to do what is necessary to update tracked objects with measurements, retire stale tracked objects, confirm if object is still active. Notice how domain rules - logic that is important for the behavior of the tracked is sprinkled into different methods.

**What breaks at scale:** when a second engineer adds a new update path — say, a fused measurement from a different sensor — they write another function with slightly different confidence blending. The rule now exists in two places. Over time, the rules diverge. There is no single authority on what a valid track state looks like. Also you may see how extending this code requires careful analysis of the assumptions. What if assumptions change? Also, you have to write a bit of a boilerplate here and there.

Question of the day: **Can we do better?**

---

### Level 2 — Active Record / OOP in C++

Logic moves into the object. A `Track` now owns its update rules and retirement logic. The domain knowledge is no longer scattered — it lives on the class. This is the natural resolution of the transactional script problem.

```cpp
// This is a C++ Code Example
#include <cstdint>
#include <optional>
#include <algorithm>  /* std::clamp */

/* Named constants — no magic numbers in logic */
namespace tracker {

constexpr float    kConfBlendPrior     = 0.70F;
constexpr float    kConfBlendMeas      = 0.30F;
constexpr float    kConfirmThreshold   = 0.75F;
constexpr float    kMinDtSecs          = 1e-6F;
constexpr uint64_t kRetirementAgeMs    = 500U;

/* Measurement is a plain data carrier — no behaviour, no validation here.
   Validation is the responsibility of the ingest layer before construction.
   In production this would typically be a generated protobuf/IDL struct.      */
struct Measurement
{
    float    x;
    float    y;
    float    confidence;   /* expected [0.0, 1.0] — not enforced here          */
    uint64_t timestamp_ms;
};

class Track
{
public:
    explicit Track(uint32_t id,
                   float    x,
                   float    y,
                   float    confidence,
                   uint64_t timestamp_ms) noexcept
        : id_           { id }
        , x_            { x }
        , y_            { y }
        , vx_           { 0.0F }
        , vy_           { 0.0F }
        , confidence_   { std::clamp(confidence, 0.0F, 1.0F) }
        , last_seen_ms_ { timestamp_ms }
        , active_       { true }
    {}

    /* Non-copyable: tracks have identity; copying one is a domain error.
       Move is allowed — ownership can transfer to a different container.       */
    Track(const Track&)            = delete;
    Track& operator=(const Track&) = delete;
    Track(Track&&)                 = default;
    Track& operator=(Track&&)      = default;
    ~Track()                       = default;

    /* Domain rule: update track state from a new measurement.
       dt is computed by the caller from timestamps — not recomputed here to
       keep this function testable without a live clock.                        */
    void update(const Measurement& meas, float dt_secs) noexcept
    {
        /* Guard: dt too small means clock stall or duplicate message.
           Velocity is left unchanged — a deliberate domain decision.           */
        if (dt_secs > kMinDtSecs)
        {
            vx_ = (meas.x - x_) / dt_secs;
            vy_ = (meas.y - y_) / dt_secs;
        }

        x_ = meas.x;
        y_ = meas.y;

        /* Confidence blend — clamp output to keep it in [0, 1].
           Input confidence from meas is not re-validated; the ingest layer
           owns that responsibility. Clamping the result is a safety net only. */
        const float blended = (kConfBlendPrior * confidence_)
                            + (kConfBlendMeas  * meas.confidence);
        confidence_   = std::clamp(blended, 0.0F, 1.0F);
        last_seen_ms_ = meas.timestamp_ms;
    }

    void retire_if_stale(uint64_t now_ms) noexcept
    {
        /* Underflow guard: if now_ms < last_seen_ms_ the track was updated
           in the future — treat as not stale rather than retiring spuriously. */
        if (now_ms >= last_seen_ms_)
        {
            const uint64_t age_ms = now_ms - last_seen_ms_;
            if (age_ms > kRetirementAgeMs)
            {
                active_ = false;
                ROS_WARN("track %d is stale, retirning", id_);

            }
        } else {
        }
    }

    [[nodiscard]] bool is_confirmed() const noexcept
    {
        return active_ && (confidence_ >= kConfirmThreshold);
    }

    /* Accessors — minimal surface exposed to callers                          */
    [[nodiscard]] uint32_t id()         const noexcept { return id_; }
    [[nodiscard]] float    x()          const noexcept { return x_; }
    [[nodiscard]] float    y()          const noexcept { return y_; }
    [[nodiscard]] float    confidence() const noexcept { return confidence_; }
    [[nodiscard]] bool     is_active()  const noexcept { return active_; }

    void serialize_to_ros_message(ObstacleMsg& msg) const noexcept
    {   
        // For ease of serializing to ROS
        msg.id        = id_;
        msg.x         = x_;
        msg.y         = y_;
        msg.confirmed = is_confirmed();
    }

private:
    uint32_t id_;
    float    x_;
    float    y_;
    float    vx_;
    float    vy_;
    float    confidence_;
    uint64_t last_seen_ms_;
    bool     active_;
};

} /* namespace tracker */
```
This resolves some of the issues with the transactional scripts. The states of the data are localized. There is clear responsibility for the class. If you want to update the domain logic, you can create a different tracked object type and you can compose/inherit to share the useful code. 

**What breaks at scale:** the `serialize_to_ros_message` method is the tell. Once a domain object begins absorbing infrastructure concerns — message formats, database schemas, logging structures — changing the infrastructure requires touching the domain model. The model is no longer a pure expression of domain knowledge; it is a load-bearing wall for the system around it. Testing the confirmation rule now requires a ROS environment.

---

### Level 3 — Domain-Driven Design in Rust

The domain model is completely isolated. Value objects (`TrackId`, `Confidence`, `Position`, `Velocity`) encode domain concepts and enforce their own invariants at the type level. The `Track` entity manages lifecycle transitions explicitly. There is no infrastructure anywhere in this module — no serialization, no ROS, no shared memory. Those concerns belong to an adapter layer outside the domain.

```rust
// This is a rust example.

#[derive(Debug)]
pub enum DomainError {
    InvalidConfidence(f32),
    // Other error types...
}

// Value objects: immutable, no identity, invariants enforced by construction

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct TrackId(u32);

#[derive(Debug, Clone, Copy)]
pub struct Confidence(f32);

impl Confidence {
    // Invariant enforced at the type boundary — impossible to construct invalid confidence
    pub fn new(value: f32) -> Result<Self, DomainError> {
        if value >= 0.0 && value <= 1.0 {
            Ok(Confidence(value))
        } else {
            Err(DomainError::InvalidConfidence(value))
        }
    }

    pub fn value(&self) -> f32 { self.0 }

    // Domain rule expressed as a method on the concept that owns it
    pub fn blend(self, measurement: Confidence) -> Confidence {
        Confidence(0.7 * self.0 + 0.3 * measurement.0)
    }
}

#[derive(Debug, Clone, Copy)]
pub struct Position { pub x: f32, pub y: f32 }

#[derive(Debug, Clone, Copy)]
pub struct Velocity { pub vx: f32, pub vy: f32 }

impl Velocity {
    // Domain rule expressed as a method on the concept that owns it
    pub fn from_displacement(prev: Position, next: Position, dt_secs: f32) -> Self {
        Velocity {
            vx: (next.x - prev.x) / dt_secs,
            vy: (next.y - prev.y) / dt_secs,
        }
    }
}

// Explicit lifecycle: a track is either Tentative or Confirmed, never ambiguous
#[derive(Debug, Clone)]
pub enum TrackStatus {
    Tentative,
    Confirmed,
    Retired,
}

// The domain entity: owns identity and lifecycle transitions
#[derive(Debug)] // Non-copyable!
pub struct Track {
    id: TrackId,
    position: Position,
    velocity: Velocity,
    confidence: Confidence,
    status: TrackStatus,
    last_seen_ms: u64, // technically, this requires its own domain type as well! For simplicity, we won't :)
}

impl Track {
    pub fn new(id: TrackId, position: Position,
               confidence: Confidence, timestamp_ms: u64) -> Self {
        Track {
            id,
            position,
            velocity: Velocity { vx: 0.0, vy: 0.0 },
            confidence,
            status: TrackStatus::Tentative,
            last_seen_ms: timestamp_ms,
        }
    }

    // Domain rule: what does updating a track mean, precisely?
    // Expressed entirely in domain terms — no infrastructure visible
    pub fn apply_measurement(&mut self, new_position: Position,
                              new_confidence: Confidence, timestamp_ms: u64) {
        let dt = (timestamp_ms - self.last_seen_ms) as f32 / 1000.0;
        if dt > 0.0 {
            self.velocity = Velocity::from_displacement(
                self.position, new_position, dt
            );
        }
        self.position = new_position;
        self.confidence = self.confidence.blend(new_confidence);
        self.last_seen_ms = timestamp_ms;
        self.try_confirm();
    }

    // Lifecycle transition: confirmation is a domain event, not an external check
    fn try_confirm(&mut self) {
        if let TrackStatus::Tentative = self.status {
            if self.confidence.value() >= 0.75 {
                self.status = TrackStatus::Confirmed;
            }
        }
    }

    // Lifecycle transition: retirement is explicit and irreversible
    pub fn retire_if_stale(&mut self, now_ms: u64) {
        if now_ms.saturating_sub(self.last_seen_ms) > 500 {
            self.status = TrackStatus::Retired;
        }
    }

    pub fn is_active(&self) -> bool {
        !matches!(self.status, TrackStatus::Retired)
    }

    // Read-only access for the adapter layer — domain does not know what uses this
    pub fn id(&self) -> TrackId { self.id }
    pub fn position(&self) -> Position { self.position }
    pub fn status(&self) -> &TrackStatus { &self.status }
}

// Infrastructure adapter lives outside the domain entirely
// It translates the domain model into whatever the system needs
mod adapter {
    use super::{Track, TrackStatus};

    pub struct RosObstacleMsg {
        pub id: u32,
        pub x: f32,
        pub y: f32,
        pub confirmed: bool,
    }

    // The adapter knows about both the domain and the infrastructure.
    // The domain knows about neither.
    pub fn to_ros_message(track: &Track) -> RosObstacleMsg {
        RosObstacleMsg {
            id: track.id().0,
            x: track.position().x,
            y: track.position().y,
            confirmed: matches!(track.status(), TrackStatus::Confirmed),
        }
    }
}
```

**What this achieves:** the domain rules — confidence blending, velocity estimation, confirmation threshold, retirement — all live inside the domain module with no external dependencies. `Confidence::new` makes it impossible to construct a confidence value outside `[0, 1]` — the invariant is structural, not a runtime assertion. The `TrackStatus` enum makes lifecycle states explicit; there is no boolean `active` flag that can be set to any combination. The adapter translates the domain into ROS messages without the domain knowing ROS exists. Changing the message format does not touch the domain model. Testing the confirmation rule requires no infrastructure at all.

---

### The Progression Summarized

| | Transactional Script | Active Record | DDD |
|---|---|---|---|
| **Where are the rules?** | Scattered in functions | On the object, mixed with infrastructure | Isolated in a pure domain model |
| **How are invariants enforced?** | Runtime conditionals, easily bypassed | Encapsulation, partially enforced | Type system — structurally impossible to violate |
| **What does testing require?** | The full data layout | The class, possibly infrastructure | Only the domain module |
| **What changes when infrastructure changes?** | Everything | The object | Only the adapter |
| **Ubiquitous language** | Absent — names are technical | Partial — class names reflect domain | Full — every type is a domain concept |

The progression is not about language sophistication. C++ is not better than C because it is newer; Rust is not better than C++ because it is modern. Each language choice in this document was made because the language's features align with what that level of maturity requires. C gives you direct control over data layout, which transactional scripts need. C++ gives you objects with encapsulation, which active record needs. Rust gives you a type system that can encode domain invariants structurally, which DDD benefits from — but DDD can be practiced in any language that supports encapsulation and module boundaries.

---

## Sources

- Evans, E. (2003). *Domain-Driven Design: Tackling Complexity in the Heart of Software*. Addison-Wesley. — Primary source for entity, value object, domain isolation, and ubiquitous language concepts used in the Level 3 implementation.
- Vernon, V. (2013). *Implementing Domain-Driven Design*. Addison-Wesley. — Source for aggregate design, lifecycle transitions, and the adapter/anticorruption layer pattern.
- Fowler, M. (2002). *Patterns of Enterprise Application Architecture*. Addison-Wesley. — Original description of the Transaction Script and Active Record patterns used in Levels 1 and 2.
- Klabnik, S. & Nichols, C. (2023). *The Rust Programming Language* (2nd ed.). No Starch Press. — Reference for Rust ownership, type system invariants, and enum-based state modeling used in Level 3.
- Blackshear, S., et al. (2019). Move: A Language With Programmable Resources. Libra Association Technical Report. — Supporting reference for type-system-enforced invariants as a domain modeling technique.
- Paden, B., Čáp, M., Yong, S. Z., Yershov, D., & Frazzoli, E. (2016). A survey of motion planning and control techniques for self-driving urban vehicles. *IEEE Transactions on Intelligent Vehicles*, 1(1), 33–55. — Domain reference for obstacle tracking as a perception subdomain in AD systems.
- Wohlin, C., et al. (2012). *Experimentation in Software Engineering*. Springer. — Background on software design maturity models and the relationship between design structure and maintainability.
