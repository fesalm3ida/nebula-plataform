# Entidade: LogLevel

## Descrição

LogLevel representa a classificação oficial de severidade de um Log.

Seu objetivo é padronizar os níveis de log utilizados pelo Nebula Player, evitando valores livres e inconsistentes.

---

## Atributos

| Atributo | Obrigatório | Único | Observação |
|---|---:|---:|---|
| LogLevelID | Sim | Sim | Identificador lógico do nível de log. |
| Name | Sim | Sim | Nome único do nível de log. |
| Description | Não | Não | Descrição funcional do nível. |
| Severity | Sim | Não | Grau numérico ou lógico de severidade. |
| IsActive | Sim | Não | Indica se o nível está ativo. |
| CreatedAt | Sim | Não | Data de criação do registro. |
| UpdatedAt | Sim | Não | Data da última atualização. |

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---|---|---|---|
| LogLevel | 1:N | Log | Um LogLevel pode classificar diversos Logs. |

---

## Regras Importantes

- Todo Log deve possuir um LogLevel.
- LogLevel evita valores livres em registros técnicos.
- LogLevels podem possuir severidade própria.
- LogLevels podem ser ativados ou desativados.