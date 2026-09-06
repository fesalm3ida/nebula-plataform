---
tipo: Releases
id: docs-RELEASES
projeto: Nebula Platform
status: Em desenvolvimento
atualizacao: '2026-07-12'
milestone: Session Presence and Heartbeat
tags:
- releases
aliases:
- '`docs/RELEASES.md`'
- docs-RELEASES
---


# `docs/RELEASES.md`

```markdown
# Nebula Platform — Releases

Este documento registra as principais entregas, milestones e versões internas
da Nebula Platform.

---

## Roadmap de Versões

| Versão | Objetivo | Status |
|---|---|---|
| 0.1.0 | Fundação arquitetural | ✅ Concluída |
| 0.2.0 | Modelo de domínio | ✅ Concluída |
| 0.3.0 | Nebula Core First Light | 🔄 Em desenvolvimento |
| 0.4.0 | Persistência PostgreSQL | ⏳ Planejada |
| 0.5.0 | Nebula Admin | ⏳ Planejada |
| 0.6.0 | Nebula Player Android | ⏳ Planejada |
| 0.7.0 | Telemetria e Monitoramento | ⏳ Planejada |
| 1.0.0 | Primeira versão pública | ⏳ Planejada |

---

# v0.3.0-dev — First Light

- **Data:** 2026-07-12
- **Status:** Em desenvolvimento
- **Milestone atual:** Session Presence and Heartbeat

## Destaques

- Primeira implementação executável do Nebula Core.
- Arquitetura em camadas baseada em DDD e Clean Architecture.
- API HTTP construída com FastAPI.
- Repositórios temporários em memória.
- Ciclo completo de Device.
- Ciclo mínimo de Session.
- Modelo de presença por Heartbeat.
- 137 testes automatizados aprovados.

## Device

### Domínio

- Entidade `Device`.
- Enum `DeviceStatus`.
- Enum `DevicePlatform`.
- Value Object `MacAddress`.
- Value Object `DeviceKey`.
- Value Object `DeviceFingerprint`.
- Value Object `AppVersion`.

### Casos de Uso

- `RegisterDeviceUseCase`.
- `ActivateDeviceUseCase`.
- `AuthenticateDeviceUseCase`.

### Endpoints

```text
POST /devices/register
POST /devices/{device_id}/activate
POST /auth/device