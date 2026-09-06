---
tipo: Changelog
id: CHANGELOG
projeto: Nebula Platform
relacionados:
- '[[CONTRIBUTING]]'
- '[[PROJECT_STATUS-v2]]'
- '[[PROJECT_STATUS]]'
- '[[README]]'
- '[[RELEASES]]'
tags:
- changelog
aliases:
- CHANGELOG
---

v0.3.0

Added

JWT Authentication

Bearer Authentication

Ownership Validation

Session Lifecycle

Alembic

SQLAlchemy

Docker Secrets

Security Layer

Changed

Session endpoints now require Bearer.

Authentication moved to app/api/security.

Device identity comes from JWT.

Security

Anti-IDOR implemented.

Session hijacking protection.

213 automated tests.
