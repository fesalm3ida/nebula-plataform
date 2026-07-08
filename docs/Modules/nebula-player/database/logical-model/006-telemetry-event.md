# Entidade: TelemetryEvent

## Descrição

TelemetryEvent representa um evento operacional gerado pelo Nebula Player durante uma Session.

Seu objetivo é registrar acontecimentos relevantes relacionados ao comportamento da aplicação, permitindo análises operacionais, métricas de qualidade (QoS), auditoria e observabilidade.

TelemetryEvent não representa conectividade.

TelemetryEvent não representa diagnóstico técnico.

TelemetryEvent representa acontecimentos relevantes da execução do Player.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| TelemetryEventID | Sim | Sim | Identificador lógico do evento. |
| SessionID | Sim | Não | Session à qual o evento pertence. |
| EventTypeID | Sim | Não | Tipo de evento associado. |
| EventTimestamp | Sim | Não | Momento em que o evento ocorreu. |
| Payload | Sim | Não | Dados específicos do evento. |
| CreatedAt | Sim | Não | Data de persistência do registro. |

---

## Tipos de Evento

Exemplos de eventos suportados pelo MVP:

- PlaybackStarted
- PlaybackStopped
- ChannelChanged
- BufferStarted
- BufferFinished
- ErrorOccurred

Novos tipos poderão ser adicionados futuramente sem necessidade de alterar o domínio.

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| Session | 1:N | TelemetryEvent | Uma Session pode gerar diversos eventos de telemetria. |
| EventType | 1:N | TelemetryEvent | Um EventType pode classificar diversos TelemetryEvents. |

---

## Regras Importantes

- Todo TelemetryEvent pertence exatamente a uma Session.
- TelemetryEvents representam fatos ocorridos durante a execução do Player.
- TelemetryEvents são imutáveis após registrados.
- TelemetryEvents nunca representam Heartbeats.
- TelemetryEvents nunca substituem Logs.
- O formato do Payload depende do EventType.
- O Nebula Core é responsável por persistir os eventos recebidos.

---

### Ajuste aprovado

`EventType` será modelado como entidade própria.

Motivo:

- evitar valores soltos em `TelemetryEvent`;
- padronizar tipos de telemetria;
- facilitar dashboards;
- permitir ativar/desativar tipos de evento;
- preparar validação futura de payloads.

Impacto:

- `TelemetryEvent.EventType` será substituído por `EventTypeID`;
- será adicionada a entidade `EventType`;
- o relacionamento será `EventType 1:N TelemetryEvent`.