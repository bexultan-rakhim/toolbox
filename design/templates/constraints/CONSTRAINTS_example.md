CONSTRAINTS for: motor-controller-service
Last updated: 2025-11-01
Owned by: robotics-platform-team

---

CONTRACT: Velocity Command Interface with Navigation Stack
- This service subscribes to /cmd_vel (geometry_msgs/Twist) from the navigation
  stack. The linear.x and angular.z fields are the only consumed fields. Any
  change to the topic name, message type, or expected units (m/s and rad/s
  respectively) will cause the robot to stop responding to navigation commands
  entirely. The navigation stack has no fallback — silence equals a full stop.
- **Status:** Permanent
- **Affects:** navigation-service, path-planner-service
- **Safe changes:** Internal PID tuning, adding diagnostic publishers on separate topics
- **Unsafe changes:** Renaming /cmd_vel, changing message type away from Twist,
  changing unit assumptions (e.g. scaling to cm/s)
- **Verification:** Run `nav_integration_smoke_test.launch` and confirm the robot
  follows a 1m straight path and a 90° turn without stalling or oscillating.
  Echo /cmd_vel and confirm Twist fields match expected shape.
- **Link:** docs/interfaces/cmd_vel_contract.md

---

CONTRACT: Emergency Stop Heartbeat to Safety Supervisor
- This service publishes a heartbeat to /motor_controller/heartbeat at exactly
  50 Hz. The safety-supervisor monitors this topic and triggers a hardware e-stop
  if the rate drops below 40 Hz for more than 200ms. This is a physical safety
  boundary — an unintended e-stop mid-operation can damage the arm or injure
  nearby operators.
- **Status:** Permanent
- **Affects:** safety-supervisor-service, physical hardware e-stop relay
- **Safe changes:** Optimizing publisher thread priority
- **Unsafe changes:** Reducing publish rate, adding any blocking call on the
  publisher thread, renaming the topic
- **Verification:** Use `rostopic hz /motor_controller/heartbeat` under full CPU
  load simulation (`stress --cpu 4`) and confirm rate stays above 45 Hz.
  Confirm safety-supervisor logs show zero e-stop triggers during a 60s run.
- **Link:** docs/safety/estop_architecture.md, safety-supervisor-service/CONSTRAINTS.md

---

TIMING: Joint State Publish Latency
- Joint states must be published to /joint_states within 5ms of the encoder
  interrupt firing. The robot_state_publisher uses these to compute forward
  kinematics for the arm. Latency above 10ms causes visible TF tree jitter
  and breaks grasp planning accuracy. This bound was established empirically
  during arm calibration — it is not conservative.
- **Status:** Permanent
- **Affects:** robot_state_publisher, grasp-planning-service, RViz visualization
- **Safe changes:** Batching diagnostics published on a separate thread
- **Unsafe changes:** Adding synchronous I/O, file logging, or any network call
  on the encoder interrupt callback path
- **Verification:** Record /joint_states with rosbag during a full arm cycle.
  Run `tools/latency_audit.py` and confirm p99 publish latency stays under 8ms.
- **Link:** docs/timing/encoder_pipeline.md

---

TIMING: Firmware Update Window
- The motor controller firmware may only be flashed during the scheduled
  maintenance window (Sundays 00:00–04:00 UTC). Flashing outside this window
  interrupts active mission sessions and may corrupt in-progress odometry logs
  that fleet-manager is actively streaming. There is no recovery path for a
  corrupted session log — it is permanently lost.
- **Status:** Permanent
- **Affects:** fleet-manager-service, active mission sessions
- **Safe changes:** Preparing and staging firmware binaries ahead of the window
- **Unsafe changes:** Triggering a flash outside the maintenance window,
  automating flash without checking for active sessions first
- **Verification:** Confirm fleet-manager shows no active sessions before
  initiating flash. Post-flash, run `self_test.launch` and verify all joint
  torque readings are within ±2% of pre-flash baseline.
- **Link:** docs/ops/firmware_update_runbook.md

---

SCHEMA: CAN Bus Message ID Allocation
- Motor controller CAN message IDs 0x100–0x1FF are reserved exclusively for
  this service. The safety-supervisor and sensor-fusion-service have their ID
  ranges hardcoded in firmware — there is no runtime config. Collisions on the
  CAN bus fail silently: the wrong service receives the message and acts on it,
  or messages are dropped without any error surfacing in logs.
- **Status:** Permanent
- **Affects:** safety-supervisor-service, sensor-fusion-service, CAN firmware
- **Safe changes:** Adding new message IDs within the 0x100–0x1FF range
- **Unsafe changes:** Broadcasting outside the reserved range, reusing any ID
  already listed in docs/can_id_registry.md
- **Verification:** After any CAN ID change, run `tools/can_bus_collision_check.py`
  against the full registry and confirm zero conflicts reported.
- **Link:** docs/can_id_registry.md, sensor-fusion-service/CONSTRAINTS.md

---

SCHEMA: Odometry Covariance Fields Consumed by Fleet Manager
- The nav_msgs/Odometry messages published to /odom are consumed by fleet-manager
  to track robot position across the facility. Covariance matrix indices 0 and 35
  (x variance and yaw variance) are read explicitly. Setting these to zero tells
  fleet-manager the robot is perfectly localized, which disables uncertainty-aware
  path replanning and has previously caused collisions with dynamic obstacles.
- **Status:** Temporary — fleet-manager is being updated in Q2 2026 to read
  covariance dynamically. This constraint can be removed after fleet-manager
  v2.4 is deployed to all facilities.
- **Affects:** fleet-manager-service
- **Safe changes:** Tuning non-zero covariance values to better reflect real sensor noise
- **Unsafe changes:** Zeroing out any covariance field, changing the message type
- **Verification:** Run `fleet_manager_localization_test.py` in simulation and
  confirm the robot triggers replanning at least once when a dynamic obstacle
  is introduced mid-path.
- **Link:** docs/interfaces/odometry_contract.md, github.com/org/fleet-manager/issues/88

---

INFRA: Realtime Kernel Requirement
- This service must run on a host with a PREEMPT_RT patched kernel. The 5ms
  joint state latency constraint cannot be met on a standard kernel under load.
  Critically, this failure mode is invisible in CI and in low-load testing —
  it only surfaces under production CPU contention, making it easy to ship
  a broken deployment with full green tests.
- **Status:** Permanent
- **Affects:** All latency-sensitive publishers on this service
- **Safe changes:** None — this is a hard deployment requirement
- **Unsafe changes:** Deploying to any host without confirming RT kernel
- **Verification:** Run `uname -a` on the deployment host and confirm the kernel
  string contains "PREEMPT_RT". Then run the full `latency_audit.py` suite and
  confirm p99 stays under 8ms.
- **Link:** docs/infra/realtime_kernel_setup.md

---

INFRA: CAN Interface Name Hardcoded in Motor Firmware
- The SocketCAN interface must be named exactly `can0`. The motor controller
  firmware in the current hardware generation cannot read its interface name
  from config — it is compiled in. Renaming the interface (e.g. to `robot_can0`
  for clarity) causes the firmware to fail silently: motors receive no commands
  and no error is raised anywhere in the stack.
- **Status:** Temporary — frozen until firmware v3.0 ships (target Q3 2026).
  Do not attempt to rename until firmware v3.0 is confirmed deployed on all units.
- **Affects:** Motor firmware, all motor-driven hardware
- **Safe changes:** None — interface name is completely frozen until v3.0
- **Unsafe changes:** Any renaming of the SocketCAN network interface
- **Verification:** Run `ip link show can0` on the robot host and confirm the
  interface is UP before deploying. Post-deploy, confirm /joint_states is
  publishing within 5 seconds of service start.
- **Link:** docs/infra/can_interface_setup.md, github.com/org/motor-firmware/issues/42
