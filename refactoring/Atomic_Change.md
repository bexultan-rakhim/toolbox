# Atomic Changes
## What
This document introduces a refactoring concept called **atomic change**. Simply put, atomic change is a changes to code that changes the source file and code structure, but **does not change the behavior**. 
## Why
If you start reading any book on refactoring, it will suggest that you should be writing tests to protect correct behavior, so that you can easily modify your code without worrying of breaking anything. Indeed, you should be writing tests. 

However, let's be realistic. More than often than not, you end up in a situation where code you want to refactor is beyond salvation, and writing tests in themselves is a struggle. **How to refactor the code, if it is not even organized in a way to be testable in the first place?** If you have been asking this question, this document is exactly about this topic. So lets clearly define objective of this document.

1. We will try to define an atomic changes - small code modifications safe enough to not require writing tests in advance.
2. We will discuss how to use these steps to extract testable code.

If we can do this, then we can get to point, where regular refactoring techniques become useful again.

> [!WARNING]
> But before going there, I want to give you word of wisdom. Before trying to spend resources untangling a mess, ask yourself: "Is this worth the effort?".
> Remember, point of refactoring is not to achieve some aesthetics. It is about being productive.
> The best way to deal with bad code is not waste time on it. If it is a throwaway code in a long run, consider [putting it into quarantine](https://learn.microsoft.com/en-us/azure/architecture/patterns/anti-corruption-layer).

## How
Let's start to define some of the simpler examples. We will first discuss example with refactoring simple boolean operations.

### 1. Simplifying Boolean Logic
You must memorize these laws by heart. They will help you to simplify complex logic. The most important in this list is De Morgan's laws (8th law), as it can help you simplify really complex expressions.

```python
# Assume 'a', 'b', and 'c' are boolean variables
a = True
b = False
c = True

# 1. Identity Laws
identity_and = (a and True) == a
identity_or  = (a or False) == a

# 2. Null (Annulment) Laws
null_and = (a and False) == False
null_or  = (a or True) == True

# 3. Idempotent Laws
idempotent_and = (a and a) == a
idempotent_or  = (a or a) == a

# 4. Complement Laws
complement_and = (a and not a) == False
complement_or  = (a or not a) == True

# 5. Double Negation
double_negation = (not (not a)) == a

# 6. Commutative Laws
commute_and = (a and b) == (b and a)
commute_or  = (a or b) == (b or a)

# 7. Distributive Laws
distribute_1 = (a and (b or c)) == ((a and b) or (a and c))
distribute_2 = (a or (b and c)) == ((a or b) and (a or c))

# 8. De Morgan's Laws
de_morgan_1 = (not (a and b)) == (not a or not b)
de_morgan_2 = (not (a or b)) == (not a and not b)

# 9. Absorption Laws
absorb_1 = (a or (a and b)) == a
absorb_2 = (a and (a or b)) == a
```
Easy right? Let's go further.

### 2. Simplifying Complex if-statements:
1. Return Early pattern:
```python
# Ugly nested if conditions
def upload_file(request):
    if request.method == "POST":
        if request.user.is_authenticated:
            if 'file' in request.FILES:
                # Actual logic buried here
                return "Success"
            else:
                return "No file"
        else:
            return "Unauthorized"
    return "Invalid Method"

# Flatter and Readable, yet same logic
def upload_file(request):
    if request.method != "POST":
        return "Invalid Method"
    if not request.user.is_authenticated:
        return "Unauthorized"
    if 'file' not in request.FILES:
        return "No file"

    # Actual logic starts here at the top level
    return "Success"
```
2. Remove Useless Else:
```python
def get_user_tier(points):
    if points > 1000:
        tier = "Gold"
    elif points > 500:
        tier = "Silver"
    else:
        tier = "Bronze"
    return tier

# This is the same logic
def get_user_tier(points):
    if points > 1000:
        return "Gold"
    if points > 500:
        return "Silver"
    return "Bronze"
```

3. Explain Variable:
```python
# What does this logic actually mean?
if (order.total > 100 and user.is_member) or (order.has_promo and not order.is_discounted):
    apply_free_shipping(order)

# Self-Documenting Code
is_high_value_member = order.total > 100 and user.is_member
is_eligible_promo = order.has_promo and not order.is_discounted

if is_high_value_member or is_eligible_promo:
    apply_free_shipping(order)
```

4. The Consolidation Law:
```python
# Before (Nested)
if user.is_logged_in:
    if user.has_permission:
        if settings.notifications_enabled:
            send_alert()

# After (Consolidated)
if user.is_logged_in and user.has_permission and settings.notifications_enabled:
    send_alert()

# Instead of one giant line:
can_receive_alert = (
    user.is_logged_in and 
    user.has_permission and 
    settings.notifications_enabled
)
if can_receive_alert:
    send_alert()
```
But be careful of cases like these:
```python
if user.is_logged_in:
    log_access_attempt()  # <--- This "interstitial" code prevents a simple merge
    if user.has_permission:
        open_dashboard()
```
