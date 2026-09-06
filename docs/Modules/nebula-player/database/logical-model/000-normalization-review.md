---
tipo: Modelo Logico
id: nebula-player-logical-000-normalization-review
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[nebula-player-logical-001-client]]'
- '[[nebula-player-logical-002-device]]'
- '[[nebula-player-logical-003-device-content-authorization]]'
- '[[nebula-player-logical-004-session]]'
- '[[nebula-player-logical-005-heartbeat]]'
- '[[nebula-player-logical-006-telemetry-event]]'
- '[[nebula-player-logical-007-log]]'
- '[[nebula-player-logical-008-event-type]]'
- '[[nebula-player-logical-009-log-level]]'
tags:
- modelo-logico
- nebula-player
aliases:
- 07/07/2026
- nebula-player-logical-000-normalization-review
---


# 07/07/2026

| Entidade                   | 1FN | 2FN | 3FN | DDD | Observação                                                       |
| -------------------------- | --- | --- | --- | --- | ---------------------------------------------------------------- |
| Client                     | ✅   | ✅   | ✅   | ✅   | Sem ajustes                                                      |
| Device                     | ✅   | ✅   | ✅   | ✅   | Separação entre AdministrativeStatus e OperationalState aprovada |
| DeviceContentAuthorization | ✅   | ✅   | ✅   | ✅   | Histórico preservado                                             |
| Session                    | ✅   | ✅   | ✅   | ✅   | Contexto temporal único                                          |
| Heartbeat                  | ✅   | ✅   | ✅   | ✅   | Responsabilidade única                                           |
| TelemetryEvent             | ✅   | ✅   | ⚠️  | ✅   | `EventType` promovido para entidade                              |
| Log                        | ✅   | ✅   | ⚠️  | ✅   | `LogLevel` promovido para entidade                               |
