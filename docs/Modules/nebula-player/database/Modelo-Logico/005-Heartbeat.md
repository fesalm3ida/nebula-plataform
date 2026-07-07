# Entidade: Heartbeat

## Descrição

Heartbeat representa um sinal periódico enviado pelo Nebula Player ao Nebula Core durante uma Session ativa.

Seu objetivo é informar que o Device permanece operacional, conectado e em condições de continuar executando suas atividades.

Heartbeat não representa eventos de reprodução, ações do usuário ou diagnósticos técnicos.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| HeartbeatID | Sim | Sim | Identificador lógico do Heartbeat. |
| SessionID | Sim | Não | Session à qual o Heartbeat pertence. |
| Timestamp | Sim | Não | Momento em que o Heartbeat foi gerado. |
| Ping | Não | Não | Tempo de resposta observado. |
| Latency | Não | Não | Latência da comunicação. |
| Status | Sim | Não | Resultado do envio do Heartbeat. |
| CreatedAt | Sim | Não | Data de persistência do registro. |

---

## Estados Permitidos

| Status | Descrição |
|---|---|
| Success | Heartbeat recebido com sucesso. |
| Timeout | Heartbeat não recebido dentro do tempo esperado. |
| Failed | Ocorreu falha durante a comunicação. |

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| Session | 1:N | Heartbeat | Uma Session pode gerar diversos Heartbeats. |

---

## Regras Importantes

- Todo Heartbeat pertence a exatamente uma Session.
- Heartbeats são imutáveis após registrados.
- Heartbeat nunca altera o AdministrativeStatus do Device.
- Heartbeat pode influenciar o OperationalState calculado pelo Nebula Core.
- Heartbeat representa exclusivamente conectividade e disponibilidade.
- A frequência de envio será definida em etapa posterior da arquitetura.