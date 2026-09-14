---
tipo: Releases
id: RELEASES
projeto: Nebula Platform
atualizacao: '2026-09-14'
relacionados:
- '[[CHANGELOG]]'
- '[[CONTRIBUTING]]'
- '[[PROJECT_STATUS-v2]]'
- '[[PROJECT_STATUS]]'
- '[[README]]'
tags:
- releases
aliases:
- RELEASES
---

# Nebula Platform — Releases

v0.6.0 — Nebula Player funcional (reprodução real)

- **Player Android com reprodução real** de mídia (`media_kit`/libmpv): Ao vivo, Filmes e Séries.
- **Catálogo derivado do próprio M3U**: classificação por URL (`/movie/`, `/series/`, ao vivo) — na lista de referência, 19.348 filmes e 311.901 episódios, com capas (TMDB), categorias e agrupamento de episódios por série.
- **Controles próprios do player**: volume (barra de ajuste), play/pause e barra de progresso, com **auto-hide em 3 s**, **toque na tela alternando play/pause** e respeito à área segura (acima dos botões nativos do Android).
- **Tema** roxo/preto com degradê para azul escuro celeste e **layout responsivo** (retrato: lista + player em tela cheia; paisagem: grupos/canais/preview).
- **Resiliência**: decode UTF-8 da lista, auto-heal da identidade do device (401), boot sem erro quando não há lista/sessão, **lista local** em "Mudar lista".
- **Operação**: runbook em `docs/RUNBOOK.md`.
- Correção no Core: `POST /sessions` retoma a sessão ativa em vez de retornar 409.

v0.5.0 — Nebula Admin + Player Android + Observabilidade

- Nebula Admin: serviço FastAPI (BFF) + UI Flutter Web (login, dashboard, playlists, devices, associações).
- Nebula Player (Flutter Android) funcional: registro → ativação → associação → autenticação → sessão → provisionamento → heartbeat → telemetria (validado em dispositivo real).
- Subdomínio de Observabilidade (TelemetryEvent/Log) com ingestão.
- Correção: repositório PostgreSQL de Device passa a aceitar value objects.
- ~293 testes (Core + Admin).

v0.4.0 — PostgreSQL Persistence + Playlist Domain

- PostgreSQL validada (models, mappers, migrations, repositórios).
- Playlist Domain (entidade, associação, repositórios, use cases, CRUD API, /me/provisioning).
- 259 testes.

v0.3.0 — Foundation Complete

- Arquitetura em camadas (DDD/Clean Architecture).
- Persistência, Segurança, JWT, Ownership, Sessions.
- 213 testes.
