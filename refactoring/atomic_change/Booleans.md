Simplifying Boolean Logic
=========================

You must memorize these laws by heart. They will help you to spot overly complex logic and reduce it to its simplest form. This is the essence of an atomic change: replacing a noisy expression with a shorter, mathematically equivalent one without altering the program's behavior.

The most important in this list are **De Morgan's laws** (8th law) and the **Absorption laws** (9th law), as they can help you drastically simplify deeply nested or confusing conditions.

Here are the boolean laws in C++, demonstrating the "Complex" version you might find in legacy code, and the "Simplified" version you should refactor it into.

```Cpp
bool isValid = true;
bool isReady = false;
bool isAdmin = true;

// 1. Identity Laws: Removing redundant constants
// BEFORE                            // AFTER
bool r1 = (isValid && true);         bool r1 = isValid;
bool r2 = (isValid || false);        bool r2 = isValid;

// 2. Null (Annulment) Laws: Recognizing hardcoded outcomes
// BEFORE                            // AFTER
bool r3 = (isValid && false);        bool r3 = false;
bool r4 = (isValid || true);         bool r4 = true;

// 3. Idempotent Laws: Removing duplicated checks
// BEFORE                            // AFTER
bool r5 = (isValid && isValid);      bool r5 = isValid;
bool r6 = (isValid || isValid);      bool r6 = isValid;

// 4. Complement Laws: Spotting impossible or guaranteed conditions
// BEFORE                            // AFTER
bool r7 = (isValid && !isValid);     bool r7 = false;
bool r8 = (isValid || !isValid);     bool r8 = true;

// 5. Double Negation: Removing unnecessary mental gymnastics
// BEFORE                            // AFTER
bool r9 = !(!isValid);               bool r9 = isValid;

// 6. Commutative Laws: Reordering for readability
// BEFORE                            // AFTER
bool r10 = (isReady && isValid);     bool r10 = (isValid && isReady);

// 7. Distributive Laws: "Factoring out" common variables
// BEFORE
bool canEdit = (isAdmin && isReady) || (isAdmin && isValid);
// AFTER
bool canEdit = isAdmin && (isReady || isValid);

// 8. De Morgan's Laws: Untangling complex negations
// Example A: Pushing negations inward
// BEFORE
bool isBlocked = !(isReady || isAdmin);
// AFTER
bool isBlocked = !isReady && !isAdmin;

// Example B: Eliminating negative chains
// BEFORE
bool canProceed = !(!isValid || !isReady);
// AFTER
bool canProceed = isValid && isReady;

// 9. Absorption Laws: Removing swallowed conditions
// BEFORE
bool r11 = isValid || (isValid && isReady);
// AFTER
bool r11 = isValid;

// BEFORE
bool r12 = isValid && (isValid || isReady);
// AFTER
bool r12 = isValid;

```

Easy, right?
