---
tipo: Guia
id: DEPLOY-RENDER
projeto: Nebula Platform
status: Ativo
atualizacao: '2026-09-17'
relacionados:
- '[[STARTUP]]'
- '[[RUNBOOK]]'
- '[[DEPLOY-RAILWAY]]'
- '[[ADR-029]]'
tags:
- deploy
- render
- operacao
aliases:
- Deploy no Render
---

# Deploy do backend Nebula no Render

Guia para publicar **Nebula Core** e **Nebula Admin (BFF)** no
[Render](https://render.com), com banco gerenciado e **HTTPS** — o que dispensa
o ngrok no webhook do Mercado Pago.

Na raiz do repositório existe um **blueprint** ([`render.yaml`](../render.yaml))
que cria tudo automaticamente.

---

## 1. Arquitetura no Render

```
Render (workspace nebula)
├── PostgreSQL           → variável DATABASE_URL injetada no Core
├── nebula-core  (Docker, rootDir backend/nebula-core)
│        https://nebula-core.onrender.com      (health: /health)
└── nebula-admin (Docker, rootDir backend/nebula-admin)
         https://nebula-admin.onrender.com     (health: /health)
         NEBULA_CORE_BASE_URL=https://nebula-core.onrender.com
         NEBULA_CORE_SERVICE_TOKEN=<ADMIN_API_KEY do Core>

Fora do Render:
├── Portal Web (Flutter)  → Render Static Site, Cloudflare Pages ou Netlify
└── Player Android        → aponta para a URL pública do Core
```

Os **Dockerfiles** já existem (`backend/nebula-core/Dockerfile` e
`backend/nebula-admin/Dockerfile`) e:
- instalam o pacote do serviço;
- sobem a API na porta `$PORT` (definida pelo Render);
- no Core, executam **`alembic upgrade head`** antes de iniciar
  → **as migrations aplicam no deploy**, sem passo manual.

---

## 2. Caminho rápido — Blueprint (recomendado)

1. Render → **New → Blueprint**;
2. Conecte o repositório `nebula-plataform` (autorize o GitHub);
3. O Render lê o `render.yaml` e mostra o que será criado:
   **1 PostgreSQL + 2 Web Services (Docker)**;
4. Clique em **Apply**. Ele vai pedir os valores marcados com `sync: false`:
   - `MERCADOPAGO_ACCESS_TOKEN`
   - `MERCADOPAGO_NOTIFICATION_URL` (preencha depois do 1º deploy,
     com a URL do Core + `/webhooks/mercadopago`)
   - `MERCADOPAGO_BACK_URL` (URL do portal, opcional)
   - `NEBULA_CORE_BASE_URL` (URL pública do Core, ex.:
     `https://nebula-core.onrender.com`)
   - `ADMIN_SEED_PASSWORD` (senha do administrador)

> `NEBULA_CORE_SERVICE_TOKEN` é preenchido automaticamente com o
> `ADMIN_API_KEY` gerado pelo Core (`fromService`), então **os dois ficam iguais**.

---

## 3. Caminho manual (se preferir criar um a um)

### 3.1 Banco
1. **New → PostgreSQL**;
   - Name: `nebula-postgres` · Database: `nebula` · User: `nebula`;
   - Region: **a mesma dos serviços** (ex.: Oregon);
   - Plan: **Free** (expira em 30 dias) ou **Starter** (produção).
2. Anote a **Internal Database URL** (uso interno) e a **External** (com
   `?sslmode=require`, para acesso de fora).

### 3.2 Nebula Core
1. **New → Web Service** → repositório `nebula-plataform`;
2. **Language: Docker**;
3. **Root Directory:** `backend/nebula-core`
   **Dockerfile Path:** `./Dockerfile`;
4. **Health Check Path:** `/health`;
5. **Environment Variables:**

| Variável | Valor |
|---|---|
| `DATABASE_URL` | *Internal Database URL* do Postgres (ou o *Connection String*) |
| `JWT_SECRET_KEY` | segredo longo (ex.: `openssl rand -hex 32`) |
| `ADMIN_API_KEY` | segredo (será o token do BFF) |
| `APP_ENV` | `production` |
| `MERCADOPAGO_ACCESS_TOKEN` | token do Mercado Pago |
| `MERCADOPAGO_NOTIFICATION_URL` | `https://<core>.onrender.com/webhooks/mercadopago` |
| `MERCADOPAGO_BACK_URL` | `https://<portal>` (opcional) |

6. **Create Web Service**. Nos **Logs** deve aparecer o `alembic upgrade head`
   e `Uvicorn running on http://0.0.0.0:<PORT>`.

**Verificar:**
```bash
curl -s https://<core>.onrender.com/health      # {"status":"healthy"}
```

### 3.3 Nebula Admin (BFF)
1. **New → Web Service** → o mesmo repositório;
2. **Language: Docker** · **Root Directory:** `backend/nebula-admin`
   · **Dockerfile Path:** `./Dockerfile` · **Health Check:** `/health`;
3. **Environment Variables:**

| Variável | Valor |
|---|---|
| `NEBULA_CORE_BASE_URL` | `https://<core>.onrender.com` |
| `NEBULA_CORE_SERVICE_TOKEN` | **o mesmo** `ADMIN_API_KEY` do Core |
| `ADMIN_JWT_SECRET_KEY` | segredo longo |
| `ADMIN_SEED_EMAIL` | `admin@nebula.local` |
| `ADMIN_SEED_PASSWORD` | senha do administrador |
| `ADMIN_SEED_ROLE` | `super_admin` |

**Verificar:**
```bash
curl -s https://<admin>.onrender.com/health
curl -s https://<admin>.onrender.com/openapi.json | grep -o '"/portal[^"]*"' | head
```

### 3.4 Webhook do Mercado Pago
A URL é **fixa** (`https://<core>.onrender.com/webhooks/mercadopago`) — sem
ngrok. Faça uma compra de teste e confira nos **Logs do Core**:
`POST /webhooks/mercadopago 200 OK`.

### 3.5 Portal Web (Flutter)
O endereço da API entra em **tempo de build**:
```bash
cd frontend/nebula-admin
flutter build web --release \
  --dart-define=NEBULA_ADMIN_API=https://<admin>.onrender.com \
  --dart-define=ADMIN_PATH=<sua-rota-secreta>
```
Publique `build/web` como **Static Site** no Render (ou Cloudflare Pages/Netlify):
- **Usuário:** `https://<portal>/`
- **Administrador:** `https://<portal>/#/<ADMIN_PATH>`

### 3.6 Player Android
```bash
cd frontend/nebula-player
flutter build apk --release \
  --dart-define=NEBULA_CORE_API=https://<core>.onrender.com \
  --dart-define=NEBULA_PORTAL_URL=https://<portal>
```

---

## 4. ⚠️ Atenção ao plano Free

| Limite | Impacto no Nebula |
|---|---|
| Web Service **free dorme após ~15 min** sem tráfego | a primeira requisição demora ~30–60 s (cold start). **O webhook do Mercado Pago pode estourar o timeout** — o MP reenvia, mas com atraso. Para o webhook, use o plano **Starter** (US$ 7/mês) no Core. |
| PostgreSQL **free expira em 30 dias** | os dados são apagados. Para produção: **Starter** ou um banco externo (**Neon**/**Supabase**, gratuitos) — basta apontar `DATABASE_URL`. |
| 750 h/mês de instância free | suficiente para 1 serviço 24/7, **não** para dois. |

> 💡 Combinação econômica e estável: **Core** em plano **Starter** (por causa do
> webhook) + **BFF** e **portal** em Free/Static + **Postgres no Neon** (free).

---

## 5. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| Deploy falha com *"health check failed"* | app não subiu ou `/health` inacessível | veja os Logs; confirme que o serviço usa a porta `$PORT` |
| `ValueError: Provide DATABASE_URL or POSTGRES_PASSWORD` | faltou a variável do banco | configure `DATABASE_URL` no Core |
| BFF responde **502** | `NEBULA_CORE_BASE_URL` errado ou Core dormindo | confira a URL e o `/health` do Core |
| Ações admin/portal dão **401** | tokens de serviço diferentes | `NEBULA_CORE_SERVICE_TOKEN` = `ADMIN_API_KEY` |
| Banco apagado após ~30 dias | Postgres **free** expirou | mude para Starter ou Neon/Supabase |
| Webhook do MP com timeout | Core free dormindo (cold start) | plano Starter no Core |
| Migrations não aplicam | `alembic.ini`/`migrations` fora da imagem | confira o `COPY` no Dockerfile do Core |

---

> Relacionados: **[`STARTUP`](STARTUP.md)** (ambiente local) ·
> **[`RUNBOOK`](RUNBOOK.md)** (operação, licenciamento e pagamentos) ·
> **[`DEPLOY-RAILWAY`](DEPLOY-RAILWAY.md)** (alternativa) ·
> **ADR-029** (pagamentos).
