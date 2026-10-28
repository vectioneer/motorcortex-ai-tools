---
name: architecture-overview
description: >
  Use when explaining or reasoning about how a Motorcortex system is put
  together — runtime, parameter tree, communication layer, client APIs,
  tools, test environments, or the security model. For API-level detail,
  consult docs.motorcortex.io.
owner: coen
review-by: 2027-01-28
---

# Motorcortex Architecture Overview

## Architecture at a glance

A Motorcortex system consists of:

- **MCX-RTOS + Motorcortex Core/Engine** — the runtime on the motion controller: a hard real-time tuned Linux running the real-time engine. Executes control logic in deterministic real-time tasks and acts as EtherCAT master (pre-installed `etherlab` fork) for drives, I/O, and sensors.
- **Parameter tree** (the Motorcortex Data Tree) — the central concept. All signals, parameters, states, and I/O of the running control system are exposed in a hierarchical tree; everything is addressable by path (e.g., `root/Control/dummyDouble`).
- **Communication layer** — request/reply channel (login, tree info, get/set parameters, default port 5568) plus publish/subscribe channel (high-rate signal-group streaming, default port 5567), over WebSockets with TLS, messages serialized with Protocol Buffers. Protocol and API details: docs.motorcortex.io.
- **Client APIs** — C++, Python, JavaScript, Rust. The client libraries are open source; usage is documented on docs.motorcortex.io.
- **Tools** — the MOTORCORTEX.IO development tools: **ECAT** (EtherCAT configurator), **GRID** (web-based GUI/HMI editor), **DESK** (signal plotting, editing, and recording), **Cockpit** (controller management), plus an App-Store with standard configurations.

## Development domains

- **Real-time application development** — the control application that runs on the controller: control logic, modules, EtherCAT configuration.
- **Client development** — connecting external programs and UIs to a running Motorcortex system in Python, JavaScript, C++, or Rust.

## Test environments

Development does not require physical controller hardware. A Motorcortex system can run in a **virtual machine** locally on the developer's computer (QEMU preferred; no hard real time). It is suited for testing real-time **application code** as well as **client code** against a live system. The applications' built-in Digital Twin covers testing without real hardware attached: simulation and production run exactly the same code.

## Security model

- User authentication (login/password) on connection, with session tokens and automatic refresh
- Permission groups controlling read/write access to parts of the parameter tree
- Secure connections (WSS/TLS, Motorcortex Root CA)
- Industrial-grade security, certifiable against Common Criteria

## Further information

**Official documentation: https://docs.motorcortex.io** — consult on demand for anything not covered by this skill; its content is deliberately not duplicated here. The `docs-map` skill lists every page by section, so fetch the right page instead of guessing.
