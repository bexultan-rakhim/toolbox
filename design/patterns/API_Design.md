Designing Great APIs: C++ and Rust
==================================

What
----

Great API design is the art of making an interface **easy to use correctly and hard to use incorrectly**. It is not just about functionality, but about the "ergonomics" of the code.

In C++ and Rust, this involves:

- **Self-documenting types:** Using the type system to express intent (e.g., `std::unique_ptr` vs `T*`).

- **Compile-time enforcement:** Leveraging features like `[[nodiscard]]`, `const`, and Rust's ownership model to catch bugs before the code even runs.

- **Predictable Error Handling:** Ensuring errors are "in-band" and impossible to ignore.

Why
---

Ask yourself, when was the last time, when you saw the function signature and immediately know how to use this function and it did not betray you?

Code is read and maintained far more often than it is written. Let's look at exactly what happens when APIs are poorly designed versus well-designed.

**1\. Preventing Catastrophic Failure (Safety)** A bad API relies on the developer to remember the rules. A good API enforces the rules at compile time.

```cpp
// Bad: The compiler happily accepts dangerous input.
void processUser(User* u);
processUser(nullptr); // CRASH at runtime

```
Why this is bad? Well, in C++ there is no point to pass raw pointer to a standalone functions, given that it is a common rule that raw pointers are for **non-resource-owning** types. For anything that should manage resource lifecycle, you should be using smart pointers. So, if this function accepts raw pointer, it violates this principle, because whatever it does with the type gives it ambiguity on ownership. If it was non-owning, then you could just pass the reference instead:

```cpp
// Good: The compiler refuses to compile invalid state.
void processUser(User& u);
// processUser(nullptr); // 🛑 Compile error! Safe by design.

```

**2\. Eliminating Cognitive Load** When an API is "hard to use wrong," a developer doesn't need to constantly refer to documentation to understand the parameters. The call site tells the whole story.

```cpp
// Bad: What do these booleans mean?
initGraphics(1080, 1920, true, false);

```
What if you accidentally swap the order? Does width comes first or height?
```rust
// Good: The intent is immediately obvious without reading docs.
init_graphics(
    Width(1920),
    Height(1080),
    Fullscreen::Yes,
    Vsync::No
);

```

**3\. Fearless Refactoring (Maintainability)** When you change the internal implementation of a strongly-typed API, the compiler will act as a safety net, instantly pointing out exactly where the API contract is broken across your entire codebase, rather than letting logic errors slip into production.

How
---

### 1\. Express Ownership Clearly

Raw pointers in C++ lack clarity regarding lifecycle management and nullability. If a function doesn't manage the lifetime of a resource, it should take a reference.

**Bad (C++):** Ambiguous ownership.

```cpp
void renderModel(Model* m); // Who deletes this? Does it take ownership?

```

**Good (C++):** Explicit intent.

```cpp
void renderModel(const Model& m); // Just reading, cannot be null.
void storeModel(std::unique_ptr<Model> m); // Explicitly taking ownership.

```

**Rust:** Lifetimes and the borrow checker enforce this natively.

```rust
fn render_model(m: &Model) {} // Borrows read-only.
fn animate_model(m: &mut Model) {} // Borrows mutably.
fn store_model(m: Model) {} // Takes ownership, caller loses access.

```

### 2\. Use "In-Band" Error Handling

Avoid "out-of-band" errors like `errno`. Force the caller to acknowledge the possibility of failure immediately.

**Bad (C++):** Errors can be easily ignored.

```cpp
bool initializeSystem(); // Often ignored.
int readData(Buffer& b); // Returns -1 on error, sets errno.

```

**Good (C++):** Use `[[nodiscard]]` and `std::expected` (C++23).

```cpp
[[nodiscard]] std::expected<Data, ErrorCode> fetchData() noexcept;

```

**Rust:** The `Result` enum forces the caller to handle both success and failure paths.

```cpp
fn fetch_data() -> Result<Data, ErrorCode> { /* ... */ }

// Caller must explicitly handle it:
match fetch_data() {
    Ok(data) => println!("Success!"),
    Err(e) => eprintln!("Error: {:?}", e),
}

```

### 3\. Strong Typing over "Stringly" Typed

Don't use primitives for everything. Prevent users from accidentally swapping parameters of the same underlying type.

**Bad:** Swappable primitives.

```cpp
// C++
void setCoordinates(double lat, double lon);
// Call site: setCoordinates(lon, lat); // Compiles fine, logic is ruined.

```

**Good:** Use strong types.

```cpp
// C++
struct Latitude { double v; };
struct Longitude { double v; };

void setCoordinates(Latitude lat, Longitude lon);
// Call site: setCoordinates(Latitude{35.6}, Longitude{139.6}); // Impossible to swap.

```

### 4\. Fuzz Your Interface

Even with perfect types, logic edge cases exist. Use fuzzing tools to throw pseudo-random, malformed inputs at your API to find unhandled crashes.

**C++ (libFuzzer):**

```cpp
extern "C" int LLVMFuzzerTestOneInput(const uint8_t *Data, size_t Size) {
    // Pass random bytes to your API to ensure it never crashes
    MyLibrary::parse(std::string_view(reinterpret_cast<const char*>(Data), Size));
    return 0;
}

```

**Rust (cargo-fuzz):**

```rust
fuzz_target!(|data: &[u8]| {
    if let Ok(s) = std::str::from_utf8(data) {
        let _ = my_library::parse(s); // Ensure parsing never panics
    }
});

```
