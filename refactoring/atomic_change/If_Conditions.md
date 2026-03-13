Simplifying Complex If-Statements
=================================

These patterns focus exclusively on simplifying `if/else` conditions. By restructuring your control flow, you can make the "happy path" of your code much clearer and reduce indentation depth.

### 1\. Return Early Pattern (Guard Clauses)

Deeply nested conditions are hard to read. By inverting the conditions and returning early, you can keep your main logic at the top level of the function.

```cpp
// BEFORE (Deeply Nested)
std::string uploadFile(const Request& req) {
    if (req.method == "POST") {
        if (req.user.isAuthenticated) {
            if (req.hasFile("file")) {
                // Actual logic buried here
                return "Success";
            } else {
                return "No file";
            }
        } else {
            return "Unauthorized";
        }
    }
    return "Invalid Method";
}

// AFTER (Flat and Readable)
std::string uploadFile(const Request& req) {
    if (req.method != "POST") {
        return "Invalid Method";
    }
    if (!req.user.isAuthenticated) {
        return "Unauthorized";
    }
    if (!req.hasFile("file")) {
        return "No file";
    }

    // Actual logic starts here at the top level
    return "Success";
}

```

### 2\. Remove Useless Else

If an `if` block returns or breaks, you don't need an `else` block. This eliminates unnecessary state variables and indentation.

```cpp
// BEFORE (Using a state variable)
std::string getUserTier(int points) {
    std::string tier;
    if (points > 1000) {
        tier = "Gold";
    } else if (points > 500) {
        tier = "Silver";
    } else {
        tier = "Bronze";
    }
    return tier;
}

// AFTER (Direct returns)
std::string getUserTier(int points) {
    if (points > 1000) {
        return "Gold";
    }
    if (points > 500) {
        return "Silver";
    }
    return "Bronze";
}

```

### 3\. Explain Variable

Complex boolean expressions inside an `if` statement can be hard to parse mentally. Extracting them into well-named boolean variables makes the code self-documenting.

```cpp
// BEFORE (What does this logic actually mean?)
if ((order.total > 100 && user.isMember) || (order.hasPromo && !order.isDiscounted)) {
    applyFreeShipping(order);
}

// AFTER (Self-Documenting Code)
bool isHighValueMember = (order.total > 100 && user.isMember);
bool isEligiblePromo = (order.hasPromo && !order.isDiscounted);

if (isHighValueMember || isEligiblePromo) {
    applyFreeShipping(order);
}

```

### 4\. The Consolidation Law

If you have a sequence of nested `if` statements with no intermediate code between them, they can be consolidated into a single condition using the `&&` operator.

```cpp
// BEFORE (Nested)
if (user.isLoggedIn) {
    if (user.hasPermission) {
        if (settings.notificationsEnabled) {
            sendAlert();
        }
    }
}

// AFTER (Consolidated)
if (user.isLoggedIn && user.hasPermission && settings.notificationsEnabled) {
    sendAlert();
}

// ALTERNATIVE AFTER (Combined with "Explain Variable")
bool canReceiveAlert = user.isLoggedIn && user.hasPermission && settings.notificationsEnabled;

if (canReceiveAlert) {
    sendAlert();
}

```

**Caution:** Be careful when there is intermediate code. You cannot safely consolidate if statements if code executes between them.

```cpp
// CAUTION: Interstitial code prevents a simple merge
if (user.isLoggedIn) {
    logAccessAttempt(); // <--- This prevents consolidating the if-statements
    if (user.hasPermission) {
        openDashboard();
    }
}

```
