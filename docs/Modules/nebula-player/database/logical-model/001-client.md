---
tipo: Modelo Logico
id: nebula-player-logical-001-client
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[nebula-player-logical-000-normalization-review]]'
- '[[nebula-player-logical-002-device]]'
- '[[nebula-player-logical-003-device-content-authorization]]'
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
- 'Entidade: Client'
- nebula-player-logical-001-client
---

# Entidade: Client

## Descrição Lógica

Client representa a entidade comercial vinculada aos Devices do Nebula Player.

No modelo lógico, Client existe para garantir que todo Device tenha um proprietário lógico.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| ClientID | Sim | Sim | Identificador lógico principal do Client. |
| Name | Sim | Não | Nome comercial, pessoa física, empresa ou organização. |
| Document | Não | Não | Documento ou identificador comercial. Pode ser CPF, CNPJ ou outro identificador. |
| Status | Sim | Não | Situação administrativa do Client. |
| CreatedAt | Sim | Não | Data de criação do registro. |
| UpdatedAt | Sim | Não | Data da última atualização. |

---

## Estados Permitidos

| Status | Descrição |
|---|---|
| Active | Client ativo e apto a possuir Devices ativos. |
| Inactive | Client desativado logicamente. |

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| Client | 1:N | Device | Um Client pode possuir zero ou mais Devices. |

---

## Regras de Integridade

### RL-CLIENT-001

ClientID deve identificar unicamente um Client.

### RL-CLIENT-002

Name é obrigatório.

### RL-CLIENT-003

Status é obrigatório.

### RL-CLIENT-004

Client não deve ser removido fisicamente.

### RL-CLIENT-005

Um Client pode existir sem Devices.

### RL-CLIENT-006

Todo Device deve pertencer a exatamente um Client.

---

## Observações

Client pertence ao domínio lógico necessário para vincular Devices a uma entidade comercial.

O Nebula Player não manipula Client diretamente.

A criação, edição e desativação de Client pertencem ao Nebula Core/Nebula Admin.