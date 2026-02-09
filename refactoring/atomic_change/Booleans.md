# Simplifying Boolean Logic
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

Easy, right?
