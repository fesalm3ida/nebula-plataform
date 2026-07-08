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