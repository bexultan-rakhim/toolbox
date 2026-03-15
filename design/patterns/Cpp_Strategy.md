C++ Strategy Pattern: Implementation & Versatility
==================================================

What
----

This is a pattern I use quite a lot, and have found several ways to implement it. The benefits of this pattern and its different implementations provide some of the most versatile feature if you design ahead of things. As name suggests, strategy pattern gives you "strategic" advantage (pun intended) when you are designing software for evolution. 

The **Strategy Pattern** is a behavioral design pattern that decouples a specific algorithm or logic from the object that uses it. Instead of an object containing a massive, hard-coded decision tree, it delegates the work to a separate "strategy" component. This transforms a monolithic piece of code into a modular system where behaviors are interchangeable parts.

Why
---

Strategy pattern is uniquely useful pattern. It often saves you from implementing code structure that makes it hard to swap implementations. I usually use it for cases when you are doing a prototype of a system, where algorithm that you use may change based on certain conditions. Or when you want to have flexibility to easily swap one implementation with another and iterate with implementations. This pattern has following traits:

-   **Composability & Versatility**: It allows you to build complex behavior by plugging in small, focused components. You can swap a "Production" strategy for a "Test" or "Mock" strategy without changing a single line of the caller's core logic, making the system much easier to manage.

-   **Predictability**: Because each strategy is isolated, it is easier to reason about and debug. You aren't hunting through 500 lines of `if/else` statements to find why a specific branch was taken. Also, you are not modifying one algorithm to turn it to another - it means you do not have to track git history to find where bug happened in time, instead you are localizing it to a specific class.

-   **Domain-driven Design**: Strategies can be named after actual business rules (e.g., `StandardShipping`, `ExpressOvernight`), making the code a direct map of the domain requirements.

### Implementation Trade-offs
There are few implementation of this pattern. I want to demonstrate 4 different implementations and analyze their trade-offs. Here is the summary table for these patterns. In the next section you can find implementations for each.

| Implementation Type | Complexity | Runtime Cost | Flexibility | Best Use Case |
| **Classic (Virtual)** | Medium | V-Table lookup | High (Dynamic) | Plugin systems, GUI event handling. |
| **Template (Mixin)** | High | Zero | Low (Static) | High-performance math or driver code. |
| **Functional** | Low | Small (Type erasure) | Very High | Quick callbacks, local lambda logic. |
| **Policy (Enum)** | Medium | Zero | Medium (Static) | Multi-platform builds, debug vs release. |

How
---

### 1\. Classic Runtime Polymorphism (The Interface Approach)

This uses abstract base classes and virtual functions. It is the most versatile for swapping behavior while the application is already running.

```cpp
#include <memory>

// The Strategy Interface
class IStrategy {
public:
    virtual ~IStrategy() = default;
    virtual void execute() const = 0;
};

// Concrete Implementations
class ConcreteStrategyA : public IStrategy {
    void execute() const override { /* Logic A */ }
};

class Context {
    std::unique_ptr<IStrategy> strategy;
public:
    void set_strategy(std::unique_ptr<IStrategy> s) { strategy = std::move(s); }
    void run() const { if (strategy) strategy->execute(); }
};

```
This is classic implementation and it is great for implementing a plugin systems. You can decide at a runtime which strategy to use. You can delay the strategies available for later, implement them in plugin and add it to the strategy list and select it at runtime as well. Main disadvantage of this pattern is V-table and overhead that comes with it. Second issue is indirection - you can not easily tell which strategy is running at runtime without tracing the call-stack to identify exact type.

### 2\. Template Subclass (The Mixin Approach)

This "injects" the strategy at compile time. It is used when performance is critical and the strategy is known during compilation.

```cpp
template <typename TStrategy>
class Context : private TStrategy {
public:
    void run() {
        // Injects strategy behavior via inheritance or composition
        this->execute();
    }
};

struct FastStrategy {
    void execute() { /* Hyper-optimized logic */ }
};

// Usage: Context<FastStrategy> ctx;

```
This resolves the issues with the classic approach by adding few issues of its own. Yes, it does not have V-table, but strategy must be resolved at runtime. If you swap strategy, you for recompilation. One way to fix this is to use `std::variant` and inject variant to the class without templating, now you can delay strategy usage to runtime:

```cpp


struct FastStrategy {
    void execute() { /* Hyper-optimized logic */ }
};

struct SecureStrategy {
    void execute() { /* Hyper-optimized logic */ }
};

using Strategy = std::variant<FastStrategy, SecureStrategy>;

template
class Context {
  Strategy strategy_;
public:
    void set_strategy(Strategy s) {strategy_ = s;}
    void run() const {
        std::visit([](auto&& s){ s.execute(); };, strategy);
    }

};

```
This implementation provides medium complexity and the best solution for case where set of strategies is finite and known in advance, but selecting strategy needs to be delayed to runtime. Main disadvantage of this technique is memory usage - you will allocate memory for largest variant in strategy. This methods is not as flexible as runtime polymorphism, as you still need to know all variants at compile time. Runtime cost is often really small - normally many variant implementations utilize switch statements for branching logic. 

### 3\. std::function Injection (The Functional Approach)

The most idiomatic "Modern C++" way. It uses type erasure to store any callable (function pointer, lambda, or functor) with a matching signature.

```cpp
#include <functional>

class Context {
    std::function<void()> strategy;
public:
    void set_strategy(std::function<void()> s) { strategy = std::move(s); }
    void run() { if (strategy) strategy(); }
};

// Usage:
// ctx.set_strategy([]{ /* Dynamic Lambda Logic */ });

```
If your strategy stores the data, then this Context can not store that data. So this method is reserved for the cases where you deal with pure algorithms without data. This technique has small runtime overhead due to type erasure. Also, many compilers can not inline the `std::function`. However, this technique is as flexible as classic polymorphism based approach, as you can inject any function at runtime. There is another way to do this with templates as well:

```cpp
class GenericContext {
public:
    template <typename F>
    void run_with_strategy(F&& strategy) {
        // Perfect forwarding to call the strategy
        std::forward<F>(strategy)();
    }
};
// Usage: 
// ctx.run_with_strategy([]{ /* zero-overhead logic */ });
```
Advantages - zero runtime overhead. This provides high flexibility. However, main disadvantage of this technique is that it can easily be abused. Also, it makes such class hard to read. 

### 4\. Policy Pattern (Decoupling Selection from Implementation)

Instead of hard-coding logic, this uses a "Policy" to select or map to a specific "Strategy" type at compile time. This separates the **intent** (Policy) from the **implementation** (Strategy).

```cpp
enum class Policy { Secure, Fast };

// Strategy Implementations
struct AESEncryption { static void process() { /* ... */ } };
struct NoEncryption  { static void process() { /* ... */ } };

// Policy Selector (The Mapping)
template <Policy P> struct PolicyTraits;
template <> struct PolicyTraits<Policy::Secure> { using Strategy = AESEncryption; };
template <> struct PolicyTraits<Policy::Fast>   { using Strategy = NoEncryption;  };

template <Policy P>
class DataHandler {
    // Selects the strategy based on the policy type
    using SelectedStrategy = typename PolicyTraits<P>::Strategy;

public:
    void run() {
        SelectedStrategy::process();
    }
};

// Usage: DataHandler<Policy::Secure> handler;

```

Policy based strategy gives one important advantage over others - it gives you a way to implement new Contexts. As you can see, the DataHandler does not "Store" the Policy, it only references it. Theis resolves the policy at compile time. You can imagine how you can use this to instantiate different Contexts at runtime, similar to `std::variant`. Compiler generates code for policy you actually instantiate, so you can save space by carefully using it. It separates "what" from "how", so `DataHandler` does not know anything about `AESEncryption` class.

Main disadvantage of this technique is the complexity of the structure and dependency on template meta-programming. You are still performing static selection, you can not change strategy of a `DataHandler<Policy::Secure>` object once it has been instantiated. Code bloat - each time you use new policy, the compiler generates new instantiation of the Context. 
