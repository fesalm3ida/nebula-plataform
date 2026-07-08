# Entidade: Device

## Descrição Lógica

Device representa uma instalação identificável do Nebula Player.

É a principal entidade do módulo Nebula Player e atua como Aggregate Root do domínio operacional.

Todas as operações realizadas pelo Player estão associadas a exatamente um Device.

---

## Atributos

| Atributo | PK | UK | NN | Domínio | Observação |
|----------|:--:|:--:|:--:|----------|------------|
| DeviceID | ✓ | ✓ | ✓ | UUID | Identificador lógico do Device. |
| ClientID | | | ✓ | UUID | Proprietário lógico do Device. |
| DeviceKey | | ✓ | ✓ | String | Credencial única utilizada durante autenticação. |
| NDF | | ✓ | ✓ | String | Nebula Device Fingerprint (ADR-009). |
| MACAddress | | | ✓ | String | Endereço MAC do sistema operacional. |
| Name | | | ✓ | String | Nome amigável do Device. |
| Platform | | | ✓ | Enum | Plataforma do Device. |
| AppVersion | | | ✓ | String | Versão instalada do Nebula Player. |
| AdministrativeStatus | | | ✓ | Enum | Estado administrativo do Device. |
| OperationalState | | | ✓ | Enum | Estado operacional calculado pelo Nebula Core. |
| LastSeenAt | | | | DateTime | Última comunicação conhecida. |
| ActivatedAt | | | | DateTime | Data de ativação. |
| BlockedAt | | | | DateTime | Data de bloqueio. |
| RevokedAt | | | | DateTime | Data de revogação. |
| ExpiredAt | | | | DateTime | Data de expiração. |
| CreatedAt | | | ✓ | DateTime | Data de criação. |
| UpdatedAt | | | ✓ | DateTime | Última atualização. |

---

## Domínios

### AdministrativeStatus

- Pending
- Active
- Blocked
- Revoked
- Expired

---

### OperationalState

- Online
- Offline
- Idle
- Unknown

---

### Platform

Exemplos:

- Android
- AndroidTV

Novas plataformas poderão ser adicionadas futuramente.

---

## Relacionamentos

| Origem | Cardinalidade | Destino | Descrição |
|---------|---------------|----------|-----------|
| Client | 1:N | Device | Um Client pode possuir diversos Devices. |
| Device | 1:N | DeviceContentAuthorization | Um Device pode possuir diversas autorizações. |
| Device | 1:N | Session | Um Device pode iniciar diversas Sessions. |

---

## Regras de Integridade

### RL-DEVICE-001

DeviceID identifica unicamente um Device.

### RL-DEVICE-002

DeviceKey deve ser única.

### RL-DEVICE-003

NDF deve ser único.

### RL-DEVICE-004

Todo Device pertence exatamente a um Client.

### RL-DEVICE-005

AdministrativeStatus e OperationalState representam conceitos independentes.

### RL-DEVICE-006

OperationalState nunca altera AdministrativeStatus.

### RL-DEVICE-007

AdministrativeStatus somente pode ser alterado pelo Nebula Core.

### RL-DEVICE-008

OperationalState é calculado a partir das Sessions e Heartbeats.

---

## Observações

Device representa a identidade operacional do Nebula Player.

Ele concentra autenticação, autorização, observabilidade e ciclo de vida da instalação.
