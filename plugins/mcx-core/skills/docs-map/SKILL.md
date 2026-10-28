---
name: docs-map
description: >
  Use when an answer needs Motorcortex detail from docs.motorcortex.io — setup
  steps, how to use DESK, GRID, ECAT or the portal, configuring a store
  application, control blocks and their parameters, the C++/Python/JS/Rust
  client APIs, the C++ Core API, maintenance, safety, FAQ — to find the right
  page to fetch instead of guessing URLs or searching the web.
review-by: 2027-01-28
---

# Finding the right page on docs.motorcortex.io

docs.motorcortex.io is the authoritative documentation; the other Motorcortex
skills deliberately do not repeat it. This skill is its map: every page, by
section, with its title and the page's own one-line description.

## How to use it

1. Pick the section below that fits the question.
2. Read that section's file and pick the page (or pages) whose title or
   description match. Search the file for a term rather than reading all of
   it when the section is large.
3. Fetch the page and answer from it, citing the URL. Prefer the page over
   memory or general knowledge when they differ.
4. A page that is missing or moved: the map is a snapshot, so fetch the live
   sitemap, https://docs.motorcortex.io/sitemap.xml, and look there before
   saying the docs do not cover it.

Do not fetch whole sections or the API reference to browse — pick pages from
the map first.

## Sections

| Section | Covers | File |
|---|---|---|
| Getting started | From an empty controller to a running application without machine hardware: connect your PC, network, browser certificate, install MCX-OS, log in to the portal, deploy and play | `sections/getting-started.md` |
| Standard applications | Configuring a store application (axes, EtherCAT, kinematics, I/O), the Machine App and the Robot App: user interface, programs, operation | `sections/applications.md` |
| Motorcortex tools | DESK (plotting, recording), ECAT (EtherCAT configuration), GRID (browser UIs), the MOTORCORTEX.IO portal (projects, packages, deploys) | `sections/motorcortex-io-tools.md` |
| Developing control applications | Real-time C++ applications: control blocks with every parameter, unit and default, environment setup (VS Code, CLion), the application template, MATLAB & Simulink | `sections/developing-control-applications.md` |
| Core API reference | The Doxygen reference of the C++ Core library: classes, namespaces, modules, examples — names only, look a class up by name | `sections/api-reference.md` |
| Developing client applications | Client libraries in C++, JavaScript, Python and Rust, and the protocol (Protobuf) | `sections/developing-client-applications.md` |
| Software features | Cockpit, Podman (Docker) containers, the VS Code extension | `sections/software-features.md` |
| Software maintenance | Backup and restore, network configuration, licences, software versions, remote access and file transfer, start/stop, simulation mode, file locations | `sections/software-maintenance.md` |
| Safety | TwinSAFE projects with FSoE: create, add hardware, download, link, test | `sections/safety.md` |
| Hardware | MCX-A4 and MCX-A4+ controllers, virtual machine installation | `sections/hardware.md` |
| Frequently asked questions | Certificates, connection, Cockpit, deployment, EtherCAT, licences, files | `sections/frequently-asked-questions.md` |
| Release notes | Release notes | `sections/releasenotes.md` |

The section files are generated from the live site (captured date in each);
the docs site's own search is https://docs.motorcortex.io/search/.
