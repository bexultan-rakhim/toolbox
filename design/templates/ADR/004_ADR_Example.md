#### 004\. Standardize on DDS-based Middleware (ROS 2) for Swarm Communication

**Status:** Accepted (Supersedes 001. Custom UDP Broadcast Protocol)

**Context:** Our current swarm of 50 warehouse robots relies on a custom UDP broadcast protocol (ADR 001). As we scale to 200+ robots, we are experiencing significant packet loss and lack of quality-of-service (QoS) controls. The lack of standardized discovery makes adding new robots to the mesh network a manual, error-prone process. We need a robust, industry-standard middleware that supports real-time constraints and reliable discovery in a lossy wireless environment.

**Decision:** **We shall migrate all inter-robot and robot-to-cloud communication to ROS 2 using the CycloneDDS implementation.** The rationale for this decision is the need for built-in Reliability and Liveliness QoS profiles. By moving to a Data Distribution Service (DDS) standard, we offload the complexity of network discovery and serialization to a proven framework. The trade-off is a higher memory footprint on our edge compute modules (approx. 15% increase) and a steeper learning curve for the firmware team.

**Alternatives:**

-   **ROS 1 (TCPROS):** Rejected due to the single-point-of-failure (ROS Master) and poor performance over intermittent Wi-Fi.

-   **MQTT:** Rejected because the centralized broker architecture creates a bottleneck that violates our requirement for peer-to-peer decentralized swarm behavior.

**Consequences:**

-   **2026-01-10 (Positive):** Network congestion decreased by 30% due to efficient multicast discovery.

-   **2026-02-15 (Negative):** Debugging "Type Mismatches" across different node versions has become more complex; requires stricter CI/CD linting.

-   **2026-03-01 (Positive):** Successfully integrated third-party LIDAR drivers that support ROS 2 natively, saving 3 weeks of development.

**Governance:**

-   **Decision Makers:** CTO, Lead Robotics Architect, Network Systems Lead.

-   **Upholding Responsibility:** Swarm Logic Team, DevOps.
