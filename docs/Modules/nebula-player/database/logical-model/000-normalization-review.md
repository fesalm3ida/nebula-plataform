
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
