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