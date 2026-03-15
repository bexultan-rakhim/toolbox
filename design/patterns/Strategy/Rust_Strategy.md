Rust Strategy Pattern: Implementation & Versatility
===================================================

What
----
This is another document about implementing strategy pattern, but in Rust. If you are interested in C++, check [this doc](Cpp_Strategy.md).

The **Strategy Pattern** defines a family of interchangeable algorithms behind a common interface, letting the caller swap behavior without changing the code that uses it.

In Rust, this maps naturally onto **Traits** — but unlike most languages and similar to C++, Rust gives you multiple distinct mechanisms to express the pattern, each with different performance and flexibility characteristics. Choosing the right one is part of writing idiomatic Rust.

> **Core idea:** separate *what to do* (Context) from *how to do it* (Strategy).


Why
---

- **Versatility:** Rust is the rare language where you can choose static *or* dynamic dispatch without a rewrite. Use generics in a hot loop, swap to `dyn Trait` when you need runtime flexibility — the pattern scales from firmware to web servers.

- **Maintainability:** Each strategy is an isolated unit. You can test, benchmark, and replace individual algorithms without touching the surrounding logic. Complex behavior becomes a collection of small, auditable pieces.

- **Safety:** Strategy swapping across threads is memory-safe by construction. The compiler refuses to compile unsafe combinations — if a strategy crosses a thread boundary, it must satisfy `Send + Sync`, enforced at compile time, not at runtime.

- **Zero-cost when you want it:** Unlike most OOP languages where the pattern implies a vtable, Rust lets you pay only for what you use. Monomorphization and enum dispatch carry no runtime overhead at all.

### Trade-offs

| Implementation | Complexity | Runtime Cost | Flexibility | Best Use Case |
|---|---|---|---|---|
| `Trait Objects (dyn)` | Medium | Vtable lookup | High — Dynamic | Plugin systems, heterogeneous collections |
| `Generics (Static)` | Medium | Zero — Inlined | Low — Static | Hot loops, math libs, embedded |
| `Closures (Fn)` | Low | Near-zero | Very High | Callbacks, adapters, one-off logic |
| `Enums (Sum Type)` | Low | Zero — Branch | Medium | Small, closed sets of known algorithms |
| `Associated Types` | High | Zero — Inlined | Low — Static | Compile-time policy binding, type-level config |


How
---

### 1. Dynamic Dispatch — `Box<dyn Trait>`

The closest to the "classic" OOP strategy pattern. The concrete type is unknown at compile time; dispatch goes through a **vtable** at runtime. Use this when strategies are loaded dynamically, user-configurable, or stored in heterogeneous collections.

**When to reach for it:** plugin architectures, runtime-selectable algorithms, any time the set of strategies isn't fixed at compile time.

```rust
trait Compressor {
    fn compress(&self, data: &[u8]) -> Vec<u8>;
}

struct Pipeline {
    compressor: Box<dyn Compressor>,
}

impl Pipeline {
    fn new(compressor: Box<dyn Compressor>) -> Self { Self { compressor } }
    fn run(&self, data: &[u8]) -> Vec<u8> { self.compressor.compress(data) }
}

// Swap at runtime — no recompilation needed
pipeline.compressor = Box::new(ZstdCompressor);
```

> **Cost:** one pointer indirection per call. Negligible in most code; meaningful in tight loops.

---

### 2. Static Dispatch — Generics

The compiler generates a **separate, fully optimized copy** of the code for each concrete type via monomorphization. No vtable, no indirection, no heap allocation. This is Rust's zero-cost abstraction in action.

**When to reach for it:** performance-critical code, library APIs where the caller controls the type, anything that runs in a loop millions of times.

```rust
// unlike C++, we do not need separate mechanism.
// Same trait works for both dynamic and static dispatch!
trait Compressor { 
    fn compress(&self, data: &[u8]) -> Vec<u8>;
}

struct Pipeline<C: Compressor> {
    compressor: C,
}

impl<C: Compressor> Pipeline<C> {
    fn new(compressor: C) -> Self { Self { compressor } }
    fn run(&self, data: &[u8]) -> Vec<u8> { self.compressor.compress(data) }
}

// Type is resolved at compile time — fully inlined and optimized
let pipeline = Pipeline::new(ZstdCompressor);
```

> **Cost:** zero. Binary size grows with each monomorphized variant — worth watching in embedded contexts.

---

### 3. Functional Strategy — Closures

Skip the struct entirely. Pass behavior directly as a **closure** using Rust's `Fn` trait family. The most concise option — great for short-lived, one-off logic where defining a full type would be overkill.

**When to reach for it:** event handlers, transformation pipelines, test doubles, anywhere the strategy is a single function's worth of logic.

```rust
// no need for trait even!
struct Pipeline<F: Fn(&[u8]) -> Vec<u8>> {
    compressor: F,
}

impl<F: Fn(&[u8]) -> Vec<u8>> Pipeline<F> {
    fn run(&self, data: &[u8]) -> Vec<u8> { (self.compressor)(data) }
}

// Inline logic, no struct required
let pipeline = Pipeline { compressor: |data| lz4_compress(data) };
```

> **Fn vs FnMut vs FnOnce:** use `Fn` for shared references, `FnMut` if the closure mutates state, `FnOnce` if it consumes a value.

---

### 4. Sum Type — Enums

The most idiomatic Rust approach for a **closed, finite set** of strategies. The compiler knows every variant at compile time, dispatch is a branch instruction, and there is no heap allocation. `match` enforces exhaustiveness — adding a new variant forces you to handle it everywhere.

**When to reach for it:** a known, stable set of algorithms (e.g. sort orders, auth modes, compression levels). If the set will grow or come from outside your crate, prefer `dyn Trait`.

```rust
// enums in rust are similar to variants. Kind of.
enum Compressor { Lz4, Zstd, Brotli }

struct Pipeline { compressor: Compressor }

impl Pipeline {
    fn run(&self, data: &[u8]) -> Vec<u8> {
        match self.compressor {
            Compressor::Lz4    => lz4_compress(data),
            Compressor::Zstd   => zstd_compress(data),
            Compressor::Brotli => brotli_compress(data),
        }
    }
}
```

> **Exhaustiveness is a feature:** the compiler errors if you add a variant and forget to handle it. This is the enum's killer advantage over `dyn Trait`.

You may argue that Pipeline should not be aware of specific implementation details fo compression algorithms. Above implementation is simple and clear. However, if you insist, you can make pipeline oblivious to specific algorithms completely. Here is how:

```rust
enum Compressor { Lz4, Zstd, Brotli }

// enums can implement match instead of Pipeline!
impl Compressor {
    fn compress(&self, data: &[u8]) -> Vec<u8> {
        match self {                     // ← match lives on the enum, not the context
            Compressor::Lz4    => lz4_compress(data),
            Compressor::Zstd   => zstd_compress(data),
            Compressor::Brotli => brotli_compress(data),
        }
    }
}

struct Pipeline {
    compressor: Compressor,
}

impl Pipeline {
    fn run(&self, data: &[u8]) -> Vec<u8> {
        self.compressor.compress(data)  // ← Pipeline has no idea what's inside
    }
}
```
Difference is only tradeoff of clarity to gain encapsulation. 

---

### 5. Associated Types — Compile-time Policy Binding

The most powerful and most complex option. A `Policy` trait uses an **associated type** to bind a strategy at the type level — no runtime selection at all. The type system encodes *which* strategy is used, making illegal configurations impossible to express.

**When to reach for it:** library design where you want users to configure behavior through types, not values. Think `std::collections::HashMap`'s `BuildHasher`, or `tokio`'s `Executor`.

```rust
trait CompressionPolicy {
    type Algorithm: Compressor;
}

// Each policy is a zero-sized type — pure compile-time configuration
struct HighSpeedPolicy;
struct HighRatioPolicy;

impl CompressionPolicy for HighSpeedPolicy { type Algorithm = Lz4Compressor;   }
impl CompressionPolicy for HighRatioPolicy { type Algorithm = BrotliCompressor; }

struct Pipeline<P: CompressionPolicy> {
    _policy: std::marker::PhantomData<P>,
}

impl<P: CompressionPolicy> Pipeline<P> {
    fn run(&self, data: &[u8]) -> Vec<u8> {
        P::Algorithm::compress(data)
    }
}

// Different pipelines are different types — mixing them is a compile error
let fast:  Pipeline<HighSpeedPolicy> = Pipeline::default();
let small: Pipeline<HighRatioPolicy> = Pipeline::default();
```

> **PhantomData:** `PhantomData<P>` is a zero-sized marker that tells the compiler `Pipeline` logically owns a `P`, without storing one. No runtime cost.

You may ask when you may even need this? Well, with generics, the *caller* chooses the type. With associated types, the *implementor* chooses the type. Let me explain. With generics, nothing stops caller do this:

```rust
trait Compressor<T> {
    fn compress(&self, data: T) -> Vec<u8>;
}
// caller can implement new types satisfying trait
impl Compressor<&[u8]> for ZstdCompressor { ... }
impl Compressor<String> for ZstdCompressor { ... } //uh-oh
```

with associates:

```rust
trait Compressor {
    type Input;  // the implementor fixes this — one answer per type
    fn compress(&self, data: Self::Input) -> Vec<u8>;
}

impl Compressor for ZstdCompressor {
    type Input = &[u8];  // decided once, forever
    fn compress(&self, data: &[u8]) -> Vec<u8> { ... }
}
```
Because of this, with Policy you can bundle multiple types as compile-time configuration.

```rust
trait StoragePolicy {
    type Compressor: Compress;
    type Serializer: Serialize;
    type Encryption: Encrypt;
}

struct ProductionPolicy;
impl StoragePolicy for ProductionPolicy {
    type Compressor  = Zstd;
    type Serializer  = Bincode;
    type Encryption  = Aes256;
}

// The whole policy travels as one type — all choices stay in sync
struct Database<P: StoragePolicy> { ... }
```

---

## Choosing the Right Tool

```
Is the set of strategies fixed at compile time?
├── No  → Box<dyn Trait>          (runtime flexibility)
└── Yes → Is it a small, closed set?
          ├── Yes → Enum           (zero cost, exhaustive matching)
          └── No  → Is the logic trivial?
                    ├── Yes → Closure      (lightweight, no boilerplate)
                    └── No  → Generics or Associated Types
                              ├── Single impl per type → Associated Types  (policy pattern)
                              └── Multiple impls       → Generics          (monomorphization)
```
