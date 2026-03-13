Refactoring Functions
=====================

Once your boolean logic and `if` conditions are simplified, the next step is to look at the structure of your functions. These atomic changes focus on organizing code into logical, bite-sized pieces that are easy to name, reuse, and - most importantly - test.

### 1\. Extract Function

This is the most common atomic change. When a function grows too large or contains a block of code that requires a comment to explain *what* it does, that block should be extracted into its own function.

```cpp
// BEFORE
void printReceipt(const Order& order) {
    // Print banner
    std::cout << "*****************************\n";
    std::cout << "**** STORE RECEIPT    ****\n";
    std::cout << "*****************************\n";

    // Print details
    std::cout << "Amount: $" << order.amount << "\n";
    std::cout << "Date: " << order.date << "\n";
}

// AFTER
void printBanner() {
    std::cout << "*****************************\n";
    std::cout << "**** STORE RECEIPT    ****\n";
    std::cout << "*****************************\n";
}

void printDetails(const Order& order) {
    std::cout << "Amount: $" << order.amount << "\n";
    std::cout << "Date: " << order.date << "\n";
}

void printReceipt(const Order& order) {
    printBanner();
    printDetails(order);
}

```

### 2\. Inline Function

The exact opposite of Extract Function. Sometimes, a function's body is just as clear as its name, or an old refactoring created too much unnecessary indirection. If the function isn't hiding any complexity, inline it.

```cpp
// BEFORE
bool isMoreThanFive(int rating) {
    return rating > 5;
}

void evaluateDriver(int rating) {
    if (isMoreThanFive(rating)) {
        giveBonus();
    }
}

// AFTER
void evaluateDriver(int rating) {
    if (rating > 5) {
        giveBonus();
    }
}

```

### 3\. Separate Query from Modifier (Command-Query Separation)

A function should either answer a question (return a value) or do something (change state/modify data), but **never both**. Functions that do both are notoriously difficult to test because you can't check the value without accidentally triggering the side-effect.

```cpp
// BEFORE: Checking the password also logs the user in (side-effect!)
bool checkPasswordAndLogin(const User& user, const std::string& password) {
    if (user.password == hash(password)) {
        Session::start(user.id); // < -  Side effect!
        return true;
    }
    return false;
}

// AFTER: Separated into a pure query and a distinct action
bool isPasswordValid(const User& user, const std::string& password) {
    return user.password == hash(password); // Safe to test anytime
}

void loginUser(const User& user) {
    Session::start(user.id);
}

```

### 4\. Split Phase

If a function does two completely different things sequentially (like parsing raw data, and then doing math on it), split it into two distinct phases. You can pass the output of the first phase as the input to the second.

```cpp
// BEFORE: Parsing and calculating are tangled together
double calculateTotalScore(const std::string& rawData) {
    // Phase 1: Parse
    std::vector<int> scores;
    std::stringstream ss(rawData);
    std::string item;
    while (std::getline(ss, item, ',')) {
        scores.push_back(std::stoi(item));
    }

    // Phase 2: Calculate
    double total = 0;
    for (int score : scores) {
        total += score;
    }
    return total;
}

// AFTER: Two distinct, highly testable functions
std::vector<int> parseScores(const std::string& rawData) {
    std::vector<int> scores;
    std::stringstream ss(rawData);
    std::string item;
    while (std::getline(ss, item, ',')) {
        scores.push_back(std::stoi(item));
    }
    return scores;
}

double sumScores(const std::vector<int>& scores) {
    double total = 0;
    for (int score : scores) {
        total += score;
    }
    return total;
}

// The main function just coordinates them
double calculateTotalScore(const std::string& rawData) {
    std::vector<int> scores = parseScores(rawData);
    return sumScores(scores);
}

```

### 5\. Replace Inline Code with Function Call

Often, developers write custom logic to achieve something that a standard library or an existing utility function already handles. Replacing manual logic with an existing function call removes cognitive load and reduces the surface area for bugs.

```cpp
// BEFORE: Manual lookup
bool isFound = false;
for (int id : userIds) {
    if (id == targetId) {
        isFound = true;
        break;
    }
}

// AFTER: Relying on the standard library
bool isFound = std::find(userIds.begin(), userIds.end(), targetId) != userIds.end();

```

### 6\. Replace Loop with Pipeline / Algorithm

Loops are imperative - they tell you *how* something is being done. Using standard algorithms (like `std::any_of`, `std::count_if`, or `std::accumulate` in C++) makes your code declarative - it tells you *what* is being done. This is a very safe and powerful atomic change.

```cpp
// BEFORE: Manual loop to check a condition
bool hasActiveUser = false;
for (const auto& user : users) {
    if (user.isActive) {
        hasActiveUser = true;
        break;
    }
}

// AFTER: Declarative algorithm
bool hasActiveUser = std::any_of(users.begin(), users.end(),
                                 [](const User& u) { return u.isActive; });

```
