# 🌌 Light beyond — Nebula Platform v0.9.0

> Release que consolida a plataforma de ponta a ponta: do domínio à TV.
> Reúne **11 marcos** — do alicerce arquitetural ao app da LG Smart TV com
> reprodução de vídeo, licenciamento e pagamento automático em nuvem.

---

## M1 — Architectural Foundation ✅
- Monorepo com **Clean Architecture + DDD** (`nebula-core`, `nebula-admin`, `frontend/*`).
- ADRs fundacionais (ADR-001 … ADR-020), convenções e documentação no Obsidian.
- Regra de fronteira: **só o Core acessa o banco**.

## M2 — Core Domain & First API ✅
- Entidades e value objects do domínio (`Device`, `DeviceKey`, `Fingerprint`, `MacAddress`).
- Primeira API FastAPI do Core e testes de domínio/aplicação.

## M3 — Session Presence ✅
- Ciclo de vida de **sessão** (`Session`), presença e heartbeat do aparelho.

## M4 — PostgreSQL Persistence ✅
- Migrações **Alembic**, repositórios PostgreSQL + in-memory, mappers e testes de integração.

## M5 — Playlist Domain ✅
- `Playlist`, `PlaylistFormat`, `PlaylistStatus` e **`PlaylistAssignment`** (Device ↔ Playlist).
- CRUD, ativação/desativação, associação e **um Device com várias listas**.

## M6 — Provisioning ✅
- Ciclo de vida administrativo do Device (activate/block/revoke/expire).
- `GET /me/provisioning` com **ContentEndpoints** para o Player.

## M7 — Telemetry (Observabilidade) ✅
- Subdomínio completo: `TelemetryEvent`, `Log`, retenção (ADR-022/023/024).
- Ingestão de eventos e logs pelo app.

## M8 — Nebula Player Android ✅ (v0.6.0)
- App Flutter com **reprodução real** (`media_kit`/libmpv): Ao vivo, Filmes e Séries.
- Catálogo derivado do próprio **M3U** (classificação por URL) com capas, categorias e agrupamento de episódios.
- Controles próprios: volume acima da barra, auto‑ocultar em 3 s, toque = play/pause, SafeArea.
- **Busca por título** em Filmes e Séries e **barra de progresso apenas em VOD**.

## M9 — Licenciamento e Pagamentos ✅ (v0.7.0)
- **Trial de 7 dias** na primeira ativação; licenças **anual** (R$ 99) e **vitalícia** (R$ 299) — são **ADR-027**.
- **Portal do usuário** (ADR-028): login por **MAC + código de 6 dígitos**, ativação, licença e **cadastro da própria lista**; **administrador em URL secreta**.
- **Mercado Pago Checkout Pro** (ADR-029): **webhook** (`payment` e `merchant_order`) + **sync** de segurança concedendo a licença **automaticamente**.
- Ação administrativa **Resetar licença** e **Remover aparelho** (bloqueada quando há pagamentos).

## M10 — Nebula Monitor ✅ (v0.8.0)
- Metade de **leitura/agregação** da observabilidade: resumo, série por hora, eventos e logs.
- Dashboard no admin com KPIs, gráfico, filtros e período (24 h / 7 d / 30 d).
- Player passa a **enviar telemetria** (reprodução iniciada/encerrada/erro).

## M11 — Nebula TV: LG Smart TV (webOS) ✅ (v0.3.3)
- App **web nativo** (HTML/CSS/JS) empacotado como app webOS (`.ipk`), escolhido por rodar em **webOS 3+** e usar o **pipeline de vídeo da TV**.
- **Ativação** com MAC + código na TV, menu (Ao vivo · Filmes · Séries · Recarregar).
- **Ao vivo**: categorias + lista de canais + **preview retangular** do canal.
- **Filmes/Séries**: grade de pôsteres com **filtro ao focar a categoria** (padrão do Ibo) e **séries agrupadas** com lista de episódios.
- Navegação por controle em **modelo de colunas** + suporte a **Magic Remote**.
- Performance: **cache da lista em IndexedDB**, carregamento com **% de progresso**, logos com fallback e cache de falhas.
- Instalação e operação por linha de comando (`ares-*`) com modo desenvolvedor.

---

## 🧊 Frentes congeladas (registradas no backlog)
| Item | Motivo |
|---|---|
| **App de TV em Flutter** (AB-013) | a frente ativa de TV é o app web (que já reproduz na LG); o Flutter fica para **Android TV/box** e futuras TVs **webOS 26+** |
| **App iOS** | exige macOS + Xcode (projeto `ios/` já configurado, pronto para build) |
| **Nebula Monitor** | implementado e documentado; aguarda novas features de produto |

---

## 🏗️ Infraestrutura
- **Render**: Core + BFF (Docker) + Portal (Static Site) com HTTPS, health checks e deploy automático.
- **PostgreSQL gerenciado**, migrações aplicadas no start do container.
- Guias: **`docs/STARTUP.md`** (subir os 6 serviços), **`docs/RUNBOOK.md`** (operação, pagamentos), **`docs/DEPLOY-RENDER.md`**, **`docs/IOS.md`**.
- Qualidade: **350+ testes** no Core, **41** no BFF, testes de widget nos apps Flutter e **25** verificações no app webOS.

---

## 🔭 Próximos passos
1. **Favoritos + retomar de onde parou** no app da TV.
2. **EPG** (guia de programação) com fonte XMLTV.
3. **Alertas no Nebula Monitor** (limite de erros por aparelho).
4. Reativar o **keep‑warm** (UptimeRobot) para o primeiro acesso ser sempre rápido.
