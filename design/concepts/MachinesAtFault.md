There Is No Such Thing as User Error
=====================================

What
----

When a autonomous car does the wrong thing, the first question in most teams is: what did the driver do wrong?

The assumption underneath that question is that machines are correct by default. They execute exactly what they were specified to do. So if the outcome was wrong, the person must have deviated.

Don Norman dismantles this in *The Design of Everyday Things*. His argument: if a user interacts with a system in a way the designer did not intend, that is not a user error — it is a design error. The system failed to constrain misuse, or failed to make the correct path obvious. The fault traces back to whoever wrote the specification. Which is always a human.

Norman calls this **system-induced error**. We usually call it user error. We are usually mistaken.

**There is no such thing as true user error**

Why
---

Robotics engineers are especially prone to this blind spot.

A robot arm follows its joint commands exactly. A motion planner returns the path it was asked for. When an operator sends a command and the arm hits a fixture, the engineer's instinct is: "they sent the wrong pose." And technically, yes. But why was the wrong pose sendable without warning? Why did the interface not show the operator what the arm was about to do before it moved? Why was there no collision check between intent and execution?

The specification permitted the error. The operator just triggered it.

Teams that close incidents as "operator error" stop looking for the design flaw underneath. The same class of incident recurs. The system accumulates sharp edges that only experienced operators — the ones who built up enough scar tissue — know to avoid. New operators keep getting hurt by the same problems.

You get your infallible logic sure, but fail to make something better: intuitive, clear, safe and easy to use. We have many junk that is difficult to use. We need no more. Let us be humble in our endeavor and when we see people fail to grasp our great design, we should put our pride aside and say ourselves that this is not as good of a design as we thought. 

How
---

### Trace every incident to a design decision

A robot on a factory floor grazes a worker's hand. The investigation finds the operator set a waypoint too close to the human workspace. Standard conclusion: operator error.

Better question: why could that waypoint be set there at all? Why did the teach pendant not flag it as inside the human zone? Why did the robot not slow down when entering a proximity threshold? The operator made a mistake, but the system had no layer to catch it.

Every incident has a design decision underneath it. Find that decision. If traceability to design decisions are impossible, make revisions to make it possible.

### Constraints over instructions

Norman distinguishes *knowledge in the world* from *knowledge in the head*. A manual loads knowledge into the operator's head. A physical or software constraint puts it into the system itself.

A drone that refuses to arm without GPS lock does not require the pilot to remember to check GPS. The constraint is in the world. A robot cell with light curtains that halt motion when broken does not rely on the operator staying alert — the curtain is the constraint.

Compare that to a robot whose safe operating zone is documented in a README. The operator has to remember it, apply it correctly, every time, under pressure. That is knowledge in the head. It will fail.

If operators keep making the same mistake, a bigger warning label is the wrong fix. Remove the ability to make the mistake, or make recovery immediate.

### Distinguish slips from mistakes

Norman draws a line between two failure types.

A **slip**: the operator knows the right action but executes the wrong one. They meant to jog X+ and hit X−. The robot moved into the fixture. This is not ignorance — it is a motor error, distraction, or a badly laid-out pendant.

A **mistake**: the operator has the wrong mental model. They believe the robot's coordinate frame is world-fixed, but it is tool-fixed. Every command they send is based on that wrong model.

These need different fixes. Slips are addressed by separating axes physically, adding dead-man switches, making destructive jogs require held confirmation. Mistakes are addressed by making the system's actual state visible — show the frame, show the pose in the workspace, show what the robot understood before it moves.

### Read error patterns as design signals

If the same type of incident keeps appearing in your logs — operators jogging in the wrong frame, setting waypoints outside the safe zone, triggering e-stops by accident — that is the system telling you something about its own interface.

It is not evidence that operators need more training. It is a specification review waiting to happen.

---

Robots do exactly what they are told. When they cause harm, the responsibility traces back through the specification to the people who wrote it. Operators are not the last line of defence against bad design. They are the people the design is supposed to serve.

References
----------

[1] Norman, D. A. (2013). *The Design of Everyday Things* (Revised and expanded edition). Basic Books.

