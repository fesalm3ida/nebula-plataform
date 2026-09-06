---
tipo: Modelo Logico
id: nebula-player-logical-003-device-content-authorization
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[nebula-player-logical-000-normalization-review]]'
- '[[nebula-player-logical-001-client]]'
- '[[nebula-player-logical-002-device]]'
- '[[nebula-player-logical-004-session]]'
- '[[nebula-player-logical-005-heartbeat]]'
- '[[nebula-player-logical-006-telemetry-event]]'
- '[[nebula-player-logical-007-log]]'
- '[[nebula-player-logical-008-event-type]]'
- '[[nebula-player-logical-009-log-level]]'
tags:
- modelo-logico
- nebula-player
aliases:
- 'Entidade: DeviceContentAuthorization'
- nebula-player-logical-003-device-content-authorization
---

# Entidade: DeviceContentAuthorization

## Descrição

DeviceContentAuthorization representa uma decisão administrativa que autoriza um Device a consumir um ContentEndpoint específico.

Ela não é apenas uma tabela de ligação. Cada autorização possui identidade própria, histórico e ciclo de vida.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| AuthorizationID | Sim | Sim | Identificador lógico da autorização. |
| DeviceID | Sim | Não | Device autorizado. |
| ContentEndpointID | Sim | Não | ContentEndpoint autorizado. |
| Status | Sim | Não | Estado da autorização. |
| GrantedAt | Sim | Não | Data em que o acesso foi concedido. |
| RevokedAt | Não | Não | Data em que o acesso foi revogado. |
| ExpiredAt | Não | Não | Data em que o acesso expirou. |
| CreatedAt | Sim | Não | Data de criação do registro. |
| UpdatedAt | Sim | Não | Data da última atualização. |

---

## Estados Permitidos

| Status | Descrição |
|---|---|
| Pending | Autorização criada, mas ainda não vigente. |
| Authorized | Autorização vigente. |
| Revoked | Autorização revogada. |
| Expired | Autorização expirada. |

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| Device | 1:N | DeviceContentAuthorization | Um Device pode possuir várias autorizações. |
| DeviceContentAuthorization | N:1 | ContentEndpoint | Cada autorização aponta para um ContentEndpoint. |

---

## Regras Importantes

- Cada nova concessão de acesso gera uma nova DeviceContentAuthorization.
- Uma autorização revogada nunca retorna para Authorized.
- Uma autorização expirada nunca retorna para Authorized.
- Autorizações não devem ser removidas fisicamente.
- O Player nunca cria ou altera autorizações.
- O Core é responsável por validar se existe autorização vigente antes de liberar o ContentEndpoint.
- ContentEndpoint pertence ao domínio da Nebula Platform/Core e aparece aqui apenas como referência externa.

