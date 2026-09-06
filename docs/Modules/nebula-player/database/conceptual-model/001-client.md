---
tipo: Modelo Conceitual
id: nebula-player-conceptual-001-client
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[ADR-008]]'
tags:
- modelo-conceitual
- nebula-player
aliases:
- 'Entidade: Client'
- nebula-player-conceptual-001-client
---

# Entidade: Client

## Definição

Client representa a entidade comercial da Nebula Platform.

Um Client pode representar uma pessoa física, pessoa jurídica ou qualquer organização cadastrada na plataforma.

O Client é a raiz do Agregado Operacional e o proprietário lógico dos Devices vinculados à sua conta.

Um Client nunca consome conteúdo diretamente.

Todo acesso ao conteúdo ocorre através de Devices autorizados.

---

## Responsabilidades

O Client é responsável por:

- representar a entidade comercial da Nebula Platform;
- possuir Devices;
- centralizar as informações cadastrais mínimas;
- servir como raiz do Agregado Operacional;
- permitir desativação lógica através do Status.

---

## Identidade

Todo Client possui uma identidade própria.

### ClientID

Identificador interno da Nebula Platform.

É utilizado como identidade principal do domínio.

---

## Atributos Conceituais

- ClientID
- Name
- Document
- Status
- CreatedAt
- UpdatedAt

---

# Status do Client

O Status representa a situação administrativa do Client dentro da Nebula Platform.

É alterado exclusivamente pelo Nebula Admin ou pelo Nebula Core.

Estados possíveis:

- Active
- Inactive

---

## Relacionamentos

Um Client:

- pode possuir zero ou mais Devices;
- nunca acessa diretamente ContentEndpoints;
- recebe acesso ao conteúdo exclusivamente através de seus Devices.

---

## Invariantes

### INV-CLIENT-001

Todo Device deve pertencer exatamente a um Client.

---

### INV-CLIENT-002

Um Client pode existir sem possuir Devices.

---

### INV-CLIENT-003

A remoção física de um Client não deve deixar Devices órfãos.

---

### INV-CLIENT-004

Clients não devem ser removidos fisicamente.

A desativação deve ocorrer através do Status.

---

### INV-CLIENT-005

Todo Device pertence a apenas um Client por vez.

---

## Regras Operacionais

- O cadastro de Clients é realizado pelo Nebula Admin.
- Apenas Clients ativos podem possuir Devices ativos.
- O Client nunca interage diretamente com o Nebula Player.
- O Nebula Player conhece apenas o Device ao qual está vinculado.

---

## Ciclo de Vida

```text
Cadastro
     │
     ▼
Active
     │
     ▼
Uso Normal
     │
     ▼
Inactive
```

A desativação preserva todo o histórico do Client e de seus Devices.

---

## Observações Arquiteturais

Client representa exclusivamente a entidade comercial da Nebula Platform.

Ele não representa:

- um usuário administrador;
- uma conta de provedor de conteúdo;
- um dispositivo.

Sua principal responsabilidade é atuar como proprietário lógico dos Devices cadastrados.

Todo consumo de conteúdo ocorre através de Devices autorizados pelo Nebula Core.

Conforme definido na ADR-008, um Client pode representar:

- Pessoa Física;
- Pessoa Jurídica;
- Organização.

O restante do domínio permanece independente do tipo de Client.
