---
name: terminology
description: >
  Use when writing or reviewing any text that names Motorcortex, MCX, MCX-Robot,
  the Robot App, the Motion Controller, or the Visualization Computer — to get
  platform-wide terminology right, including the one word to use for each
  machine type (manipulator, mobile platform, machine, device).
owner: coen
review-by: 2027-01-28
---

# Motorcortex Terminology

Platform-wide terminology shared by all domains.

## Terminology

| Term | Definition |
|------|------------|
| **Motorcortex** | The motion control platform developed by Vectioneer. Provides real-time control, a web-based GUI, and a programming environment for motion systems. |
| **MCX** | Abbreviation for Motorcortex. Used in product names, scope tags, and identifiers. |
| **MCX-Robot** | The Motorcortex Robot Application. A closed-source, configurable robot app built on top of the Motorcortex platform. It provides all standard robot control functionality out of the box. |
| **Robot App** | Informal name for MCX-Robot. |
| **Motion Controller** | The hardware unit running the Motorcortex platform and the MCX-Robot application. |
| **Visualization Computer** | A separate computer (or the same unit) running a web browser that connects to the Motorcortex GUI. |

### Machine types and parts

One word per thing, across all documentation:

| Use | Not | For |
|---|---|---|
| **manipulator** | arm, robot arm | A kinematic chain that positions a tool |
| **mobile platform** | AGV, AMR | A machine that drives itself around |
| **machine** | — | Anything without kinematics |
| **device** | slave, EtherCAT slave | A node on the EtherCAT bus |

**These are the words for prose. Do not rename code.** A package or class
named `Agv` keeps its name, and the `<Slave>` elements in `io/master.xml` stay
`<Slave>` — that is what the EtherCAT specification and the tooling call them.
Write "mobile platform" in the sentence and the code name when naming the
package or class.

A page may say the code name once where a reader needs the link — "the mobile
platform (`AGV` in the code)" — and then use the prose word from there on.
