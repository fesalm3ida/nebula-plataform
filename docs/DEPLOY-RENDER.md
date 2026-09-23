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

## 4.1 Publicar o Portal Web no Render (passo a passo)

O portal é um app **estático** (Flutter Web). O Render **não** tem o Flutter no
ambiente de build, então fazemos o build **localmente** e publicamos o
resultado como **Static Site** (gratuito, com CDN e sem *cold start*).

### a) Build local apontando para as APIs do Render
```bash
cd /home/fealmeida/projects/nebula-plataform/frontend/nebula-admin
chmod +x build_web.sh

./build_web.sh https://nebula-admin-ciri.onrender.com painel-nbl-7f2c9a
```
> Troque os dois argumentos pelos **seus**: a URL do **BFF** e a **rota secreta
> do administrador** (evite a de exemplo em produção).
> O script gera `build/web` e copia para **`deploy/web`**.

### b) Versionar o resultado e enviar
```bash
cd /home/fealmeida/projects/nebula-plataform
git add frontend/nebula-admin/deploy
git commit -m "build(portal): web build apontando para o Render"
git push origin main
```

### c) Criar o Static Site no Render
Render → **New → Static Site** → conecte `nebula-plataform` e preencha:

| Campo | Valor |
|---|---|
| **Name** | `nebula-portal` (define o subdomínio) |
| **Branch** | `main` |
| **Build Command** | `echo "build ja versionado em deploy/web"` |
| **Publish Directory** | `frontend/nebula-admin/deploy/web` |

Clique em **Create Static Site** → o deploy leva ~1 min.

### d) Acessos
```text
Usuário:        https://<portal>.onrender.com
Administrador:  https://<portal>.onrender.com/#/painel-nbl-7f2c9a
```

### e) Fechar o ciclo
1. **nebula-core → Environment:**
   `MERCADOPAGO_BACK_URL = https://<portal>.onrender.com`
   (https ⇒ o Mercado Pago devolve o usuário ao portal após o pagamento);
2. **App Android** recompilado com a URL do portal:
   ```bash
   cd frontend/nebula-player
   flutter run -d <SERIAL> \
     --dart-define=NEBULA_CORE_API=https://nebula-core-6hq4.onrender.com \
     --dart-define=NEBULA_PORTAL_URL=https://<portal>.onrender.com
   ```

> **Automatizar o build no Render (alternativa):** em vez do build local, é
> possível usar um **Web Service (Docker)** com um estágio Flutter
> (`ghcr.io/cirruslabs/flutter:stable`) e servir com nginx — fica automático a
> cada push, mas perde o CDN/estático do Static Site e o Free dorme.

---

## 4.2 Keep-warm (evitar o cold start)

No plano **Free** o Render dorme após ~15 min sem tráfego e a primeira
requisição paga **~25 s** de cold start. Isso atrapalha o **webhook do Mercado
Pago** (que precisa de resposta rápida) e a experiência no portal.

Há duas formas de manter os serviços acordados:

### a) UptimeRobot (externo, sem mexer no repositório)
1. Crie uma conta em <https://uptimerobot.com>;
2. **Add New Monitor**:
   | Campo | Valor |
   |---|---|
   | Monitor Type | **HTTP(s)** |
   | Friendly Name | `Nebula Core` |
   | URL | `https://nebula-core-6hq4.onrender.com/health` |
   | Monitoring Interval | **10 minutes** |
   | Alert Contacts | seu e-mail (opcional) |
3. (Opcional) Em *Advanced*, valide a palavra **`healthy`** no conteúdo;
4. Repita para o **BFF** (`https://nebula-admin-ciri.onrender.com/health`).

> O plano gratuito permite vários monitores e intervalo de 5 minutos.

### b) GitHub Actions (versionado no repositório)
O workflow [`.github/workflows/keep-warm.yml`](../.github/workflows/keep-warm.yml)
faz o ping a cada 10 minutos (Core e BFF) e pode ser disparado manualmente
(*Actions → Keep-warm → Run workflow*).

> Limitações: o cron mínimo do GitHub é 5 min, pode atrasar alguns minutos e
> workflows agendados são desativados após ~60 dias sem commits no repositório.

### c) Alternativa definitiva
Plano **Starter** no Core (US$ 7/mês): a instância não dorme e o webhook
responde sempre de imediato.

---

## 5. Problemas comuns

> Os quatro primeiros itens são **casos reais** do primeiro deploy (todos já
> corrigidos no código ou documentados aqui).

| Sintoma | Causa | Solução |
|---|---|---|
| **Todas** as rotas dão **500**, mas `/health` responde 200 | faltava variável de ambiente (ex.: `NEBULA_CORE_BASE_URL`): o `get_settings()` estourava dentro da dependência de cada rota | definir a variável. **Já corrigido**: os serviços validam a configuração na subida e o deploy falha com erro claro |
| `502 Failed to reach the Nebula Core` **na primeira** chamada | cold start do Core free (~25 s) vs. timeout padrão do httpx (5 s) | **já corrigido**: 60 s (BFF→Core) e 20 s (Core→MP); complementar com *keep-warm* |
| APK **release** com `Failed host lookup: ...onrender.com` (em debug funciona) | o template do Flutter declara `INTERNET` **apenas** nos manifests de `debug/` e `profile/` | **já corrigido**: `INTERNET` no `android/app/src/main/AndroidManifest.xml` |
| Blueprint: *"Blueprint file render.yaml not found on main branch"* mesmo após o push | o Render usa um snapshot antigo do repositório | recarregar (**F5**) e refazer **New → Blueprint** (ou reconectar o GitHub App) |
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
