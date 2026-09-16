---
tipo: Guia
id: STARTUP
projeto: Nebula Platform
status: Ativo
atualizacao: '2026-09-16'
relacionados:
- '[[RUNBOOK]]'
- '[[PROJECT_STATUS-v2]]'
- '[[RELEASES]]'
tags:
- guia
- operacao
aliases:
- Guia de Inicialização dos Serviços
---

# Guia de Inicialização dos Serviços — Nebula Platform

Referência rápida de **caminho absoluto + comando** para subir/reiniciar cada
serviço, na ordem recomendada.

---

## 🔢 Ordem de subida

```
1. NGROK  →  2. PostgreSQL (Docker)  →  3. Nebula Core  →  4. Nebula Admin (BFF)
          →  5. Portal Web (Flutter)  →  6. Mobile (Nebula Player)
```

> O **ngrok** só é necessário quando você for testar **pagamentos** (webhook).

---

## 📍 Caminhos absolutos (resumo)

| # | Serviço | Caminho absoluto | Porta |
|---|---|---|---|
| 1 | ngrok (binário) | `/usr/local/bin/ngrok` | — |
| 2 | PostgreSQL (Docker) | `/home/fealmeida/projects/nebula-plataform/infra/docker` | 5434 |
| 3 | Nebula Core | `/home/fealmeida/projects/nebula-plataform/backend/nebula-core` | 8000 |
| 4 | Nebula Admin (BFF) | `/home/fealmeida/projects/nebula-plataform/backend/nebula-admin` | 8001 |
| 5 | Portal Web (Flutter) | `/home/fealmeida/projects/nebula-plataform/frontend/nebula-admin` | 3000 |
| 6 | Mobile (Player) | `/home/fealmeida/projects/nebula-plataform/frontend/nebula-player` | dispositivo |

**Ferramentas:**

| Ferramenta | Caminho |
|---|---|
| Flutter SDK | `/home/fealmeida/projects/nebula-plataform/develop/flutter/bin/flutter` |
| adb (Android SDK) | `/home/fealmeida/Android/Sdk/platform-tools/adb` |
| uvicorn (venv do Core) | `/home/fealmeida/projects/nebula-plataform/backend/nebula-core/.venv/bin/uvicorn` |

---

## 1) NGROK — túnel público (para o webhook do Mercado Pago)

**Caminho:** `/usr/local/bin/ngrok`

```bash
# subir o serviço (em um terminal dedicado, deixe rodando)
ngrok http 8000

# opcional: domínio estático (evita trocar a URL a cada reinício)
ngrok http 8000 --url=https://<seu-dominio>.ngrok-free.app
```

**Verificar:**
```bash
curl -s http://127.0.0.1:4040/api/tunnels        # lista os túneis ativos
curl -s -o /dev/null -w "%{http_code}\n" https://<sua-url>/health   # esperado: 200
```

> ⚠️ Copie a URL **exata** da linha `Forwarding` (termina em **`.dev`** ou `.app`).
> Ela deve ser a mesma em `MERCADOPAGO_NOTIFICATION_URL` no `.env` do Core.
> Painel de inspeção das requisições: **`http://127.0.0.1:4040`**.

---

## 2) POSTGRESQL (Docker) — porta 5434

**Caminho:** `/home/fealmeida/projects/nebula-plataform/infra/docker`

```bash
# VERIFICAR se está ativo
docker ps --filter name=nebula-postgres
# esperado: nebula-postgres  Up ... (healthy)  0.0.0.0:5434->5432/tcp

# SUBIR o serviço
cd /home/fealmeida/projects/nebula-plataform/infra/docker
docker compose --env-file .env -f compose.yml up -d
```

**Observações:**
- Volume nomeado `nebula_postgres_data` → os dados **persistem**.
- ⚠️ **Nunca** use `docker compose down -v` (o `-v` apaga os dados).

---

## 3) NEBULA CORE — porta 8000

**Caminho:** `/home/fealmeida/projects/nebula-plataform/backend/nebula-core`

```bash
cd /home/fealmeida/projects/nebula-plataform/backend/nebula-core

# (quando houver migrations novas)
./.venv/bin/python -m alembic upgrade head

# SUBIR o serviço
./.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
```

**Verificar:**
```bash
curl -s http://localhost:8000/health        # {"status":"healthy"}
```

> Não precisa exportar variáveis: o Core lê `.env` + `.secrets/` automaticamente
> (senha do banco, JWT e o token do Mercado Pago).

---

## 4) NEBULA ADMIN (BFF) — porta 8001

**Caminho:** `/home/fealmeida/projects/nebula-plataform/backend/nebula-admin`

```bash
cd /home/fealmeida/projects/nebula-plataform/backend/nebula-admin
PYTHONPATH=. /home/fealmeida/projects/nebula-plataform/backend/nebula-core/.venv/bin/uvicorn \
  app.main:app --host 0.0.0.0 --port 8001
```

**Verificar:**
```bash
curl -s http://localhost:8001/health
curl -s http://localhost:8001/openapi.json | grep -o '"/portal[^"]*"' | head
```

> ⚠️ Suba **da pasta `backend/nebula-admin`** — de outra pasta, `app.main:app`
> resolve para o **Core** e a porta 8001 passa a servir as rotas do Core.
> As configurações vêm de `backend/nebula-admin/.env`.

---

## 5) PORTAL WEB (Flutter — usuário **e** administrador) — porta 3000

**Caminho:** `/home/fealmeida/projects/nebula-plataform/frontend/nebula-admin`

```bash
# descubra o IP do WSL (usado pelo navegador do Windows)
hostname -I | cut -d' ' -f1        # ex.: 172.18.88.46

cd /home/fealmeida/projects/nebula-plataform/frontend/nebula-admin
flutter run -d web-server --web-port=3000 --web-hostname=0.0.0.0 \
  --dart-define=NEBULA_ADMIN_API=http://<IP_DO_WSL>:8001 \
  --dart-define=ADMIN_PATH=gestao-nebula-3f9c
```

**Endereços no navegador:**

| Acesso | URL | Login |
|---|---|---|
| **Usuário** | `http://<IP_DO_WSL>:3000` | MAC Address + código de ativação (6 dígitos) |
| **Administrador** | `http://<IP_DO_WSL>:3000/#/gestao-nebula-3f9c` | `admin@nebula.local` / `nebula@2026` |

> ⚠️ **Não confunda as pastas:** o portal é `frontend/nebula-admin`.
> `frontend/nebula-player` é o **app Android** (não roda na web).

---

## 6) MOBILE — Nebula Player (Android)

**Caminho:** `/home/fealmeida/projects/nebula-plataform/frontend/nebula-player`

```bash
# 1) o dispositivo precisa aparecer como "device"
adb devices                    # USB ou Wi-Fi (adb connect <IP>:<porta>)

# 2) entrar na pasta do app
cd /home/fealmeida/projects/nebula-plataform/frontend/nebula-player

# 3) túnel do celular para o Core + rodar
adb -s <SERIAL> reverse tcp:8000 tcp:8000
flutter run -d <SERIAL> \
  --dart-define=NEBULA_CORE_API=http://localhost:8000 \
  --dart-define=NEBULA_PORTAL_URL=http://<IP_DO_WSL>:3000
```

**Atalhos úteis (no terminal do `flutter run`):**

| Tecla | Ação |
|---|---|
| `R` | hot restart (re-executa o boot: registro → auth → provisionamento) |
| `r` | hot reload |
| `q` | encerra o app |

**Verificações no projeto:**
```bash
flutter analyze
flutter test
```

> ⚠️ `10.0.2.2` é o endereço do **emulador**. Em aparelho físico use
> `http://localhost:8000` + `adb reverse` (como acima).

---

## ✅ Verificação rápida de tudo

```bash
docker ps --filter name=nebula-postgres                 # Postgres
curl -s http://localhost:8000/health                    # Core
curl -s http://localhost:8001/health                    # BFF
curl -s -o /dev/null -w "%{http_code}\n" http://localhost:3000   # Portal (200)
curl -s http://127.0.0.1:4040/api/tunnels               # ngrok
adb devices                                             # Mobile
```

---

## 🧯 Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `404` no webhook do MP | URL do ngrok errada (`.app` x `.dev`) | copie a URL **exata** da linha `Forwarding` |
| `address already in use` | serviço antigo na porta | `ss -ltnp \| grep <porta>` → `kill <PID>` |
| Portal mostra o **Player** | `flutter run` na pasta errada | rode de `frontend/nebula-admin` |
| URL do admin cai no portal do usuário | fragmento normalizado | recarregue a **URL completa** `…/#/<ADMIN_PATH>` |
| App não acha o Core | falta `adb reverse` | `adb -s <SERIAL> reverse tcp:8000 tcp:8000` |
| `adb: no devices/emulators found` | Wi‑Fi caiu | reconecte (`adb connect`) ou anexe o USB ao WSL |

---

> Documento complementares: **[`docs/RUNBOOK.md`](RUNBOOK.md)** (operação
> detalhada, licenciamento e pagamentos) e os ADRs **027/028/029**.
