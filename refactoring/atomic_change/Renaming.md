Naming and Self-Documenting Code
================================

Renaming is the ultimate atomic change. Thanks to modern IDEs (where renaming a variable or function is as simple as pressing `F2` or `Shift+F6`), you can instantly improve the clarity of your code across an entire project with zero risk of breaking behavior.

A core philosophy of clean code is: **Code should explain exactly what it does. Comments should only explain** ***why*** **it does it.** If you have to write a comment to explain *what* a block of code is doing, you usually just have a naming problem.

Here are the atomic changes you can apply to make your code self-documenting.

### 1\. Replace Comment with Variable Name

If you find yourself writing a comment above a complex `if` condition or mathematical calculation, extract that logic into a variable and use the comment as the variable's name.

```cpp
// BEFORE (Comment acts as a crutch for bad code)

// Check if we have enough stock and the account is in good standing
if (item.stock >= order.qty && account.balance >= order.total && account.status == 1) {
    shipOrder();
}

// AFTER (The code speaks for itself)

bool hasEnoughStock = item.stock >= order.qty;
bool isAccountInGoodStanding = (account.balance >= order.total) && (account.status == STATUS_ACTIVE);

if (hasEnoughStock && isAccountInGoodStanding) {
    shipOrder();
}

```

### 2\. Replace Comment with Function Name

Similar to variables, if you have a chunk of code preceded by a comment explaining what the chunk does, that is a massive red flag. Extract that chunk into its own function, and name the function exactly what the comment said.

```cpp
// BEFORE
void calculateFinalPrice(Order& order) {
    // 1. Apply loyalty tier discount
    if (order.customer.yearsActive > 5) {
        order.price *= 0.90;
    } else if (order.customer.yearsActive > 2) {
        order.price *= 0.95;
    }

    // 2. Add shipping costs based on region
    if (order.region == "US") {
        order.price += 5.00;
    } else {
        order.price += 15.00;
    }
}

// AFTER
void calculateFinalPrice(Order& order) {
    applyLoyaltyDiscount(order);
    addShippingCosts(order);
}

```

### 3\. Rename Variable to Reveal Intent (Kill Abbreviations)

In the 1980s, screens were small and memory was expensive. Today, there is absolutely no excuse for using single-letter variables or cryptic abbreviations (with the exception of standard loop iterators like `i` or `j`). If a variable requires a comment to explain its abbreviation, rename it.

```cpp
// BEFORE
int d;      // elapsed time in days
int tm;     // timeout in milliseconds
bool isAuth;// is user authenticated?

// AFTER
int elapsedDays;
int timeoutMilliseconds;
bool isUserAuthenticated;

```

### 4\. Rename Function to Expose Side-Effects (No Surprises)

A function's name must describe *everything* it does. If a function returns a value but also mutates state behind the scenes, its name must reflect that, or it becomes a trap for the next developer.

```cpp
// BEFORE: Sounds like a harmless query, but it actually creates a database record!
User getUser(const std::string& email) {
    User u = db.find(email);
    if (!u.exists()) {
        u = db.create(email); // SIDE EFFECT!
    }
    return u;
}

// AFTER: The name warns the caller of the behavior.
User getOrCreateUser(const std::string& email) {
    User u = db.find(email);
    if (!u.exists()) {
        u = db.create(email);
    }
    return u;
}

```

### 5\. Remove "Weasel Words" (Manager, Data, Info, Processor)

Generic words are a symptom of a poorly defined concept. If you name a class `UserData`, what does it hold? Passwords? Display names? Purchase history? If you name a class `TaskProcessor`, what is it actually doing?

Renaming generic concepts into specific domain terms makes the architecture significantly easier to understand.

```cpp
// BEFORE (Vague, "Weasel" names)
class UserInfo { ... };
class ConnectionManager { ... };
class EventProcessor { ... };

// AFTER (Specific, Domain-based names)
class UserCredentials { ... };
class ConnectionPool { ... };
class EventDispatcher { ... }; // or EventQueue, depending on what it actually does

```
