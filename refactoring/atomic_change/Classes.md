Classes and Composition
=======================

**A Quick Caveat:** Class structure and overall architecture are fundamentally deep design problems. True architectural refactoring requires careful planning and often breaks existing interfaces. The patterns outlined below are meant to be "easy wins"---safe, atomic changes that untangle localized messes and nudge your code toward a better design without requiring a massive, risky system rewrite.

When it comes to structuring your data and behavior, traditional object-oriented design often pushes you towards deep inheritance hierarchies (the "SOLID" way). However, modern software engineering often favors the **CUPID** properties: code that is *Composable*, follows the *Unix philosophy* (does one thing well), is *Predictable*, *Idiomatic*, and *Domain-based*.

Deep inheritance makes code unpredictable and rigid. The atomic changes below focus on flattening hierarchies, favoring composition, and pushing logic into clear, predictable functions.

### 1\. Replace Inheritance with Composition (Composable)

Inheritance forces an "IS-A" relationship, which often breaks down as requirements change (e.g., the classic "fragile base class" problem). Composition uses a "HAS-A" relationship, allowing you to mix and match behaviors like Lego bricks.

```cpp
// BEFORE (Rigid Inheritance Hierarchy)
class Character {
public:
    virtual void move() = 0;
};

class FlyingEnemy : public Character {
public:
    void move() override {
        // Complex 3D flight logic
    }
};

// AFTER (Composition: Plug-and-play behaviors)
struct Transform {
    float x, y, z;
};

// Unix philosophy: This function does one thing---moves something flying.
void updateFlight(Transform& t) {
    // Complex 3D flight logic applied to the transform
}

struct Enemy {
    Transform transform;
    bool canFly = true;
};

void updateEnemy(Enemy& enemy) {
    if (enemy.canFly) {
        updateFlight(enemy.transform);
    }
}

```

### 2\. Replace Virtual Methods with Functions (Predictable & Composable)

Instead of creating a new subclass every time you want to change a tiny piece of behavior, use `std::function` or function pointers. This allows you to inject behavior at runtime without the boilerplate of virtual tables and derived classes.

```cpp
// BEFORE (Heavy Polymorphism)
class TaxCalculator {
public:
    virtual double calculate(double amount) = 0;
    virtual ~TaxCalculator() = default;
};

class USATaxCalculator : public TaxCalculator {
public:
    double calculate(double amount) override { return amount * 1.08; }
};

// AFTER (Idiomatic C++ using std::function)
#include <functional>

struct Order {
    double amount;
    std::function<double(double)> taxStrategy;
};

// Just pure, predictable functions
double calcUSATax(double amount) { return amount * 1.08; }
double calcUKTax(double amount) { return amount * 1.20; }

void processOrder(Order& order) {
    double finalPrice = order.taxStrategy(order.amount);
}

// Usage: order.taxStrategy = calcUSATax;

```

### 3\. Extract Struct for Data Clumps (Domain-based)

If you see the same 3 or 4 variables being passed around together to multiple functions, they belong to the same domain concept. Grouping them into a simple `struct` makes your function signatures cleaner and the domain clearer.

```cpp
// BEFORE (Primitive Obsession & Data Clumps)
void spawnParticle(float x, float y, float z, float vx, float vy, float vz, int lifetime) {
    // ...
}

void updateParticle(float& x, float& y, float& z, float vx, float vy, float vz) {
    // ...
}

// AFTER (Domain-based structures)
struct Vector3 {
    float x, y, z;
};

struct Particle {
    Vector3 position;
    Vector3 velocity;
    int lifetime;
};

void spawnParticle(const Particle& templateParticle) {
    // ...
}

void updateParticle(Particle& particle) {
    // ...
}

```

### 4\. Move Hidden State to Explicit Parameters (Predictable)

Classes that mutate their own hidden state based on internal logic are hard to test and reason about. You can apply an atomic change to extract that logic into a "pure" free function that takes inputs and returns outputs, making the behavior 100% predictable.
Plus, this makes the logic easily testable. Point here is that by separating logic from data, you are not compromising testability and encapsulation. Oftentimes, you see people using `friend` classes or mocks to test such complex logic, which is arguably worse.

```cpp
// BEFORE (Unpredictable state mutation)
class ShoppingCart {
private:
    std::vector<Item> items;
    double totalDiscount = 0.0;

public:
    void applyDiscounts() {
        // Modifies internal state directly. Hard to test without a full Cart setup.
        if (items.size() > 5) {
            totalDiscount = 0.10;
        }
    }
};

// AFTER (Predictable pure function)
// The logic is decoupled from the class state. Extremely easy to test.
double calculateDiscount(int itemCount) {
    if (itemCount > 5) return 0.10;
    return 0.0;
}

class ShoppingCart {
private:
    std::vector<Item> items;
    double totalDiscount = 0.0;

public:
    void applyDiscounts() {
        // State mutation is explicit and delegates to the pure function
        totalDiscount = calculateDiscount(items.size());
    }
};

```

### 5\. Replace Classes with Namespaces (Unix Philosophy)

If a class only contains `static` methods and has no state (no member variables), it shouldn't be a class at all. C++ has namespaces for grouping related functions.

```cpp
// BEFORE (Using classes as Java-style static containers)
class MathUtils {
public:
    static double clamp(double val, double min, double max) {
        if (val < min) return min;
        if (val > max) return max;
        return val;
    }
};

// AFTER (Idiomatic C++ grouping)
namespace MathUtils {
    double clamp(double val, double min, double max) {
        if (val < min) return min;
        if (val > max) return max;
        return val;
    }
}

```
