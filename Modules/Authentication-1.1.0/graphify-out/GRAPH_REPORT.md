# Graph Report - G:/GitHub-main/insight-cdss/Modules/Authentication-1.1.0  (2026-07-22)

## Corpus Check
- 26 files · ~50,634 words
- Verdict: corpus is large enough that graph structure adds value.

## Summary
- 616 nodes · 1030 edges · 39 communities (37 shown, 2 thin omitted)
- Extraction: 98% EXTRACTED · 2% INFERRED · 0% AMBIGUOUS · INFERRED: 21 edges (avg confidence: 0.59)
- Token cost: 0 input · 0 output

## Community Hubs (Navigation)
- Security Core & Migrations
- Auth API Routes
- Test Suite
- Contract Examples
- Documentation & UI
- CSRF Security Policy
- App Entry & Contract
- Auth Contract Root Schema
- Compatibility Sub-Schemas
- Error Policy Schema
- Module Metadata Schema
- Timeout Policy Schema
- CSRF Policy References
- CSRF Cookie Properties
- Security Policy Properties
- Session Cookie Properties
- Session Gates Schema
- Session Expiry Schema
- Security Policy Root Schema
- Capabilities & Workflows
- Compatibility Routes
- Role Enum Schema
- Auth Schemes
- Clinical Scope
- Deprecated Routes
- Clinical Scope Module
- User Display Schema
- User Object Schema
- Auth Object Schema
- Session Schema Root
- Schema References
- Auth Session Schema
- Session Root Properties
- CSRF Write Methods
- Username Validation
- Cookie Max-Age
- Design Document
- Audit Log Table
- Login Failures Table

## God Nodes (most connected - your core abstractions)
1. `get_conn()` - 28 edges
2. `AuthTestCase` - 25 edges
3. `login()` - 18 edges
4. `cfg()` - 17 edges
5. `required` - 16 edges
6. `_tx()` - 15 edges
7. `_require_csrf()` - 14 edges
8. `change_password()` - 14 edges
9. `_audit()` - 13 edges
10. `normalize_role()` - 13 edges

## Surprising Connections (you probably didn't know these)
- `published_schema()` --calls--> `schema()`  [EXTRACTED]
  main.py → contract.py
- `contract_payload()` --calls--> `cfg()`  [EXTRACTED]
  contract.py → security.py
- `contract_payload()` --calls--> `cookie_kwargs()`  [EXTRACTED]
  contract.py → security.py
- `contract_payload()` --calls--> `csrf_cookie_kwargs()`  [EXTRACTED]
  contract.py → security.py
- `contract()` --calls--> `contract_payload()`  [EXTRACTED]
  main.py → contract.py

## Import Cycles
- None detected.

## Communities (39 total, 2 thin omitted)

### Community 0 - "Security Core & Migrations"
Cohesion: 0.07
Nodes (82): Connection, _active_admin_count(), active_disclaimer_version(), _canonical_uuid(), cfg(), cfg_bool(), cfg_int(), change_user_password() (+74 more)

### Community 1 - "Auth API Routes"
Cohesion: 0.09
Nodes (65): BaseModel, HTTPException, Request, accept_disclaimer(), _account_response(), AccountListResponse, AccountResponse, _audit() (+57 more)

### Community 2 - "Test Suite"
Cohesion: 0.06
Nodes (11): assert_auth_schema(), assert_safe_session(), AuthTestCase, Auth03SecurityTests, AuthDiscoveryTests, AuthUuidContractTests, AuthContractTests, AuthMigrationTests (+3 more)

### Community 3 - "Contract Examples"
Cohesion: 0.04
Nodes (48): auth, required, schemes, basePath, capabilities, compatibility, jwksPolicy, jwtPolicy (+40 more)

### Community 4 - "Documentation & UI"
Cohesion: 0.08
Nodes (33): Admin Account Lifecycle, Session Cookie Policy, CSRF Double-Submit Protection, Disclaimer Gating for Psychiatrists, JWT Session Payload, POST /api/auth/login Route, GET /api/auth/session Route, Authentication v1 Contract (+25 more)

### Community 5 - "CSRF Security Policy"
Cohesion: 0.08
Nodes (24): bootstrapPath, cookieName, failureStatus, headerName, httpOnly, maxAgeSeconds, path, sameSite (+16 more)

### Community 6 - "App Entry & Contract"
Cohesion: 0.15
Nodes (20): contract_payload(), _load_json(), openapi_document(), Authentication discovery artifacts and runtime security metadata., schema(), _schema_path(), contract(), healthz() (+12 more)

### Community 7 - "Auth Contract Root Schema"
Cohesion: 0.10
Nodes (20): additionalProperties, $id, schemaVersion, required, $schema, type, auth, basePath (+12 more)

### Community 8 - "Compatibility Sub-Schemas"
Cohesion: 0.10
Nodes (20): additionalProperties, properties, required, type, type, type, const, type (+12 more)

### Community 9 - "Error Policy Schema"
Cohesion: 0.10
Nodes (20): type, type, additionalProperties, properties, required, type, type, csrfFailure (+12 more)

### Community 10 - "Module Metadata Schema"
Cohesion: 0.12
Nodes (16): const, const, const, const, pattern, type, properties, basePath (+8 more)

### Community 11 - "Timeout Policy Schema"
Cohesion: 0.14
Nodes (14): type, caller, readiness, server, timeoutPolicy, type, type, additionalProperties (+6 more)

### Community 12 - "CSRF Policy References"
Cohesion: 0.19
Nodes (14): required, path, required, bootstrapPath, cookieName, failureStatus, headerName, httpOnly (+6 more)

### Community 13 - "CSRF Cookie Properties"
Cohesion: 0.15
Nodes (13): const, minLength, type, properties, const, minLength, type, bootstrapPath (+5 more)

### Community 14 - "Security Policy Properties"
Cohesion: 0.17
Nodes (12): additionalProperties, type, minLength, type, const, properties, csrf, downstreamTrust (+4 more)

### Community 15 - "Session Cookie Properties"
Cohesion: 0.17
Nodes (12): const, minLength, type, const, httpOnly, name, path, sameSite (+4 more)

### Community 16 - "Session Gates Schema"
Cohesion: 0.18
Nodes (11): type, additionalProperties, properties, required, type, type, disclaimerAccepted, gates (+3 more)

### Community 17 - "Session Expiry Schema"
Cohesion: 0.20
Nodes (10): format, type, expiresAt, session, additionalProperties, properties, required, type (+2 more)

### Community 18 - "Security Policy Root Schema"
Cohesion: 0.20
Nodes (9): additionalProperties, $id, required, $schema, type, csrf, downstreamTrust, jwks (+1 more)

### Community 19 - "Capabilities & Workflows"
Cohesion: 0.25
Nodes (8): items, type, uniqueItems, type, capabilities, workflows, items, type

### Community 20 - "Compatibility Routes"
Cohesion: 0.25
Nodes (8): items, type, additionalProperties, required, path, compatibilityRoutes, deprecated, replacement

### Community 21 - "Role Enum Schema"
Cohesion: 0.25
Nodes (8): enum, roles, items, minItems, type, uniqueItems, admin, psychiatrist

### Community 22 - "Auth Schemes"
Cohesion: 0.29
Nodes (7): properties, required, schemes, const, items, type, uniqueItems

### Community 23 - "Clinical Scope"
Cohesion: 0.29
Nodes (7): minLength, type, items, type, declaration, populations, properties

### Community 24 - "Deprecated Routes"
Cohesion: 0.29
Nodes (7): const, properties, type, deprecated, path, replacement, type

### Community 25 - "Clinical Scope Module"
Cohesion: 0.29
Nodes (7): supportedClinicalScope, additionalProperties, required, type, declaration, populations, workflows

### Community 26 - "User Display Schema"
Cohesion: 0.29
Nodes (7): minLength, type, minLength, type, displayName, id, properties

### Community 27 - "User Object Schema"
Cohesion: 0.29
Nodes (7): user, additionalProperties, required, type, displayName, roles, username

### Community 28 - "Auth Object Schema"
Cohesion: 0.33
Nodes (6): additionalProperties, required, type, auth, required, schemes

### Community 29 - "Session Schema Root"
Cohesion: 0.33
Nodes (6): schemaVersion, required, authenticated, gates, session, user

### Community 30 - "Schema References"
Cohesion: 0.40
Nodes (5): pattern, schemas, items, type, uniqueItems

### Community 31 - "Auth Session Schema"
Cohesion: 0.40
Nodes (4): additionalProperties, $id, $schema, type

### Community 32 - "Session Root Properties"
Cohesion: 0.40
Nodes (5): const, properties, authenticated, schemaVersion, const

### Community 33 - "CSRF Write Methods"
Cohesion: 0.40
Nodes (5): PATCH, POST, writeMethods, const, type

### Community 34 - "Username Validation"
Cohesion: 0.50
Nodes (4): username, maxLength, minLength, type

### Community 35 - "Cookie Max-Age"
Cohesion: 0.67
Nodes (3): minimum, type, maxAgeSeconds

### Community 36 - "Design Document"
Cohesion: 0.67
Nodes (3): Carbon Health Design System, Five-State Clinical Status System, Teal as Clinical Trust

## Knowledge Gaps
- **237 isolated node(s):** `moduleId`, `moduleVersion`, `interfaceVersion`, `schemaVersion`, `basePath` (+232 more)
  These have ≤1 connection - possible missing edges or undocumented components.
- **2 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `properties` connect `Module Metadata Schema` to `Auth Contract Root Schema`, `Compatibility Sub-Schemas`, `Error Policy Schema`, `Timeout Policy Schema`, `Capabilities & Workflows`, `Compatibility Routes`, `Clinical Scope Module`, `Auth Object Schema`, `Schema References`?**
  _High betweenness centrality (0.047) - this node is a cross-community bridge._
- **Why does `errorPolicy` connect `Error Policy Schema` to `Module Metadata Schema`?**
  _High betweenness centrality (0.013) - this node is a cross-community bridge._
- **Are the 8 inferred relationships involving `AuthTestCase` (e.g. with `Auth03SecurityTests` and `AuthDiscoveryTests`) actually correct?**
  _`AuthTestCase` has 8 INFERRED edges - model-reasoned connections that need verification._
- **What connects `moduleId`, `moduleVersion`, `interfaceVersion` to the rest of the system?**
  _237 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Security Core & Migrations` be split into smaller, more focused modules?**
  _Cohesion score 0.06593707250341997 - nodes in this community are weakly interconnected._
- **Should `Auth API Routes` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `Test Suite` be split into smaller, more focused modules?**
  _Cohesion score 0.059506531204644414 - nodes in this community are weakly interconnected._