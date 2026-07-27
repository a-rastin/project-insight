# Graph Report - /root/projects/insight/deployment  (2026-07-27)

## Corpus Check
- Corpus is ~2,268 words - fits in a single context window. You may not need a graph.

## Summary
- 240 nodes · 264 edges · 17 communities
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Schema Validation Properties
- Build & Volume Schema
- Backup & Restore Schema
- Module Items & References
- Root Schema Definition
- Manifest Instance
- Supervisor Schema
- Docker Compose Unified
- Supervisor Process Manager
- Windows Docker Desktop
- Gateway Readiness Probe
- Host Recovery Contracts
- Gateway Schema
- Migration Schema
- Shutdown Schema

## God Nodes (most connected - your core abstractions)
1. `required` - 15 edges
2. `insight-unified Service` - 15 edges
3. `Windows Docker Desktop Constraints` - 9 edges
4. `Supervisor` - 8 edges
5. `required` - 7 edges
6. `insight-unified-container.service` - 7 edges
7. `Handler` - 5 edges
8. `entrypoint` - 5 edges
9. `image` - 5 edges
10. `gateway` - 5 edges

## Surprising Connections (you probably didn't know these)
- `required` --extends--> `owner`  [EXTRACTED]
  manifest.schema.json → manifest.schema.json  _Bridges community 13 → community 2_

## Import Cycles
- None detected.

## Communities (17 total, 0 thin omitted)

### Community 0 - "Schema Validation Properties"
Cohesion: 0.08
Nodes (24): type, pattern, type, pattern, type, additionalProperties, type, maximum (+16 more)

### Community 1 - "Build & Volume Schema"
Cohesion: 0.09
Nodes (24): const, const, additionalProperties, properties, required, type, minLength, type (+16 more)

### Community 2 - "Backup & Restore Schema"
Cohesion: 0.12
Nodes (21): additionalProperties, properties, required, type, backup, configured, owner, policyReference (+13 more)

### Community 3 - "Module Items & References"
Cohesion: 0.10
Nodes (20): additionalProperties, required, items, minItems, type, modules, backup, basePath (+12 more)

### Community 4 - "Root Schema Definition"
Cohesion: 0.11
Nodes (18): additionalProperties, $id, const, properties, manifestId, $schema, required, $schema (+10 more)

### Community 5 - "Manifest Instance"
Cohesion: 0.11
Nodes (17): gateway, exposed, port, image, context, dockerfile, name, $schema (+9 more)

### Community 6 - "Supervisor Schema"
Cohesion: 0.11
Nodes (18): items, minItems, type, items, minItems, type, type, const (+10 more)

### Community 7 - "Docker Compose Unified"
Cohesion: 0.12
Nodes (16): AUTH_JWT_SECRET, Capability Drop ALL + Add CHOWN DAC_OVERRIDE SETUID SETGID NET_BIND_SERVICE, Build Context ../deployment/Dockerfile, Docker Compose Unified, Data Volumes (9 modules), insight-unified Service, Port 127.0.0.1:8080, no-new-privileges:true (+8 more)

### Community 8 - "Supervisor Process Manager"
Cohesion: 0.25
Nodes (8): Path, build_process_specs(), load_manifest(), main(), ProcessSpec, Any, Run unified module processes and forward container termination cleanly., Supervisor

### Community 9 - "Windows Docker Desktop"
Cohesion: 0.17
Nodes (12): Docker Named Volumes, Docker Scout (developer only), Immutable Image Reference (env), Loopback-Only Ports 8080, Resource Caps Parity Linux/Windows, Secrets Directory Mount, tmpfs Requirements, Trivy Security Scanner (+4 more)

### Community 10 - "Gateway Readiness Probe"
Cohesion: 0.29
Nodes (6): BaseHTTPRequestHandler, aggregate_readiness(), Handler, probe(), Any, Loopback readiness aggregator for required unified modules.

### Community 11 - "Host Recovery Contracts"
Cohesion: 0.20
Nodes (11): Host Reboot and Container Recovery Contracts, Immutable Image Digest, insight-unified-container.service, Linux VPS Deployment, Loopback Port 8080 Publish, Named Docker Volumes, Secrets Mount /run/secrets, supervisor.py Process Manager (+3 more)

### Community 12 - "Gateway Schema"
Cohesion: 0.18
Nodes (11): const, additionalProperties, properties, required, type, const, exposed, gateway (+3 more)

### Community 13 - "Migration Schema"
Cohesion: 0.22
Nodes (9): additionalProperties, properties, required, type, migration, mode, readinessGate, mode (+1 more)

### Community 14 - "Shutdown Schema"
Cohesion: 0.22
Nodes (9): shutdown, signal, timeoutSeconds, additionalProperties, properties, required, type, signal (+1 more)

## Knowledge Gaps
- **139 isolated node(s):** `$schema`, `manifestId`, `name`, `dockerfile`, `context` (+134 more)
  These have ≤1 connection - possible missing edges or undocumented components.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `properties` connect `Schema Validation Properties` to `Build & Volume Schema`, `Backup & Restore Schema`, `Module Items & References`, `Supervisor Schema`, `Migration Schema`, `Shutdown Schema`?**
  _High betweenness centrality (0.278) - this node is a cross-community bridge._
- **Why does `items` connect `Module Items & References` to `Schema Validation Properties`, `Supervisor Schema`?**
  _High betweenness centrality (0.204) - this node is a cross-community bridge._
- **Why does `properties` connect `Root Schema Definition` to `Build & Volume Schema`, `Module Items & References`, `Gateway Schema`, `Supervisor Schema`?**
  _High betweenness centrality (0.185) - this node is a cross-community bridge._
- **What connects `$schema`, `manifestId`, `name` to the rest of the system?**
  _139 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Schema Validation Properties` be split into smaller, more focused modules?**
  _Cohesion score 0.08333333333333333 - nodes in this community are weakly interconnected._
- **Should `Build & Volume Schema` be split into smaller, more focused modules?**
  _Cohesion score 0.08695652173913043 - nodes in this community are weakly interconnected._
- **Should `Backup & Restore Schema` be split into smaller, more focused modules?**
  _Cohesion score 0.12380952380952381 - nodes in this community are weakly interconnected._