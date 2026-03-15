CONSTRAINTS for: motor-controller-service
Last updated: 2026-03-15
Owned by: robotics-platform-team

---

CONTRACT: Velocity command interface with navigation stack
  This service subscribes to /cmd_vel (geometry_msgs/Twist) from the
  navigation stack. The linear.x and angular.z fields are the only
  consumed fields. Any change to the topic name, message type, or
  expected unit (m/s and rad/s respectively) will cause the robot to
  stop responding to navigation commands entirely.
  Affects: navigation-service, path-planner-service
  Safe changes: internal PID tuning, adding diagnostic publishers
  Unsafe changes: renaming topic, changing units, switching message type
  Verification: Run nav_integration_smoke_test.launch and confirm robot
    follows a 1m straight path and 90° turn without stalling or oscillating.
    Manually check /cmd_vel echo output matches expected Twist fields.
  Links: docs/interfaces/cmd_vel_contract.md, 
    https://wiki.ros.org/geometry_msgs
  Status: permanent

CONTRACT: Emergency stop signal to safety-supervisor
  This service publishes a heartbeat to /motor_controller/heartbeat at
  exactly 50Hz. The safety-supervisor watches this topic and triggers
  a hardware e-stop if the rate drops below 40Hz for more than 200ms.
  Changing the publish rate, topic name, or message type will cause
  unintended emergency stops during operation.
  Affects: safety-supervisor-service, physical hardware e-stop relay
  Safe changes: optimizing publisher thread priority
  Unsafe changes: reducing publish rate, adding blocking calls on the
    publisher thread, renaming the topic
  Verification: Use rostopic hz /motor_controller/heartbeat under full
    CPU load simulation (stress --cpu 4) and confirm rate stays above 45Hz.
    Confirm safety-supervisor logs show no e-stop triggers during a 60s run.
  Links: docs/safety/estop_architecture.md, 
    safety-supervisor-service/CONSTRAINTS.md
  Status: permanent

---

TIMING: Joint state publish latency
  Joint states must be published to /joint_states within 5ms of the
  encoder interrupt firing. The robot_state_publisher node uses these
  to compute forward kinematics for the arm. Latency above 10ms causes
  visible TF tree jitter and breaks grasp planning accuracy.
  Affects: robot_state_publisher, grasp-planning-service, RViz visualization
  Safe changes: batching diagnostics published on a separate thread
  Unsafe changes: adding synchronous I/O or logging on the encoder
    interrupt callback path
  Verification: Record /joint_states with rosbag during a full arm cycle.
    Use the latency_audit.py script (tools/latency_audit.py) to confirm
    p99 publish latency stays under 8ms.
  Links: docs/timing/encoder_pipeline.md
  Status: permanent

TIMING: Firmware update window
  The motor controller firmware may only be flashed during the scheduled
  maintenance window (Sundays 00:00–04:00 UTC). Flashing outside this
  window interrupts active mission sessions and may corrupt in-progress
  odometry logs that the fleet-manager service is streaming.
  Affects: fleet-manager-service, active mission sessions
  Safe changes: preparing firmware binaries ahead of the window
  Unsafe changes: triggering a flash outside the maintenance window
  Verification: Confirm fleet-manager-service shows no active sessions
    before initiating flash. Post-flash, run self_test.launch and verify
    all joint torque readings are within ±2% of pre-flash baseline.
  Links: docs/ops/firmware_update_runbook.md
  Status: permanent

---

SCHEMA: CAN bus message ID allocation
  Motor controller CAN message IDs 0x100–0x1FF are reserved for this
  service. The safety-supervisor and sensor-fusion-service have their
  ID ranges hardcoded in firmware. Adding messages outside this range
  or reusing IDs from another service's range will cause silent message
  collisions on the bus.
  Affects: safety-supervisor-service, sensor-fusion-service, CAN firmware
  Safe changes: adding new message IDs within 0x100–0x1FF
  Unsafe changes: broadcasting outside reserved range, reusing any ID
    already listed in docs/can_id_registry.md
  Verification: After any CAN ID change, run can_bus_collision_check.py
    (tools/can_bus_collision_check.py) against the full registry and
    confirm zero conflicts reported.
  Links: docs/can_id_registry.md, 
    sensor-fusion-service/CONSTRAINTS.md
  Status: permanent

SCHEMA: Odometry message format consumed by fleet-manager
  The nav_msgs/Odometry messages published to /odom are consumed by the
  fleet-manager service to track robot position across the facility.
  The covariance matrix indices 0 and 35 (x and yaw variance) are read
  explicitly. Setting these to zero will cause fleet-manager to treat
  the robot as perfectly localized and skip uncertainty-aware path
  replanning, leading to collisions in dynamic environments.
  Affects: fleet-manager-service
  Safe changes: tuning non-zero covariance values to better reflect
    real sensor noise
  Unsafe changes: zeroing out covariance fields, changing message type
  Verification: Run fleet_manager_localization_test.py in simulation
    and confirm the robot triggers replanning at least once when a
    dynamic obstacle is introduced.
  Links: docs/interfaces/odometry_contract.md
  Status: temporary — fleet-manager is being updated in Q2 2026 to
    read covariance dynamically. Constraint can be removed after
    fleet-manager v2.4 is deployed.

---

INFRA: Realtime kernel requirement
  This service must run on a host with a PREEMPT_RT patched kernel.
  The 5ms joint state latency constraint (see TIMING above) cannot
  be met on a standard kernel under load. Deploying to a non-RT host
  will appear to work in testing but will fail intermittently in
  production under CPU contention.
  Affects: all latency-sensitive publishers on this service
  Verification: Run uname -a on the deployment host and confirm the
    kernel string contains "PREEMPT_RT". Then run the full
    latency_audit.py suite and confirm p99 stays under 8ms.
  Links: docs/infra/realtime_kernel_setup.md
  Status: permanent

INFRA: CAN interface name is hardcoded in legacy motor firmware
  The SocketCAN interface must be named can0. The motor controller
  firmware flashed on the current hardware generation cannot read its
  interface name from config — it is compiled in. Renaming the
  interface (e.g. to robot_can0 for clarity) will cause the firmware
  to fail silently and the motors will not receive any commands.
  Affects: motor firmware, all motor-driven hardware
  Safe changes: none — interface name is frozen until firmware v3.0
  Unsafe changes: any renaming of the SocketCAN network interface
  Verification: Run ip link show can0 on the robot host and confirm
    the interface is UP before deploying. Post-deploy, confirm
    /joint_states is publishing within 5 seconds of service start.
  Links: docs/infra/can_interface_setup.md, 
    firmware/CHANGELOG.md (see v3.0 migration notes)
  Status: temporary — frozen until firmware v3.0 ships (target Q3 2026).
    Track progress at github.com/org/motor-firmware/issues/42.
