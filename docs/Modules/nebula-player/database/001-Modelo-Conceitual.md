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


---
---
---

# Entidade: Device

## Definição

Device representa uma instalação autorizável do Nebula Player em um dispositivo físico ou ambiente compatível.

O Device é a principal entidade operacional da Nebula Platform, concentrando os processos de ativação, autenticação, autorização de acesso ao conteúdo, sessões, telemetria e observabilidade.

Um Device não representa um cliente comercial.

Todo Device pertence exatamente a um Client.

---

## Responsabilidades

O Device é responsável por:

- identificar uma instalação do Nebula Player;
- participar do processo de ativação;
- autenticar-se junto ao Nebula Core;
- solicitar ContentEndpoints autorizados;
- enviar eventos operacionais ao Nebula Core;
- manter histórico de utilização através de Sessions;
- originar Heartbeats;
- originar TelemetryEvents;
- originar Logs.

---

## Identidade

Todo Device possui três elementos distintos de identificação.

### DeviceID

Identificador interno da Nebula Platform.

É utilizado como identidade principal do domínio.

---

### DeviceKey

Chave única gerada pelo Nebula Player durante a primeira instalação.

É utilizada durante o processo de ativação.

---

### NDF (Nebula Device Fingerprint)

Representa a identidade operacional do dispositivo.

Seu algoritmo é definido pela ADR-009.

O NDF poderá utilizar informações como:

- DeviceKey
- MAC Address (quando disponível)
- Android ID (quando permitido)
- Fabricante
- Modelo
- Hardware
- Sistema Operacional
- Outros identificadores permitidos pela plataforma

O MAC Address nunca deve ser tratado como identificador primário.

---

## Atributos Conceituais

- DeviceID
- ClientID
- DeviceKey
- NDF
- MACAddress
- Name
- Platform
- AppVersion
- LastSeenAt
- ActivatedAt
- BlockedAt
- RevokedAt
- ExpiredAt
- CreatedAt
- UpdatedAt

---

# Estados do Device

O Device possui **duas dimensões independentes de estado**.

Essas dimensões representam conceitos distintos do domínio e nunca devem ser confundidas.

---

## Status Administrativo

Representa a situação administrativa do Device dentro da Nebula Platform.

É controlado exclusivamente pelo Nebula Core e pelo Nebula Admin.

O Nebula Player nunca altera este estado.

Estados possíveis:

- Pending
- Active
- Blocked
- Revoked
- Expired

---

## Estado Operacional (OperationalState)

Representa a condição operacional observada do Device.

É atualizado automaticamente pelo Nebula Core e pelo Nebula Monitor a partir dos eventos enviados pelo Nebula Player.

O OperationalState não representa autorização.

Ele representa apenas a condição operacional do Device.

Estados possíveis:

- Online
- Offline
- Unknown
- Unreachable

---

## Independência entre os Estados

As duas dimensões são independentes.

Exemplos válidos:

| Status | OperationalState | Interpretação |
|---------|------------------|---------------|
| Active | Online | Device autorizado e conectado. |
| Active | Offline | Device autorizado, porém desconectado. |
| Active | Unknown | Device autorizado, porém ainda sem informações suficientes para determinar seu estado operacional. |
| Blocked | Online | Device bloqueado administrativamente, mas ainda tentando comunicação com o Nebula Core. |
| Revoked | Offline | Device revogado e atualmente desconectado. |

---

## Relacionamentos

Um Device:

- pertence exatamente a um Client;
- pode possuir zero ou mais Sessions;
- pode possuir uma ou mais autorizações de acesso a ContentEndpoints;
- pode gerar Heartbeats;
- pode gerar TelemetryEvents;
- pode gerar Logs.

---

## Invariantes

### INV-DEVICE-001

Todo Device deve pertencer exatamente a um Client.

---

### INV-DEVICE-002

Todo Device deve possuir uma DeviceKey válida.

---

### INV-DEVICE-003

Todo Device deve possuir um NDF válido.

---

### INV-DEVICE-004

Um Device não pode alterar seu próprio Status Administrativo.

---

### INV-DEVICE-005

Um Device não pode cadastrar, alterar ou remover ContentEndpoints.

---

### INV-DEVICE-006

Um Device não pode acessar ContentEndpoints para os quais não esteja autorizado.

---

### INV-DEVICE-007

O MAC Address nunca deve ser utilizado como identificador primário do Device.

---

### INV-DEVICE-008

Um Device pode existir sem Sessions.

---

### INV-DEVICE-009

Um Device pode existir sem autorizações de ContentEndpoint enquanto estiver em estado Pending.

---

### INV-DEVICE-010

Status Administrativo e OperationalState representam conceitos distintos do domínio e evoluem de forma independente.

---

### INV-DEVICE-011

O OperationalState nunca concede nem revoga permissões de acesso.

Toda autorização é determinada exclusivamente pelo Status Administrativo e pelas regras do Nebula Core.

---

### INV-DEVICE-012

Mudanças no OperationalState nunca alteram automaticamente o Status Administrativo.

---

## Regras Operacionais

- A ativação do Device é realizada pelo Nebula Core.
- O bloqueio do Device é realizado exclusivamente pelo Nebula Admin.
- O Nebula Player apenas apresenta o Status recebido do Nebula Core.
- O Nebula Player nunca decide se está autorizado.
- O Nebula Player nunca armazena permanentemente recursos de conteúdo autorizados.
- O Nebula Player pode armazenar apenas os dados permitidos pela ADR-003.

---

## Ciclo de Vida

```text
Instalação do Nebula Player
        ↓
Geração da DeviceKey
        ↓
Coleta dos atributos necessários para composição do NDF
        ↓
Leitura do MAC Address (quando disponível pelo sistema operacional)
        ↓
Cálculo do NDF
        ↓
Registro no Nebula Core
        ↓
Pending
        ↓
Ativação pelo Nebula Admin/Core
        ↓
Active
        ↓
Uso normal
        ↓
Sessions
Heartbeats
TelemetryEvents
Logs
        ↓
Blocked / Revoked / Expired
```

---

## Observações Arquiteturais

O Device é a principal entidade operacional da Nebula Platform.

Sua identidade é composta por:

- DeviceID
- DeviceKey
- NDF (Nebula Device Fingerprint)

O Device possui duas dimensões independentes de estado:

- Status Administrativo
- OperationalState

Essa separação elimina ambiguidades entre autorização e conectividade, permitindo que o domínio represente corretamente situações em que um Device esteja autorizado, porém desconectado, ou bloqueado administrativamente enquanto ainda mantém comunicação temporária com o Nebula Core.

A representação física desses conceitos será definida durante a modelagem lógica e física do banco de dados.

---
---

---
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