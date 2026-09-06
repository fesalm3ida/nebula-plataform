---
tipo: Status do Projeto
id: PROJECT_STATUS
projeto: Nebula Platform
versao: 0.3.0-dev
status: Em desenvolvimento
atualizacao: '2026-07-12'
fase_atual: First Light
milestone: M3 — Session Presence
relacionados:
- '[[ADR-001]]'
- '[[ADR-016]]'
tags:
- status-do-projeto
aliases:
- Nebula Platform
- PROJECT_STATUS
---

# Nebula Platform

## Status do Projeto

- **Versão atual:** 0.3.0-dev
- **Fase atual:** First Light
- **Milestone em andamento:** M3 — Session Presence
- **Status geral:** Em desenvolvimento
- **Última atualização:** 2026-07-12

---

## Visão Geral

A Nebula Platform é um ecossistema modular para gerenciamento, reprodução,
autorização e monitoramento de conteúdo em dispositivos Android e Android TV.

O desenvolvimento atual está concentrado no **Nebula Core**, responsável pelas
regras de negócio, autenticação de Devices, ciclo de vida de Sessions e
integração futura com persistência, telemetria e observabilidade.

---

## Documentação

| Área | Status |
|---|---|
| Visão do produto | ✅ Concluída |
| Ecossistema | ✅ Concluído |
| MVP | ✅ Definido |
| Arquitetura | ✅ Consolidada |
| Domínio | ✅ Modelado |
| ADRs | ✅ ADR-001 até ADR-016 |
| RFCs | ✅ Estrutura inicial consolidada |
| Casos de uso | 🔄 Em evolução |
| API | 🔄 Em implementação |
| Banco de dados | 🔄 Modelado, persistência pendente |
| Telemetria | 🔄 Fundação preparada |
| Segurança | 🔄 Em evolução |

---

## Nebula Core

### Ambiente

- ✅ Desenvolvimento no WSL/Ubuntu
- ✅ Python 3.10+
- ✅ Ambiente virtual isolado
- ✅ FastAPI
- ✅ Uvicorn
- ✅ Pytest
- ✅ Estrutura baseada em Domain-Driven Design
- ✅ Separação por Clean Architecture

### Domínio

#### Entidades

- ✅ `Device`
- ✅ `Session`

#### Value Objects

- ✅ `MacAddress`
- ✅ `DeviceKey`
- ✅ `DeviceFingerprint`
- ✅ `AppVersion`

#### Enums

- ✅ `DeviceStatus`
- ✅ `DevicePlatform`
- ✅ `SessionStatus`

#### Presença

- ✅ `Session.last_seen`
- ✅ `Session.touch()`
- ✅ Validação de timestamps com timezone
- ✅ Proteção contra Heartbeats regressivos

### Repositórios

- ✅ `DeviceRepository`
- ✅ `SessionRepository`
- ✅ `InMemoryDeviceRepository`
- ✅ `InMemorySessionRepository`
- ⏳ `PostgreSQLDeviceRepository`
- ⏳ `PostgreSQLSessionRepository`

### Casos de Uso

- ✅ `RegisterDeviceUseCase`
- ✅ `ActivateDeviceUseCase`
- ✅ `AuthenticateDeviceUseCase`
- ✅ `StartSessionUseCase`
- ✅ `EndSessionUseCase`
- ✅ `HeartbeatSessionUseCase`

### API HTTP

| Método | Endpoint | Status |
|---|---|---|
| GET | `/` | ✅ |
| GET | `/health` | ✅ |
| POST | `/devices/register` | ✅ |
| POST | `/devices/{device_id}/activate` | ✅ Temporário |
| POST | `/auth/device` | ✅ |
| POST | `/sessions` | ✅ |
| POST | `/sessions/{session_id}/heartbeat` | ✅ |
| POST | `/sessions/{session_id}/end` | ✅ |

O endpoint de ativação é temporário e será substituído por um fluxo
administrativo protegido no Nebula Admin.

### Testes

- **137 testes aprovados**
- **0 falhas**
- **1 warning conhecido**
- Testes organizados por:
  - domínio;
  - aplicação;
  - infraestrutura;
  - API.

O warning conhecido é relacionado à depreciação do `httpx` utilizado pelo
`TestClient` do Starlette.

---

## Nebula Player

- ✅ Arquitetura documentada
- ✅ Estratégia stateless definida
- ✅ Fluxo de inicialização documentado
- ✅ Modelo local de armazenamento definido
- ⏳ Projeto Android ainda não iniciado
- ⏳ Integração com o Nebula Core pendente

---

## Nebula Admin

- ✅ Responsabilidades definidas
- ⏳ Implementação ainda não iniciada
- ⏳ Fluxo administrativo de ativação pendente
- ⏳ Gestão de Devices pendente
- ⏳ Gestão de autorizações pendente

---

## Nebula Monitor

- ✅ Responsabilidades definidas
- ✅ Modelo de presença preparado no Core
- ✅ Heartbeat disponível no Core
- ⏳ Serviço de monitoramento ainda não iniciado
- ⏳ Dashboards e alertas pendentes
- ⏳ Política de timeout pendente

---

## Persistência

### Situação atual

Os dados ainda são armazenados em memória durante a execução do Core.

Ao reiniciar o processo:

- Devices registrados são perdidos;
- Sessions abertas são perdidas;
- estados de presença são perdidos.

Esse comportamento é esperado nesta fase.

### Próxima implementação

- PostgreSQL;
- SQLAlchemy;
- Alembic;
- primeira migration;
- models de persistência;
- adaptadores PostgreSQL para os repositórios existentes.

O domínio e os casos de uso não deverão depender diretamente da tecnologia de
persistência.

---

## Próxima Tarefa

Iniciar a milestone de persistência real:

### M4 — PostgreSQL Persistence

1. Preparar dependências de persistência.
2. Configurar conexão com PostgreSQL.
3. Configurar SQLAlchemy.
4. Configurar Alembic.
5. Criar models de `Device` e `Session`.
6. Criar a primeira migration.
7. Implementar repositórios PostgreSQL.
8. Manter os testes atuais funcionando.
9. Criar testes de integração de persistência.

---

# Milestones

| Milestone | Nome | Status | Data |
|---|---|---|---|
| M1 | Architectural Foundation | ✅ Concluída | 2026-07-07 |
| M2 | Core Domain and First API | ✅ Concluída | 2026-07-11 |
| M3 | Session Presence and Heartbeat | ✅ Concluída | 2026-07-12 |
| M4 | PostgreSQL Persistence | ⏳ Próxima | — |
| M5 | Android Player Integration | ⏳ Planejada | — |
| M6 | Telemetry and Monitoring | ⏳ Planejada | — |

---

## M1 — Architectural Foundation

### Escopo

- visão do produto;
- documentação do ecossistema;
- definição do MVP;
- arquitetura;
- ADRs;
- RFCs;
- invariantes;
- modelo de domínio;
- modelo conceitual;
- modelo lógico;
- estratégia de armazenamento;
- fluxo de inicialização;
- casos de uso iniciais.

### Resultado

A fundação arquitetural do Nebula Player e da Nebula Platform foi consolidada.

### Git Tag

```text
m1-architectural-foundation