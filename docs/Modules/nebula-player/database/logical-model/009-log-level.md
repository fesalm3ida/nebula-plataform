---
tipo: Modelo Logico
id: nebula-player-logical-009-log-level
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
- '[[nebula-player-logical-008-event-type]]'
tags:
- modelo-logico
- nebula-player
aliases:
- 'Entidade: LogLevel'
- nebula-player-logical-009-log-level
---

# Entidade: LogLevel

## Descrição

LogLevel representa a classificação oficial de severidade de um Log.

Seu objetivo é padronizar os níveis de log utilizados pelo Nebula Player, evitando valores livres e inconsistentes.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| LogLevelID | Sim | Sim | Identificador lógico do nível de log. |
| Name | Sim | Sim | Nome único do nível de log. |
| Description | Não | Não | Descrição funcional do nível. |
| Severity | Sim | Não | Grau numérico ou lógico de severidade. |
| IsActive | Sim | Não | Indica se o nível está ativo. |
| CreatedAt | Sim | Não | Data de criação do registro. |
| UpdatedAt | Sim | Não | Data da última atualização. |

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| LogLevel | 1:N | Log | Um LogLevel pode classificar diversos Logs. |

---

## Regras Importantes

- Todo Log deve possuir um LogLevel.
- LogLevel evita valores livres em registros técnicos.
- LogLevels podem possuir severidade própria.
- LogLevels podem ser ativados ou desativados.