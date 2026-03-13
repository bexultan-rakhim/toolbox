The "Jenga" Theory of Software: Why Your Code Shouldn't Be a String Puppet
==========================================================================

In the physical world, we expect modularity. If you change the tires on a rover, the camera shouldn't suddenly start losing frames. If you upgrade a gripper, you shouldn't have to recalibrate the PID controller for the elbow joint. This independence is what makes complex machines maintainable.

In software, we call this **Orthogonality**.

What
====

In geometry, two lines are orthogonal if they are at right angles ($90^\circ$) to each other. A movement along the $X$-axis results in exactly zero movement along the $Y$-axis. They are completely independent vectors.

In software engineering, orthogonality is a system design principle where changing one component does not affect others.

### Orthogonality vs. SRP

It is often confused with the **Single Responsibility Principle (SRP)**, but the distinction is vital:

-   **SRP** is about **Cohesion**: "Does this module do exactly one thing?" (e.g., A motor driver only drives the motor).

-   **Orthogonality** is about **Coupling**: "If I change the internal logic of the motor driver, does the battery management system break?"

**SRP makes a module specialized; Orthogonality makes it detachable.**

Why
===

In robotics, every design choice has a **Blast Radius**. When something goes wrong---or when a requirement changes---how much of the system gets leveled?

1.  **Reduced Testing Effort:** In an orthogonal system, you only need to test the module you changed. If your "Path Planning" is orthogonal to your "Motor Control," you can verify a new A* algorithm in a simulator without worrying if it will accidentally trigger a "Hardware Emergency Stop" signal.

2.  **Faster Prototyping:** You can swap a LIDAR for a Stereocamera without rewriting the navigation logic.

3.  **Mental Model Simplicity:** You don't have to hold the entire system architecture in your head to fix a single bug.

4.  **No "String Puppets":** In non-orthogonal code, pulling one thread in the UI causes a limb to twitch in the database. Orthogonality cuts those invisible strings.

How
===

The best way to achieve orthogonality is to **design for the divorce.** Assume that every module you write will eventually want to leave and go live on a different robot.

### 1\. Eliminate Global State (The "Hidden Wire")

When two modules share a global variable, they are physically wired together in a way you can't see.

**The Tangled Way (Non-Orthogonal):**

```python
# motor.py
import global_state

def move_motor(velocity):
    # If someone changes the unit of 'current_speed' elsewhere, this breaks
    global_state.current_speed = velocity
    apply_pwm(velocity)

# logger.py
import global_state
def log_status():
    # If the motor module stops updating the global, the logger lies
    print(f"Robot is moving at {global_state.current_speed}")

```

**The Orthogonal Way:**

```python
# motor.py
def move_motor(velocity):
    apply_pwm(velocity)
    return velocity # Return the state, don't push it to a global

# main.py
speed = motor.move_motor(10)
logger.log_status(speed) # Explicit passing of data

```

### 2\. Use Physical Abstractions (The "Interface")

A module shouldn't care *how* another module does its job. It should only care about the contract.

**The Tangled Way:**

```python
def navigation_logic():
    # Navigation needs to know the motor uses PWM frequencies?
    # This is "Helicopter Parenting."
    if distance > 10:
        motor.set_pwm_frequency(5000)

```

**The Orthogonal Way:**

```python
def navigation_logic():
    # Navigation only cares about velocity.
    # How the motor achieves that (PWM, CAN bus, Stepper) is irrelevant.
    if distance > 10:
        motor.set_velocity(1.0)

```

### 3\. The "A-ha" Test

Ask yourself: **"If I move this ROS node to a completely different robot with different hardware, how many lines of code do I have to change?"** If the answer is more than a configuration file, your system is a string puppet. Orthogonality is the art of building a system that can survive its own evolution.

### The Takeaway

-   **What:** Independence of components (the $90^\circ$ rule).

-   **Why:** To limit the "Blast Radius" of bugs and changes.

-   **How:** Encapsulate logic, avoid globals, and communicate via clean, unit-agnostic interfaces
