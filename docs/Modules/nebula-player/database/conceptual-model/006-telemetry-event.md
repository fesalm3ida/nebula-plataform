---
tipo: Modelo Conceitual
id: nebula-player-conceptual-006-telemetry-event
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[nebula-player-conceptual-001-client]]'
- '[[nebula-player-conceptual-002-device]]'
- '[[nebula-player-conceptual-003-device-content-authorization]]'
- '[[nebula-player-conceptual-004-session]]'
- '[[nebula-player-conceptual-005-heartbeat]]'
- '[[nebula-player-conceptual-007-log]]'
tags:
- modelo-conceitual
- nebula-player
aliases:
- 'Entidade: TelemetryEvent'
- nebula-player-conceptual-006-telemetry-event
---

# Entidade: TelemetryEvent

## Definição

TelemetryEvent representa um evento operacional gerado pelo Nebula Player durante uma Session.

Seu objetivo é registrar acontecimentos relevantes relacionados ao comportamento da aplicação, permitindo análise operacional, diagnóstico, métricas de qualidade e observabilidade.

TelemetryEvent não representa conectividade.

TelemetryEvent não representa logs técnicos.

TelemetryEvent representa acontecimentos do funcionamento do Player.

---

## Responsabilidades

TelemetryEvent é responsável por:

- registrar eventos operacionais;
- permitir análise de experiência do usuário;
- alimentar dashboards;
- fornecer métricas de QoS;
- auxiliar diagnósticos operacionais.

---

## Identidade

Cada TelemetryEvent representa um fato ocorrido durante uma Session.

Todo evento possui identidade própria.

### TelemetryEventID

Identificador único do evento.

---

## Atributos Conceituais

- TelemetryEventID
- SessionID
- EventType
- EventTimestamp
- Payload
- CreatedAt

---

## Tipos de Evento

Exemplos:

- PlaybackStarted
- PlaybackStopped
- ChannelChanged
- BufferStarted
- BufferFinished
- VolumeChanged
- FullscreenEnabled
- FullscreenDisabled
- ErrorOccurred
- ListChange

A lista poderá evoluir conforme novas funcionalidades forem incorporadas ao Nebula Player.

---

## Relacionamentos

Todo TelemetryEvent:

- pertence exatamente a uma Session.

Uma Session pode possuir diversos TelemetryEvents.

---

## Invariantes

### INV-TELEMETRY-001

Todo TelemetryEvent pertence exatamente a uma Session.

---

### INV-TELEMETRY-002

TelemetryEvents representam fatos imutáveis.

---

### INV-TELEMETRY-003

TelemetryEvents nunca devem ser alterados após registrados.

---

### INV-TELEMETRY-004

TelemetryEvents não representam autorização.

---

### INV-TELEMETRY-005

TelemetryEvents não representam Heartbeats.

---

## Regras Operacionais

- O Nebula Player gera TelemetryEvents.
- O Nebula Core registra TelemetryEvents.
- O Nebula Monitor utiliza TelemetryEvents para análises operacionais.
- TelemetryEvents nunca são removidos durante a Session.

---

## Observações Arquiteturais

TelemetryEvent representa acontecimentos relevantes da execução do Nebula Player.

Sua finalidade é permitir análise histórica, geração de métricas e melhoria contínua da experiência do usuário.

O formato do Payload será definido durante a modelagem lógica e da API.


---

### Ajuste aprovado

`EventType` será modelado como entidade própria.

Motivo:

- evitar valores soltos em `TelemetryEvent`;
- padronizar tipos de telemetria;
- facilitar dashboards;
- permitir ativar/desativar tipos de evento;
- preparar validação futura de payloads.

Impacto:

- `TelemetryEvent.EventType` será substituído por `EventTypeID`;
- será adicionada a entidade `EventType`;
- o relacionamento será `EventType 1:N TelemetryEvent`.