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

---
---
---

# Entidade: Session

## Definição

Session representa um período contínuo de uso do Nebula Player por um Device.

Uma Session começa quando o Nebula Player inicia uma execução válida e se comunica com o Nebula Core.

Uma Session termina quando o Player é encerrado, perde comunicação por tempo limite, ocorre falha crítica ou o Nebula Core considera aquela execução encerrada.

A Session funciona como o contexto temporal dos eventos operacionais do Player.

---

## Responsabilidades

A Session é responsável por:

- representar uma execução do Nebula Player;
- agrupar Heartbeats, TelemetryEvents e Logs;
- registrar início e fim de uso;
- permitir análise de estabilidade durante um período;
- servir como base para métricas de experiência e observabilidade.

---

## Identidade

### SessionID

Identificador único da Session.

Cada nova execução relevante do Nebula Player deve gerar uma nova Session.

---

## Atributos Conceituais

- SessionID
- DeviceID
- Status
- StartedAt
- EndedAt
- LastHeartbeatAt
- AppVersion
- Platform
- IPAddress
- UserAgent
- CreatedAt
- UpdatedAt

---

## Estados

Estados possíveis:

- Active
- Closed
- TimedOut
- Failed

---

## Relacionamentos

Uma Session:

- pertence exatamente a um Device;
- pode possuir zero ou mais Heartbeats;
- pode possuir zero ou mais TelemetryEvents;
- pode possuir zero ou mais Logs.

Um Device pode possuir diversas Sessions ao longo do tempo.

---

## Invariantes

### INV-SESSION-001

Toda Session pertence exatamente a um Device.

---

### INV-SESSION-002

Um Device pode possuir múltiplas Sessions.

---

### INV-SESSION-003

Toda Session deve possuir StartedAt.

---

### INV-SESSION-004

Uma Session encerrada deve possuir EndedAt.

---

### INV-SESSION-005

Uma Session ativa não deve possuir EndedAt.

---

### INV-SESSION-006

Heartbeats, TelemetryEvents e Logs devem estar associados a uma Session sempre que possível.

---

### INV-SESSION-007

Uma Session encerrada não pode voltar ao estado Active.

---

## Ciclo de Vida

```text
Nebula Player iniciado
        ↓
Comunicação com Nebula Core
        ↓
Session criada
        ↓
Active
        ↓
Heartbeats / TelemetryEvents / Logs
        ↓
Closed / TimedOut / Failed
```

---
---
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

---
---
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
---
---

# Entidade: Log

## Definição

Log representa um registro técnico gerado durante uma Session do Nebula Player.

Seu objetivo é auxiliar diagnóstico técnico, investigação de falhas e rastreamento de comportamento interno da aplicação.

Log não representa conectividade.

Log não representa eventos de experiência do usuário.

Log não representa autorização de acesso.

Log pertence ao contexto de uma Session sempre que possível.

---

## Responsabilidades

O Log é responsável por:

- registrar informações técnicas relevantes;
- auxiliar diagnóstico de falhas;
- preservar rastros operacionais da execução;
- apoiar investigação de erros;
- complementar Heartbeats e TelemetryEvents sem substituí-los.

---

## Identidade

Cada Log representa um registro técnico ocorrido durante uma Session.

Todo Log possui identidade própria.

### LogID

Identificador único do Log.

---

## Atributos Conceituais

- LogID
- SessionID
- Level
- Source
- Message
- Context
- Timestamp
- CreatedAt

---

## Níveis

Exemplos:

- Debug
- Info
- Warning
- Error
- Critical

---

## Relacionamentos

Todo Log:

- pertence exatamente a uma Session sempre que possível.

Uma Session pode possuir diversos Logs.

---

## Invariantes

### INV-LOG-001

Log pertence ao contexto de uma Session sempre que possível.

---

### INV-LOG-002

Logs representam registros técnicos.

---

### INV-LOG-003

Logs não representam Heartbeats.

---

### INV-LOG-004

Logs não representam TelemetryEvents.

---

### INV-LOG-005

Logs não representam autorização de acesso.

---

## Regras Operacionais

- O Nebula Player gera Logs técnicos.
- O Nebula Core registra Logs recebidos do Nebula Player.
- O Nebula Monitor pode utilizar Logs para diagnóstico operacional.
- Logs não substituem Heartbeats.
- Logs não substituem TelemetryEvents.

---

## Observações Arquiteturais

Log representa diagnóstico técnico.

Sua finalidade é apoiar análise de falhas, investigação operacional e manutenção da aplicação.

Log faz parte do modelo híbrido de observabilidade, ao lado de Session, Heartbeat e TelemetryEvent.

Log permanece separado de Heartbeat e TelemetryEvent por representar diagnóstico técnico dentro do contexto de uma Session.
