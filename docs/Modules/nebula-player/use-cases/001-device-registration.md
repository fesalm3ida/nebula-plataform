---
tipo: Caso de Uso
id: nebula-player-usecase-001-device-registration
projeto: Nebula Platform
modulo: Nebula Player
relacionados:
- '[[nebula-player-usecase-002-device-authentication]]'
- '[[nebula-player-usecase-003-synchronization]]'
- '[[nebula-player-usecase-004-session-initialization]]'
- '[[nebula-player-usecase-005-playback]]'
- '[[nebula-player-usecase-006-heartbeat]]'
- '[[nebula-player-usecase-007-telemetry]]'
- '[[nebula-player-usecase-008-session-termination]]'
tags:
- caso-de-uso
- nebula-player
aliases:
- nebula-player-usecase-001-device-registration
---

Primeira instalação

↓

Não existe DeviceKey

↓

Calcula NDF

↓

Obtém MAC Address

↓

Envia solicitação ao Core

↓

Core cria Device

↓

Status = Pending

↓

Core devolve DeviceKey

↓

Player persiste DeviceKey

↓

Tela informa:

"Aguardando ativação."