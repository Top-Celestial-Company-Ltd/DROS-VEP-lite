# DROS Drone Extension — Architecture

## Reference execution chain

```
AI / Agent
   │  proposes intent
   ▼
ExecutionRequest        (schemas/execution_request.schema.json)
   │
   ▼
DROS Policy / Capability / Provenance / Posture
   │
   ▼
Deterministic PDP
   │
   ▼
Distributed / Local PEP
   │
   ▼
Drone Execution Adapter (adapters/px4, adapters/mavlink, adapters/ros2)
   │
   ▼
MAVLink / ROS2 / uORB / Flight Controller
   │
   ▼
Physical Actuation
```

Any execution path not explicitly routed through this chain is, by default, **not** governed by DROS. See `../DRONE_EXECUTION_PATH_INVENTORY.json` for the current enumeration and mediation status of every known path (MAVLink, ROS2, uXRCE-DDS, Zenoh, local socket, IPC, serial, USB, CAN, device node, firmware API, shell).

## Reference platform

PX4 + MAVLink + SITL for Phase 1–3. Rationale: open-source, supports companion computers, ROS2, SITL and HIL, and has mature log/analysis tooling. See plan v0.3 §6.

## Known transport risk (informs T4 / ATS-006)

PX4's own documentation states MAVLink messages are unauthenticated by default, and notes that other transports (uXRCE-DDS, Zenoh) may bypass the MAVLink control path entirely. This is why `DRONE_EXECUTION_PATH_INVENTORY.json` treats each transport as a separate, independently-tested mediation boundary rather than assuming MAVLink coverage implies coverage of the others.

## Posture and provenance are external inputs, not DROS-internal claims

DROS is not a GPS-spoofing detector, navigation-integrity system, or credential issuer. It consumes:
- `runtime_posture` from an external authority (`schemas/drone_posture.schema.json`, see `../DRONE_RUNTIME_POSTURE.md`)
- `provenance` from an external, cryptographically verifiable source (`schemas/provenance.schema.json`)

and deterministically maps them to capability authorization. Self-asserted posture or provenance from the governed agent itself is explicitly rejected (see ATS-009, ATS-010).

## Governance response vs. physical response

A DROS `DENY` is a governance verdict, not a physical action. What the aircraft actually does (hover, RTL, controlled landing, mission abort, capability reduction) is owned by the flight-safety architecture and recorded separately in `../DRONE_SAFETY_DEGRADATION_MATRIX.md`. DROS's responsibility is to deterministically enforce the defined policy — not to unilaterally decide which physical response is safe in a given flight condition.
