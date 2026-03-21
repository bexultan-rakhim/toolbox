Code Duplication Is Not Bad - It's a Tradeoff
=============================================
What
----
If you take anything from this article, then I want it to be this mantra:

**Duplication is FAR cheaper than the WRONG abstraction.**

Today's topic of discussion, in essence, is **accidental coupling**.

Why
---
Maybe you have seen or heard this dogma: **DRY** - don't repeat yourself. There is a lot of wisdom in reducing duplication. In many cases, you should strive to reduce duplication, or better to say - do not reinvent the wheel.

However, remember the mantra above - **WRONG abstractions are not cheap!**

Let's check one simple example here. Look at this simple class:

```python
import requests

class SensorDataClient:
    def get_lidar_scan(self, scan_id):
        # Specific logic for LiDAR scans
        url = f"https://api.robot.internal/v1/lidar/{scan_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_imu_reading(self, reading_id):
        # Specific logic for IMU readings
        url = f"https://api.robot.internal/v1/imu/{reading_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()
```

This is a simple client for a service that manages LiDAR scans and IMU readings. Currently, the logic for fetching them is almost identical. Watch this. Here is what happens if you try to DRY.

```python
import requests

class SensorDataClient:
    def _fetch_sensor_data(self, sensor_type, data_id):
        url = f"https://api.robot.internal/v1/{sensor_type}/{data_id}"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return response.json()

    def get_lidar_scan(self, scan_id):
        return self._fetch_sensor_data("lidar", scan_id)

    def get_imu_reading(self, reading_id):
        return self._fetch_sensor_data("imu", reading_id)
```

This is a logical change, if you are in a current time frame.

This is exactly the same code, with little duplication. But, the world of programming would have been simple, if not for one small fact - **requirements change**. You see, they also change in a direction where you may not have expected. This change comes with uncertainty on how services evolve in the long run. So, imagine this request for change: the safety team decides that LiDAR scans now require a **signed hardware certificate** for tamper detection, but IMU readings remain unauthenticated internal data. So, out of necessity to satisfy this requirement you now have to bloat `_fetch_sensor_data` to handle the two sensors differently:

```python
def _fetch_sensor_data(self, sensor_type, data_id, cert=None):
    url = f"https://api.robot.internal/v1/{sensor_type}/{data_id}"
    headers = {"X-Hardware-Cert": cert} if cert else {}
    response = requests.get(url, timeout=5, headers=headers)
    response.raise_for_status()
    return response.json()
```

Think why the API has to be in this form for a second.

This is the trap of incorrect abstractions. If you had kept the original duplication, you could be in a better place to evolve the LiDAR and IMU clients separately in a much more cohesive way. But now, you have a complex two-sided issue that has to be solved both on server and client side. LiDAR is safety-critical hardware with certification requirements. IMU is internal telemetry. They were never the same thing — they just happened to look the same on a Tuesday.

In fact, there was a bigger architectural trap of exactly this form — systems built around reducing duplication at all costs: [Service Oriented Architecture](https://en.wikipedia.org/wiki/Service-oriented_architecture). Check the Wikipedia section on criticisms. It is a good read on why the industry moved from that bloatware toward microservices.

How
---
Question of the day: **How to avoid wrong abstractions?**

Avoiding wrong abstractions is an exercise of **restraint**. You have to learn to be pragmatic — what Joel Spolsky calls the [Duct Tape Programmer](https://www.joelonsoftware.com/2009/09/23/the-duct-tape-programmer/) approach. Form should follow function, not form over function.

### 1. The Rule of Three

Martin Fowler codified this heuristic in [Refactoring: Improving the Design of Existing Code](https://martinfowler.com/books/refactoring.html), and it remains the gold standard for avoiding premature abstraction.

- 1st time: Just write the code.
- 2nd time: You feel a twinge of guilt, but you duplicate it anyway.
- 3rd time: Now that you have three distinct use cases, the actual pattern becomes visible.

### 2. Identify "Similarity" vs "Identity"

Before you unify two functions, ask yourself: "Do these change for the same reason?" This is the Single Responsibility Principle — articulated by Robert C. Martin in [Clean Code](https://www.oreilly.com/library/view/clean-code-a/9780136083238/) — in disguise.

- **Similarity**: Both a joint limit check and a workspace boundary check return a boolean and log a warning on failure.
- **Identity**: They are both "Safety Constraint Validators."
- **The Trap**: If you create a single `SafetyConstraintValidator` abstraction, what happens when joint limits need to account for thermal expansion at runtime? You have coupled two unrelated physical constraints because they happened to look the same on Tuesday.

### 3. Design for Deletion, Not Reuse

We often build abstractions as if they are permanent monuments. Instead, build them to be **disposable**. Sandi Metz put this best in her talk [All the Little Things](https://www.youtube.com/watch?v=8bZh5LMaSmE): prefer duplication over the wrong abstraction.

- Keep your abstractions shallow. Don't wrap a driver (like a CAN bus interface) in three layers of your own custom classes.
- If an abstraction is easy to delete, it is a good abstraction. If deleting it requires a 4-hour refactor of the entire codebase, you have built a "Wrong Abstraction" cage.

---
Sources
-------
- Spolsky, J. (2009). [The Duct Tape Programmer](https://www.joelonsoftware.com/2009/09/23/the-duct-tape-programmer/). Joel on Software. — Source of the pragmatism-first philosophy referenced in the How section.
- Fowler, M. (2018). *Refactoring: Improving the Design of Existing Code* (2nd ed.). Addison-Wesley. — Source of the Rule of Three heuristic.
- Martin, R. C. (2008). *Clean Code: A Handbook of Agile Software Craftsmanship*. Prentice Hall. — Source of the Single Responsibility Principle referenced in point 2.
- Metz, S. (2014). [All the Little Things](https://www.youtube.com/watch?v=8bZh5LMaSmE). RailsConf 2014. — Source of "duplication is far cheaper than the wrong abstraction"; the talk that popularized this framing.
