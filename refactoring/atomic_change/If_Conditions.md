# Simplifying Complex if-statements:
Patterns here exclusively about simplifying if/else conditions.

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

