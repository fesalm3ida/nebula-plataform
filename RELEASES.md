---
tipo: Releases
id: RELEASES
projeto: Nebula Platform
atualizacao: '2026-09-06'
relacionados:
- '[[CHANGELOG]]'
- '[[CONTRIBUTING]]'
- '[[PROJECT_STATUS-v2]]'
- '[[PROJECT_STATUS]]'
- '[[README]]'
tags:
- releases
aliases:
- RELEASES
---

# Nebula Platform — Releases

v0.5.0 — Nebula Admin + Player Android + Observabilidade

- Nebula Admin: serviço FastAPI (BFF) + UI Flutter Web (login, dashboard, playlists, devices, associações).
- Nebula Player (Flutter Android) funcional: registro → ativação → associação → autenticação → sessão → provisionamento → heartbeat → telemetria (validado em dispositivo real).
- Subdomínio de Observabilidade (TelemetryEvent/Log) com ingestão.
- Correção: repositório PostgreSQL de Device passa a aceitar value objects.
- ~293 testes (Core + Admin).

v0.4.0 — PostgreSQL Persistence + Playlist Domain

- PostgreSQL validada (models, mappers, migrations, repositórios).
- Playlist Domain (entidade, associação, repositórios, use cases, CRUD API, /me/provisioning).
- 259 testes.

v0.3.0 — Foundation Complete

- Arquitetura em camadas (DDD/Clean Architecture).
- Persistência, Segurança, JWT, Ownership, Sessions.
- 213 testes.
