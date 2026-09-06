---
tipo: Modelo Conceitual
id: nebula-player-conceptual-005-heartbeat
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[nebula-player-conceptual-001-client]]'
- '[[nebula-player-conceptual-002-device]]'
- '[[nebula-player-conceptual-003-device-content-authorization]]'
- '[[nebula-player-conceptual-004-session]]'
- '[[nebula-player-conceptual-006-telemetry-event]]'
- '[[nebula-player-conceptual-007-log]]'
tags:
- modelo-conceitual
- nebula-player
aliases:
- 'Entidade: Heartbeat'
- nebula-player-conceptual-005-heartbeat
---

# Entidade: Heartbeat

## Definição

Heartbeat representa um sinal periódico enviado pelo Nebula Player ao Nebula Core durante uma Session ativa.

Seu objetivo é informar que o Device continua operacional e conectado.

Heartbeat não representa eventos de reprodução nem ações do usuário.

Heartbeat representa apenas a saúde operacional da Session.

---

## Responsabilidades

O Heartbeat é responsável por:

- informar que o Device continua ativo;
- atualizar o último contato da Session;
- permitir cálculo de disponibilidade;
- permitir cálculo de Online/Offline;
- servir como base para monitoramento em tempo real.

---

## Identidade

Heartbeat representa um evento operacional.

Cada envio gera um novo Heartbeat.

---

## Atributos Conceituais

- HeartbeatID
- SessionID
- Timestamp
- Ping
- Latency
- Status
- CreatedAt

---

## Estados

Heartbeat representa um evento instantâneo.

Por esse motivo, não possui ciclo de vida próprio.

O atributo Status representa apenas o resultado da comunicação.

Exemplos:

- Success
- Timeout
- Failed

---

## Relacionamentos

Todo Heartbeat:

- pertence exatamente a uma Session.

Uma Session pode possuir diversos Heartbeats.

---

## Invariantes

### INV-HEARTBEAT-001

Todo Heartbeat pertence exatamente a uma Session.

---

### INV-HEARTBEAT-002

Heartbeat nunca altera o Status Administrativo do Device.

---

### INV-HEARTBEAT-003

Heartbeat pode influenciar o OperationalState calculado pelo Nebula Core.

---

### INV-HEARTBEAT-004

Heartbeat nunca representa autorização de acesso.

---

## Regras Operacionais

- O Nebula Player envia Heartbeats periodicamente.
- O Nebula Core registra os Heartbeats.
- O Nebula Monitor utiliza os Heartbeats para cálculo de disponibilidade.
- A frequência dos Heartbeats será definida posteriormente.
- Heartbeats nunca são alterados após registrados.

---

## Observações Arquiteturais

Heartbeat representa exclusivamente conectividade e disponibilidade.

Ele não substitui TelemetryEvent.

Ele não substitui Log.

Ele não representa eventos de reprodução.

Sua principal finalidade é permitir que o Nebula Core e o Nebula Monitor determinem o estado operacional do Device.
