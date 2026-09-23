---
tipo: Status do Projeto
id: PROJECT_STATUS-v2
projeto: Nebula Platform
versao: 0.8.0
status: 🚧 Em desenvolvimento ativo
atualizacao: '2026-09-23'
milestone: M10 — Nebula Monitor
codename: Observability
relacionados:
- '[[CHANGELOG]]'
- '[[CONTRIBUTING]]'
- '[[PROJECT_STATUS]]'
- '[[README]]'
- '[[RELEASES]]'
tags:
- status-do-projeto
aliases:
- Nebula Platform
- PROJECT_STATUS-v2
---

# Nebula Platform

# PROJECT STATUS v2.0

## Status do Projeto

- **Versão atual:** **0.8.0** (Nebula Monitor — telemetria)
- **Codename:** **Observability**
- **Milestone atual:** **M10 — Nebula Monitor** (M4–M9 concluídas)
- **Status geral:** 🚧 Em desenvolvimento ativo
- **Última atualização:** **23/09/2026**

---

# Visão Geral

A Nebula Platform é um ecossistema modular para gerenciamento, autenticação,
provisionamento, reprodução e monitoramento de dispositivos Android e Android TV.

O desenvolvimento atual está concentrado no **Nebula Core**, responsável pelas
regras de negócio, autenticação, autorização, ciclo de vida de Sessions,
persistência e futura integração com o Nebula Player, Nebula Admin e Nebula
Monitor.

---

# Situação Geral

| Área | Status |
|------|--------|
| Arquitetura | ✅ Consolidada |
| Domínio | ✅ Consolidado |
| Application Layer | ✅ Consolidada |
| Infrastructure Layer | ✅ Consolidada |
| API HTTP | ✅ Funcional |
| Persistência | ✅ Validada E2E (testes de integração PostgreSQL) |
| Segurança | ✅ Foundation Complete |
| Observabilidade | 🟢 Subdomínio implementado (TelemetryEvent/Log) · ADR-022/023 |
| Player Android | 🟢 Startflow implementado (scaffold Flutter em frontend/nebula-player) |
| Admin | 🟢 Serviço BFF (ADR-026) + UI Flutter Web · BFF ampliado (devices + associações) |
| Playlist (M5) | 🟢 Domínio iniciado (ADR-021) |

---

# Documentação

| Documento | Status |
|-----------|--------|
| Visão do Produto | ✅ |
| Ecossistema | ✅ |
| MVP | ✅ |
| Arquitetura | ✅ |
| Modelo de Domínio | ✅ |
| Banco de Dados | ✅ |
| API | 🔄 |
| Segurança | ✅ |
| ADRs | ✅ Atualizadas |
| RFCs | ✅ Estrutura consolidada |

---

# Nebula Core

## Ambiente

- ✅ Ubuntu / WSL2
- ✅ Python 3.10+
- ✅ Virtual Environment
- ✅ FastAPI
- ✅ Uvicorn
- ✅ Pytest
- ✅ PostgreSQL
- ✅ SQLAlchemy
- ✅ Alembic
- ✅ Docker Compose
- ✅ Docker Secrets
- ✅ Clean Architecture
- ✅ Domain Driven Design

---

# Domínio

## Entidades

- ✅ Device
- ✅ Session

## Value Objects

- ✅ DeviceKey
- ✅ DeviceFingerprint
- ✅ MacAddress
- ✅ AppVersion

## Enums

- ✅ DevicePlatform
- ✅ DeviceStatus
- ✅ SessionStatus

---

# Casos de Uso

- ✅ RegisterDeviceUseCase
- ✅ ActivateDeviceUseCase
- ✅ AuthenticateDeviceUseCase
- ✅ StartSessionUseCase
- ✅ HeartbeatSessionUseCase
- ✅ EndSessionUseCase

---

# API HTTP

| Método | Endpoint | Status |
|---------|----------|--------|
| GET | / | ✅ |
| GET | /health | ✅ |
| POST | /devices/register | ✅ |
| GET | /devices | ✅ (admin, lista de devices) |
| POST | /devices/{device_id}/activate | ✅ (admin) |
| POST | /devices/{device_id}/block | ✅ (admin) |
| POST | /devices/{device_id}/revoke | ✅ (admin) |
| POST | /devices/{device_id}/expire | ✅ (admin) |
| POST | /auth/device | ✅ |
| POST | /sessions | ✅ |
| POST | /sessions/{session_id}/heartbeat | ✅ |
| POST | /sessions/{session_id}/end | ✅ |
| POST | /playlists | ✅ (admin) |
| GET | /playlists | ✅ (admin) |
| GET | /playlists/{playlist_id} | ✅ (admin) |
| PATCH | /playlists/{playlist_id} | ✅ (admin) |
| POST | /playlists/{playlist_id}/status | ✅ (admin) |
| POST | /playlists/assignments | ✅ (admin) |
| GET | /me/provisioning | ✅ (Player, Bearer) |
| POST | /me/telemetry | ✅ (Player, Bearer, ADR-022/023) |
| POST | /me/logs | ✅ (Player, Bearer, ADR-022) |

### Segurança da API

Todos os endpoints relacionados ao ciclo de vida de Session utilizam:

- ✅ JWT Authentication
- ✅ HTTP Bearer
- ✅ Current Device Resolution
- ✅ Current Session Resolution
- ✅ Ownership Validation
- ✅ Anti-IDOR Protection

---

# Persistência

## Implementado

- ✅ PostgreSQL
- ✅ SQLAlchemy
- ✅ Alembic
- ✅ Docker Secrets
- ✅ Primeira Migration
- ✅ Configuração de ambiente segura

## Em evolução

- 🔄 PostgreSQLDeviceRepository
- 🔄 PostgreSQLSessionRepository

---

# Segurança

## Implementado

- ✅ JWT
- ✅ AccessTokenService
- ✅ JWTAccessTokenService
- ✅ HTTP Bearer Authentication
- ✅ CurrentDevice
- ✅ CurrentSession
- ✅ Ownership Validation
- ✅ Anti-IDOR
- ✅ Session Authorization
- ✅ WWW-Authenticate
- ✅ Secrets Management

---

# Qualidade

## Testes Automatizados

- ✅ **291 testes aprovados**
- ✅ **0 falhas**
- ⚠️ **1 warning conhecido**

### Cobertura

- Domain
- Application
- Infrastructure
- API
- Security
- Persistence

---

# Nebula Player

## Status

- ✅ Arquitetura documentada
- ✅ Estratégia Stateless definida
- ✅ Fluxo de Provisionamento definido
- ⏳ Implementação Android pendente

---

# Nebula Admin

## Status

- ✅ Responsabilidades definidas
- ⏳ Implementação pendente

---

# Nebula Monitor

## Status

- ✅ Modelo de Heartbeat preparado
- ✅ Session Presence implementada
- ⏳ Serviço de Monitoramento pendente
- ⏳ Dashboards pendentes

---

# Próxima Sprint

## Sprint 19 — Playlist Domain Module (em curso)

**ADR-021 (Aceita)** define Playlist como uma abstração de fonte de conteúdo
(M3U inicial; Xtream/Stalker previstos), cadastrada manualmente via Nebula Admin,
associada a Devices através da entidade intermediária `PlaylistAssignment`, e
entregue ao Player via `GET /me/provisioning`.

### ✅ Concluído

- Entidade de domínio `Playlist` (id, name, format, source_url, status, timestamps).
- Enums `PlaylistFormat`, `PlaylistStatus` e `PlaylistAssignmentStatus`.
- Entidade `PlaylistAssignment` (Device ↔ Playlist).
- `PlaylistRepository` e `PlaylistAssignmentRepository` (interfaces + PostgreSQL + in-memory).
- Persistência: models, mappers e migration de `playlists` e `playlist_assignments`.
- Use cases de criação, atualização, ativação/desativação, associação e provisionamento.
- Rotas de gerenciamento (`/playlists`) e endpoint `GET /me/provisioning` (Player).
- Testes de domínio, repositórios (in-memory + integração PostgreSQL), use cases e rotas.

### ⏳ Restante

- Proteger as rotas `/playlists` com autenticação do Nebula Admin (ainda inexistente).
- Implementar os formatos Xtream Codes e Stalker (apenas M3U no MVP).
- UI/gestão de associações no Nebula Admin.
- Migração aplicada ao ambiente (tabelas já criadas via `create_all` nos testes).

---

# Milestones

| ID | Milestone | Status |
|----|-----------|--------|
| M1 | Architectural Foundation | ✅ |
| M2 | Core Domain & First API | ✅ |
| M3 | Session Presence | ✅ |
| M4 | PostgreSQL Persistence | ✅ Validada (integração E2E com PostgreSQL) |
| M5 | Playlist Domain | 🟢 Implementado (entidade+repos+CRUD+provisioning) — falta Auth Admin |
| M6 | Provisioning | ✅ Provisionamento (ciclo de vida administrativo + device + ContentEndpoints) |
| M7 | Telemetry | 🟢 Subdomínio de observabilidade implementado (TelemetryEvent/Log) |

---

# Core Capabilities

## Authentication

- ✅ JWT
- ✅ Bearer

## Authorization

- ✅ Ownership Validation

## Session Lifecycle

- ✅ Start
- ✅ Heartbeat
- ✅ End

## Persistence

- ✅ PostgreSQL
- ✅ SQLAlchemy
- ✅ Alembic

## Security

- ✅ Anti-IDOR
- ✅ Docker Secrets

## Quality

- ✅ 291 Automated Tests

---

# Roadmap Imediato

1. Finalizar PostgreSQL Repositories
2. Playlist Domain
3. Xtream Server Module
4. Device Provisioning
5. Telemetry
6. Nebula Player Integration
7. Nebula Admin
8. Nebula Monitor

---

# Resumo Executivo

**Nebula Core v0.3.0** representa a conclusão da fundação arquitetural do projeto.

Nesta versão foram consolidados:

- Clean Architecture
- Domain Driven Design
- JWT Authentication
- HTTP Bearer Security
- Session Ownership
- Anti-IDOR Protection
- SQLAlchemy
- Alembic
- Docker Secrets
- PostgreSQL
- Session Lifecycle
- 291 testes automatizados

A partir desta versão o desenvolvimento migra da construção da fundação para a implementação dos módulos de negócio da plataforma.
