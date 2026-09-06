---
tipo: Modelo Conceitual
id: nebula-player-conceptual-003-device-content-authorization
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[ADR-011]]'
tags:
- modelo-conceitual
- nebula-player
aliases:
- 'Entidade: DeviceContentAuthorization'
- nebula-player-conceptual-003-device-content-authorization
---


# Entidade: DeviceContentAuthorization

## Definição

DeviceContentAuthorization representa uma decisão administrativa concedida pelo Nebula Core que autoriza um Device a consumir um ContentEndpoint específico.

Cada autorização possui identidade própria, ciclo de vida independente e histórico permanente, conforme definido na ADR-011.

Uma DeviceContentAuthorization não representa apenas um relacionamento entre Device e ContentEndpoint.

Ela representa uma decisão administrativa registrada pela Nebula Platform.

---

## Responsabilidades

A DeviceContentAuthorization é responsável por:

- conceder autorização para consumo de um ContentEndpoint;
- registrar quando a autorização foi concedida;
- registrar quando foi revogada;
- registrar quando expirou;
- preservar histórico completo das decisões administrativas;
- permitir auditoria das permissões concedidas.

---

## Identidade

Toda DeviceContentAuthorization possui identidade própria.

### AuthorizationID

Identificador único da autorização.

Cada nova autorização gera um novo AuthorizationID.

Autorizações nunca são reutilizadas.

---

## Atributos Conceituais

- AuthorizationID
- DeviceID
- ContentEndpointID
- Status
- GrantedAt
- RevokedAt
- ExpiredAt
- CreatedAt
- UpdatedAt

---

## Estados

Uma DeviceContentAuthorization possui seu próprio ciclo de vida.

Estados possíveis:

- Pending
- Authorized
- Revoked
- Expired

---

## Relacionamentos

Uma DeviceContentAuthorization:

- pertence exatamente a um Device;
- pertence exatamente a um ContentEndpoint.

Um Device pode possuir diversas autorizações.

Um ContentEndpoint pode ser autorizado para diversos Devices.

---

## Invariantes

### INV-AUTH-001

Toda DeviceContentAuthorization pertence exatamente a um Device.

---

### INV-AUTH-002

Toda DeviceContentAuthorization pertence exatamente a um ContentEndpoint.

---

### INV-AUTH-003

Um Device nunca poderá consumir um ContentEndpoint sem uma DeviceContentAuthorization válida.

---

### INV-AUTH-004

DeviceContentAuthorizations nunca devem ser removidas fisicamente.

---

### INV-AUTH-005

Toda revogação deve permanecer registrada permanentemente.

---

### INV-AUTH-006

Uma autorização revogada nunca poderá retornar ao estado Authorized.

---

### INV-AUTH-007

Uma autorização expirada nunca poderá retornar ao estado Authorized.

---

### INV-AUTH-008

Toda nova concessão de acesso gera uma nova DeviceContentAuthorization.

---

### INV-AUTH-009

Cada DeviceContentAuthorization representa exatamente uma decisão administrativa.

---

## Ciclo de Vida

```text
Pending
      │
      ▼
Authorized
      │
 ┌────┴────┐
 ▼         ▼
Revoked  Expired
```

Uma autorização encerrada nunca retorna ao estado Authorized.

Uma nova concessão sempre gera uma nova DeviceContentAuthorization.

---

## Regras Operacionais

- somente o Nebula Core pode criar DeviceContentAuthorizations;
- somente o Nebula Admin pode solicitar concessão ou revogação de autorizações;
- o Nebula Player nunca cria autorizações;
- o Nebula Player nunca altera autorizações;
- o Nebula Player apenas consome ContentEndpoints autorizados pelo Nebula Core.

---

## Observações Arquiteturais

DeviceContentAuthorization representa uma decisão administrativa imutável.

Seu histórico constitui parte do mecanismo de auditoria da Nebula Platform.

A existência de uma autorização não implica que o Device esteja online.

A existência de uma autorização apenas indica que o Device possui permissão para consumir determinado ContentEndpoint.
