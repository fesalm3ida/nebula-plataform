---
tipo: Runbook
id: RUNBOOK
projeto: Nebula Platform
status: Ativo
atualizacao: '2026-09-13'
responsavel: Nebula Team
relacionados:
- '[[PROJECT_STATUS-v2]]'
- '[[README]]'
- '[[RELEASES]]'
tags:
- runbook
- operacao
aliases:
- Runbook Operacional
---

# Runbook Operacional — Nebula Platform

Passo a passo para deixar o ambiente **operacional** (backend + Admin Web + Player Android)
após desligar todos os processos do WSL.

---

## Visão geral — o que precisa estar rodando

| # | Componente | Onde | Porta |
|---|---|---|---|
| 1 | PostgreSQL | Docker (`nebula-postgres`) | 5434 |
| 2 | Nebula Core (API) | `backend/nebula-core` | 8000 |
| 3 | Nebula Admin (BFF) | `backend/nebula-admin` | 8001 |
| 4 | Admin UI (Flutter Web) | `frontend/nebula-admin` | 3000 |
| 5 | Player (Flutter Android) | `frontend/nebula-player` | no dispositivo |

Fluxo: `Player → Core → PostgreSQL` · `Admin UI → Admin BFF → Core → PostgreSQL`.

---

## Caminhos absolutos

```text
Repo:            /home/fealmeida/projects/nebula-plataform
Core:            /home/fealmeida/projects/nebula-plataform/backend/nebula-core
Admin (BFF):     /home/fealmeida/projects/nebula-plataform/backend/nebula-admin
Admin UI:        /home/fealmeida/projects/nebula-plataform/frontend/nebula-admin
Player:          /home/fealmeida/projects/nebula-plataform/frontend/nebula-player
Infra (docker):  /home/fealmeida/projects/nebula-plataform/infra/docker
Flutter SDK:     /home/fealmeida/projects/nebula-plataform/develop/flutter
Android SDK:     /home/fealmeida/Android/Sdk
adb (SDK):       /home/fealmeida/Android/Sdk/platform-tools/adb
Segredos Core:   /home/fealmeida/projects/nebula-plataform/backend/nebula-core/.secrets
```

> Obs.: `develop/` (SDK do Flutter) está no `.gitignore` — não é versionado.
> Python: use o venv do Core (`backend/nebula-core/.venv`) também para o Admin.

---

## 0) Pré-requisitos (configuração única, já feita)

No `~/.zshrc`:
```bash
export ANDROID_HOME=$HOME/Android/Sdk
export ANDROID_SDK_ROOT=$HOME/Android/Sdk
export PATH=$PATH:$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools
```
Se `which adb` não apontar para o SDK, use o caminho completo `$ANDROID_HOME/platform-tools/adb`.

---

## 1) PostgreSQL (Docker) — porta 5434

```bash
cd /home/fealmeida/projects/nebula-plataform/infra/docker
docker compose --env-file .env -f compose.yml up -d
docker ps | grep nebula-postgres        # deve estar "Up ... (healthy)"
```
- Container: `nebula-postgres` (imagem `postgres:16-alpine`), `restart: unless-stopped`.
- **Persistência:** volume nomeado `nebula_postgres_data` → **os dados sobrevivem** a reinícios.
- ⚠️ **NUNCA** use `docker compose down -v` (o `-v` apaga o volume e você perde devices/playlists).

---

## 2) Migrações do Core (aplicar o schema)

```bash
cd /home/fealmeida/projects/nebula-plataform/backend/nebula-core
./.venv/bin/python -m alembic upgrade head
./.venv/bin/python -m alembic current    # deve mostrar a2b3c4d5e6f7 (head)
```

---

## 3) Nebula Core — porta 8000

```bash
cd /home/fealmeida/projects/nebula-plataform/backend/nebula-core
./.venv/bin/uvicorn app.main:app --port 8000
```
- Config automática: `.env` (POSTGRES_HOST/PORT/DB/USER) + `.secrets/postgres_password` + `.secrets/jwt_secret_key`.
- Verificar: `curl -s http://localhost:8000/health` → `{"status":"healthy"}`.
- Deixe rodando em um terminal.

---

## 4) Nebula Admin (BFF) — porta 8001

O Admin lê automaticamente o arquivo **`backend/nebula-admin/.env`** (ignorado pelo git):

```text
ADMIN_SEED_EMAIL=admin@nebula.local
ADMIN_SEED_PASSWORD=nebula@2026
NEBULA_CORE_BASE_URL=http://localhost:8000
NEBULA_CORE_SERVICE_TOKEN=dev-admin-key
ADMIN_JWT_SECRET_KEY=<segredo>
```

```bash
cd /home/fealmeida/projects/nebula-plataform/backend/nebula-admin
PYTHONPATH=. ../nebula-core/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8001
```

- **Login do Admin UI:** **`admin@nebula.local`** / **`nebula@2026`**.
- `NEBULA_CORE_SERVICE_TOKEN` **precisa ser igual** ao `ADMIN_API_KEY` do Core (default `dev-admin-key`).
- ⚠️ **Suba da pasta `backend/nebula-admin`**: se rodar de outra pasta, `app.main:app` resolve para o **Core** e a porta 8001 passa a servir as rotas do Core.
- **Confirme que é o Admin** (e não o Core):
  ```bash
  curl -s http://localhost:8001/openapi.json | grep -o '"/admin[^"]*"' | head
  # esperado: /admin/auth/login, /admin/devices, /admin/playlists, ...
  ```

---

## 5) Admin UI (Flutter Web) — porta 3000

Descubra o IP do WSL (usado pelo navegador do Windows):
```bash
hostname -I        # ex.: 172.18.88.46
```
```bash
cd /home/fealmeida/projects/nebula-plataform/frontend/nebula-admin
flutter run -d web-server --web-port=3000 --web-hostname=0.0.0.0 \
  --dart-define=NEBULA_ADMIN_API=http://<IP_DO_WSL>:8001
```
Abra no navegador: `http://<IP_DO_WSL>:3000` → login com `admin@nebula.local`.

> Sobrescreva o IP correto: o app chama o BFF por esse endereço (não use `localhost`, que no navegador é o Windows).

---

## 6) Player (Flutter Android)

### 6a) Conectar o dispositivo

**Opção Wi‑Fi (recomendada):**
```bash
export PATH=$ANDROID_HOME/platform-tools:$PATH
# no POCO: Opções do desenvolvedor → Depuração sem fio → Emparelhar com código
adb pair <IP_DO_CELULAR>:<PORTA_EMParelhAMENTO>     # digite o código de 6 dígitos
adb connect <IP_DO_CELULAR>:<PORTA_CONEXAO>         # ex.: 5555
adb devices                                          # o device deve aparecer como "device"
```

**Opção USB (usbipd):** no Windows (PowerShell admin):
```powershell
usbipd list
usbipd bind --force --busid <BUSID>
usbipd attach --wsl Ubuntu --busid <BUSID>
```
(no WSL: `lsusb` e `adb devices`)

### 6b) Rodar o app
```bash
cd /home/fealmeida/projects/nebula-plataform/frontend/nebula-player
adb reverse tcp:8000 tcp:8000        # celular:localhost:8000 -> WSL:localhost:8000
flutter run --dart-define=NEBULA_CORE_API=http://localhost:8000
```
> O `adb reverse` faz o celular alcançar o Core pelo `localhost:8000`.

---

## 7) Deixar o app "operacional" (dados mínimos)

Com Core + Postgres rodando (e o Player já instalado):

### 7.1 Criar uma playlist
Pelo **Admin UI** (botão "Nova playlist") ou via API:
```bash
curl -X POST -H "X-Admin-Token: dev-admin-key" -H "Content-Type: application/json" \
  -d '{"name":"Minha Lista","format":"m3u","source_url":"http://exemplo/get.php?username=USER&password=PASS&type=m3u_plus&output=mpegts"}' \
  http://localhost:8000/playlists
```
Anote o `playlist_id`.

### 7.2 Ativar o device do Player
```bash
curl -H "X-Admin-Token: dev-admin-key" http://localhost:8000/devices          # ache o device "pending"
curl -X POST -H "X-Admin-Token: dev-admin-key" http://localhost:8000/devices/<device_id>/activate
```

### 7.3 Associar a playlist ao device
```bash
curl -X POST -H "X-Admin-Token: dev-admin-key" -H "Content-Type: application/json" \
  -d '{"device_id":"<device_id>","playlist_id":"<playlist_id>"}' \
  http://localhost:8000/playlists/assignments
```

### 7.4 No app
Pressione **`R`** (hot restart) no terminal do `flutter run` → o app vai ao **menu**; **Ao vivo** carrega os canais.

> Alternativa sem Core: no app, **Mudar lista** → informe a URL M3U (lista local no dispositivo).

---

## Verificação rápida (health checks)

```bash
curl -s http://localhost:8000/health                       # Core
curl -s -H "X-Admin-Token: dev-admin-key" http://localhost:8000/playlists
curl -s -H "X-Admin-Token: dev-admin-key" http://localhost:8000/devices
docker ps | grep nebula-postgres
```
Admin BFF (se estiver rodando): `curl -s http://localhost:8001/health`.

---

## Encerrar tudo

```bash
# processos em foreground (uvicorn/flutter): Ctrl+C em cada terminal
docker stop nebula-postgres      # opcional; o container reinicia com o Docker
```

---

## Troubleshooting (problemas já encontrados)

| Sintoma | Causa | Solução |
|---|---|---|
| Login no Admin falha com `Failed to fetch` | CORS/host errado | BFF com CORS (já habilitado) + `NEBULA_ADMIN_API` apontando para o **IP do WSL** |
| `openapi.json` da 8001 mostra rotas do **Core** (`/devices`, `/playlists`) | BFF subido da pasta errada | Subir o uvicorn a partir de `backend/nebula-admin` (passo 4) |
| Não sabe a senha do Admin UI | `ADMIN_SEED_PASSWORD` sem padrão | Definida em `backend/nebula-admin/.env` (`nebula@2026`) |
| `usbipd attach` → VBoxUsbMon error | driver/usbpcap | reinstalar usbipd + remover USBPcap + reboot (ou usar Wi‑Fi) |
| `adb: unknown command pair` | adb antigo (apt) | usar `$ANDROID_HOME/platform-tools/adb` |
| App: `Falha ao iniciar sessão (409)` | sessão ativa antiga | já corrigido (o Core **retoma** a sessão) |
| App: `Falha na autenticação (401)` | banco recriado (device não existe) | o app **re-registra** sozinho; depois **ative** o device |
| App: `Falha no provisionamento (404)` | sem playlist associada | associe uma playlist (passo 7.3) |
| App não vê o device | USB não anexado ao WSL | refazer `usbipd attach` (não persiste) ou usar Wi‑Fi |

---

## Observações

- **Persistência do Postgres:** volume nomeado `nebula_postgres_data` (não use `down -v`).
- **`develop/`** contém o SDK do Flutter e está no `.gitignore`.
- **Regra de arquitetura (ADR-021):** playlists "oficiais" são gerenciadas no Nebula Admin; o **Player** consome o provisionamento do Core. A lista em **Mudar lista** é **local/pessoal** no dispositivo.
