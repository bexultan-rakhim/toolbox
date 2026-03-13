Common Easy Fixes
=================

Not every atomic change involves rewriting control flow or extracting functions. Sometimes, the biggest readability gains come from cleaning up the smallest details: the variables and values themselves.

Here are some common, easy fixes you should apply whenever you spot them.

### 1\. Replace Magic Number (or String) with Named Constant

"Magic numbers" are raw numbers or strings hardcoded directly into the logic. They force the reader to guess *why* that specific value is there. Replacing them with named constants (using `constexpr` or `const` in C++) gives the value immediate meaning.

```cpp
// BEFORE (What is 9.81? What is 4?)
double calculateDropTime(double height) {
    return std::sqrt((2 * height) / 9.81);
}

void processTask(const Task& task) {
    if (task.status == 4) {
        startTask();
    }
}

// AFTER (Self-Documenting)
constexpr double GRAVITY_MS2 = 9.81;
constexpr int STATUS_READY = 4;

double calculateDropTime(double height) {
    return std::sqrt((2 * height) / GRAVITY_MS2);
}

void processTask(const Task& task) {
    if (task.status == STATUS_READY) {
        startTask();
    }
}

```

### 2\. Replace Type Code with Enums

Taking "Magic Numbers" a step further: if you have a variable that represents a specific set of states (like status codes, roles, or types), don't use raw integers or strings. C++ `enum class` provides type safety and makes invalid states impossible to compile.

```cpp
// BEFORE (Vulnerable to typos and invalid values like setRole(99))
void setRole(int roleType) {
    if (roleType == 1) {
        // ... grant admin rights
    }
}

// AFTER (Type-safe and clear)
enum class Role {
    Guest,
    Admin,
    SuperUser
};

void setRole(Role roleType) {
    if (roleType == Role::Admin) {
        // ... grant admin rights
    }
}

```

### 3\. Split Temporary Variable

If you see a temporary variable being assigned to more than once (unless it's a loop counter or a running total), it means it has multiple responsibilities. Reusing a variable like `temp` or `result` saves a tiny bit of memory but completely destroys readability. Split it into distinct variables with clear names.

```cpp
// BEFORE (Reusing 'temp' for entirely different concepts)
void printGeometry(double height, double width) {
    double temp = 2 * (height + width);
    std::cout << "Perimeter: " << temp << "\n";

    temp = height * width;
    std::cout << "Area: " << temp << "\n";
}

// AFTER (Distinct variables for distinct concepts)
void printGeometry(double height, double width) {
    double perimeter = 2 * (height + width);
    std::cout << "Perimeter: " << perimeter << "\n";

    double area = height * width;
    std::cout << "Area: " << area << "\n";
}

```

### 4\. Inline Variable

This is the opposite of extracting a variable. Sometimes developers create variables that are assigned exactly once and then immediately returned or used. If the variable name doesn't add any extra context that the function call itself doesn't already provide, just inline it to remove the noise.

```cpp
// BEFORE (Useless temporary variables)
bool isEligibleForDiscount(const Order& order) {
    double basePrice = order.getBasePrice();
    return basePrice > 100.0;
}

// AFTER (Direct and clean)
bool isEligibleForDiscount(const Order& order) {
    return order.getBasePrice() > 100.0;
}

```

### 5\. Encapsulate Global/Public State

While larger than a simple variable rename, directly accessing public members or global variables makes tracking where data changes impossible. Wrapping them in getters/setters (or entirely moving the logic into the class) is a crucial atomic change to regain control of your data.

```cpp
// BEFORE (Uncontrolled modification)
struct Player {
    int health;
};

void takeDamage(Player& player, int damage) {
    player.health -= damage;
    if (player.health < 0) {
        player.health = 0;
    }
}

// AFTER (Controlled modification inside the class)
class Player {
private:
    int health;
public:
    void takeDamage(int damage) {
        health -= damage;
        if (health < 0) {
            health = 0;
        }
    }
};

```
