# Entidade: Session

## Descrição

Session representa um período contínuo de uso do Nebula Player por um Device.

Ela funciona como o contexto temporal onde são agrupados Heartbeats, TelemetryEvents e Logs.

Uma Session começa quando o Player inicia uma execução válida e se comunica com o Nebula Core.

Uma Session termina quando o Player é encerrado, perde comunicação por timeout, ocorre falha crítica ou o Core considera aquela execução encerrada.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| SessionID | Sim | Sim | Identificador lógico da Session. |
| DeviceID | Sim | Não | Device ao qual a Session pertence. |
| Status | Sim | Não | Estado atual da Session. |
| StartedAt | Sim | Não | Data/hora de início da Session. |
| EndedAt | Não | Não | Data/hora de encerramento da Session. |
| LastHeartbeatAt | Não | Não | Último Heartbeat recebido durante a Session. |
| AppVersion | Sim | Não | Versão do Nebula Player durante a Session. |
| Platform | Sim | Não | Plataforma usada durante a Session. |
| IPAddress | Não | Não | IP observado durante a comunicação. |
| UserAgent | Não | Não | Identificação técnica do cliente, quando disponível. |
| CreatedAt | Sim | Não | Data de criação do registro. |
| UpdatedAt | Sim | Não | Data da última atualização. |

---

## Estados Permitidos

| Status | Descrição |
|---|---|
| Active | Session em andamento. |
| Closed | Session encerrada normalmente. |
| TimedOut | Session encerrada por ausência de comunicação. |
| Failed | Session encerrada por falha crítica. |

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| Device | 1:N | Session | Um Device pode possuir várias Sessions. |
| Session | 1:N | Heartbeat | Uma Session pode gerar vários Heartbeats. |
| Session | 1:N | TelemetryEvent | Uma Session pode gerar vários TelemetryEvents. |
| Session | 1:N | Log | Uma Session pode gerar vários Logs. |

---

## Regras Importantes

- Toda Session pertence a exatamente um Device.
- Uma Session ativa não deve possuir EndedAt.
- Uma Session encerrada deve possuir EndedAt.
- Uma Session encerrada não volta para Active.
- Heartbeats, TelemetryEvents e Logs devem estar associados a uma Session sempre que possível.
- O Nebula Core pode encerrar uma Session por timeout.
- O Player não altera Sessions antigas.
- Cada nova execução relevante do Player gera uma nova Session.
