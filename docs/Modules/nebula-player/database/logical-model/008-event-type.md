---
tipo: Modelo Logico
id: nebula-player-logical-008-event-type
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[nebula-player-logical-000-normalization-review]]'
- '[[nebula-player-logical-001-client]]'
- '[[nebula-player-logical-002-device]]'
- '[[nebula-player-logical-003-device-content-authorization]]'
- '[[nebula-player-logical-004-session]]'
- '[[nebula-player-logical-005-heartbeat]]'
- '[[nebula-player-logical-006-telemetry-event]]'
- '[[nebula-player-logical-007-log]]'
- '[[nebula-player-logical-009-log-level]]'
tags:
- modelo-logico
- nebula-player
aliases:
- 'Entidade: EventType'
- nebula-player-logical-008-event-type
---

# Entidade: EventType

## Descrição

EventType representa a classificação oficial de um TelemetryEvent.

Seu objetivo é padronizar os tipos de eventos gerados pelo Nebula Player, evitando valores livres e inconsistentes.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| EventTypeID | Sim | Sim | Identificador lógico do tipo de evento. |
| Name | Sim | Sim | Nome único do tipo de evento. |
| Description | Não | Não | Descrição funcional do evento. |
| Category | Não | Não | Categoria lógica do evento. |
| IsActive | Sim | Não | Indica se o tipo de evento está ativo. |
| CreatedAt | Sim | Não | Data de criação do registro. |
| UpdatedAt | Sim | Não | Data da última atualização. |

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| EventType | 1:N | TelemetryEvent | Um EventType pode classificar diversos TelemetryEvents. |

---

## Regras Importantes

- Todo TelemetryEvent deve possuir um EventType.
- EventType evita valores livres em eventos de telemetria.
- EventTypes podem ser ativados ou desativados.
- EventTypes podem evoluir sem alteração estrutural no modelo.