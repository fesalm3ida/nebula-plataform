---
tipo: Guia
id: DEPLOY-RAILWAY
projeto: Nebula Platform
status: Ativo
atualizacao: '2026-09-17'
relacionados:
- '[[STARTUP]]'
- '[[RUNBOOK]]'
- '[[ADR-026]]'
- '[[ADR-029]]'
tags:
- deploy
- railway
- operacao
aliases:
- Deploy no Railway
---

# Deploy do backend Nebula no Railway

Guia para publicar **Nebula Core** e **Nebula Admin (BFF)** no
[Railway](https://railway.com), com banco gerenciado e **HTTPS** — o que
dispensa o ngrok no webhook do Mercado Pago.

---

## 1. Arquitetura no Railway

```
Railway (projeto: nebula)
├── Postgres            (plugin gerenciado)  → DATABASE_URL / PG*
├── nebula-core         (Docker)   → https://nebula-core-xxxx.up.railway.app
└── nebula-admin        (Docker)   → https://nebula-admin-xxxx.up.railway.app
                                     NEBULA_CORE_BASE_URL=https://nebula-core-xxxx...
                                     NEBULA_CORE_SERVICE_TOKEN=<mesmo ADMIN_API_KEY do Core>

Fora do Railway:
├── Portal Web (Flutter)  → Cloudflare Pages / Netlify (estático) — ou outro serviço
└── Player Android        → aponta para a URL pública do Core
```

Os **Dockerfiles** já existem no repositório:

| Serviço | Dockerfile |
|---|---|
| Core | `backend/nebula-core/Dockerfile` |
| BFF | `backend/nebula-admin/Dockerfile` |

---

## 2. PostgreSQL: plugin gerenciado **ou** Postgres em Docker?

### ✅ Opção A — Plugin **PostgreSQL** do Railway (recomendado)

```text
New → Database → Add PostgreSQL
```

O Railway cria o banco e disponibiliza as variáveis
`DATABASE_URL`, `PGHOST`, `PGPORT`, `PGUSER`, `PGPASSWORD`, `PGDATABASE`.
No serviço do **Core**, aponte a variável para o banco usando *reference*:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

**Por que usar:** backup automático, atualizações de versão, monitoramento e
alta disponibilidade são gerenciados pela plataforma. O **Core já aceita
`DATABASE_URL`** (e também as variáveis `PG*`) — foi preparado exatamente para
isso.

### ⚠️ Opção B — Postgres **em Docker** dentro do Railway (não recomendado)

Tecnicamente é possível: criar um serviço com a imagem `postgres:16-alpine` e
montar um **Volume** em `/var/lib/postgresql/data`.

Mas os contras são grandes:

| Ponto | Consequência |
|---|---|
| **Filesystem efêmero** | **Sem Volume, os dados são perdidos** a cada deploy/reinício |
| Volume | só **1 volume por serviço**, e custa **$0,15/GB·mês** |
| Backup | **você** tem que fazer (`pg_dump` + storage externo) |
| Atualização/monitoração/HA | todas por sua conta |
| Custo | a memória do container é cobrada **igual** ao plugin |
| Rede | precisa expor/ligar serviços manualmente |

> **Conclusão:** use **Docker + Postgres local** para desenvolvimento
> (é o que o `infra/docker/compose.yml` já faz) e o **plugin gerenciado** no
> Railway. Rodar o Postgres em container no Railway só faz sentido para
> reproduzir um cenário muito específico — e você assume backup e persistência.

---

## 3. Passo a passo

### 3.1 Projeto e banco

1. [railway.com](https://railway.com) → **New Project**;
2. **Add PostgreSQL** (fica pronto em ~30 s).

### 3.2 Serviço do Core

1. **New → GitHub Repo** → selecione `nebula-plataform`;
2. **Settings → Root Directory** = `backend/nebula-core`
   (o Railway detecta o `Dockerfile` automaticamente);
3. **Variables**:

```bash
DATABASE_URL=${{Postgres.DATABASE_URL}}
JWT_SECRET_KEY=<segredo-longo-aleatorio>
ADMIN_API_KEY=<segredo-compartilhado-com-o-bff>
APP_ENV=production

# Mercado Pago
MERCADOPAGO_ACCESS_TOKEN=<token do MP>
MERCADOPAGO_NOTIFICATION_URL=https://<dominio-do-core>/webhooks/mercadopago
MERCADOPAGO_BACK_URL=https://<dominio-do-portal>
```

4. **Settings → Networking → Generate Domain** → anote a URL HTTPS.

> As **migrations rodam sozinhas** no start do container
> (`alembic upgrade head` faz parte do `CMD` do Dockerfile).

**Verificar:**
```bash
curl -s https://<dominio-do-core>/health      # {"status":"healthy"}
```

### 3.3 Serviço do BFF (Nebula Admin)

1. **New → GitHub Repo** → o mesmo repositório;
2. **Settings → Root Directory** = `backend/nebula-admin`;
3. **Variables**:

```bash
ADMIN_JWT_SECRET_KEY=<segredo-longo-aleatorio>
ADMIN_SEED_EMAIL=admin@nebula.local
ADMIN_SEED_PASSWORD=<senha-do-admin>
ADMIN_SEED_ROLE=super_admin
NEBULA_CORE_BASE_URL=https://<dominio-do-core>
NEBULA_CORE_SERVICE_TOKEN=<mesmo valor de ADMIN_API_KEY do Core>
```

4. **Generate Domain** → anote a URL HTTPS do BFF.

> `NEBULA_CORE_SERVICE_TOKEN` **precisa ser igual** ao `ADMIN_API_KEY` do Core.

**Verificar:**
```bash
curl -s https://<dominio-do-bff>/health
curl -s https://<dominio-do-bff>/openapi.json | grep -o '"/portal[^"]*"' | head
```

### 3.4 Webhook do Mercado Pago

1. Copie o domínio HTTPS do **Core**;
2. Garanta que `MERCADOPAGO_NOTIFICATION_URL` aponta para
   `https://<dominio-do-core>/webhooks/mercadopago`;
3. Faça uma compra de teste (comprador/cartão de teste) e confira em
   **Railway → Core → Logs** a linha `POST /webhooks/mercadopago 200 OK`.

> Com domínio fixo, **não é mais necessário ngrok**.

### 3.5 Portal Web (Flutter)

O app é **estático** e o endereço da API entra em tempo de **build**:

```bash
cd frontend/nebula-admin
flutter build web --release \
  --dart-define=NEBULA_ADMIN_API=https://<dominio-do-bff> \
  --dart-define=ADMIN_PATH=<sua-rota-secreta>
```

Publique a pasta `build/web` em **Cloudflare Pages**, **Netlify** ou um serviço
estático do Railway. Endereços resultantes:

- **Usuário:** `https://<portal>/`
- **Administrador:** `https://<portal>/#/<ADMIN_PATH>`

### 3.6 Player Android

Recompile apontando para o Core público (sem `adb reverse`):

```bash
cd frontend/nebula-player
flutter build apk --release \
  --dart-define=NEBULA_CORE_API=https://<dominio-do-core> \
  --dart-define=NEBULA_PORTAL_URL=https://<portal>
```

---

## 4. Custo esperado no Railway

Cobrança **por segundo** do que o serviço usa
([tabela oficial](https://railway.com/pricing)):

| Recurso | Tarifa |
|---|---|
| Memória | $10 / GB·mês |
| CPU | $20 / vCPU·mês (uso real) |
| Volume | $0,15 / GB·mês |
| Egress | $0,05 / GB |

Plano **Hobby ($5/mês, com $5 de crédito)**. Estimativa do stack Nebula
(Core 512 MB + BFF 512 MB + Postgres 512 MB, rodando 24/7):

**≈ $12 a $20/mês.** O vilão é a **memória rodando o tempo todo** — o plano
*Free* ($1/mês de crédito) não sustenta produção.

> 💡 Para reduzir: rode o BFF sob demanda, use menos memória por serviço ou
> migre os serviços para um VPS (Hetzner ≈ €4/mês) mantendo o **Postgres no
> plugin** do Railway.

---

## 5. Problemas comuns

| Sintoma | Causa | Solução |
|---|---|---|
| Core reinicia com `ValueError: Provide DATABASE_URL or POSTGRES_PASSWORD` | faltou a variável do banco | configure `DATABASE_URL=${{Postgres.DATABASE_URL}}` |
| `ModuleNotFoundError: httpx` no Core | dependência de runtime faltando (corrigido) | garanta o `httpx` nas dependências (já está no `pyproject`) |
| BFF responde **502** em tudo | `NEBULA_CORE_BASE_URL` errado/fora do ar | confira a URL do Core e o `/health` |
| Ações administrativas dão **401** | tokens de serviço diferentes | `NEBULA_CORE_SERVICE_TOKEN` = `ADMIN_API_KEY` |
| Webhook do MP retorna **422** | notificação `merchant_order` (já suportada) | atualize o deploy para a versão atual do Core |
| Migrations não aplicam | `alembic.ini`/`migrations` fora da imagem | confira o `COPY` no `Dockerfile` do Core |
| Admin cai no portal do usuário | fragmento normalizado | acesse a **URL completa** `…/#/<ADMIN_PATH>` |

---

> Relacionados: **[`STARTUP`](STARTUP.md)** (subir tudo localmente) ·
> **[`RUNBOOK`](RUNBOOK.md)** (operação, licenciamento e pagamentos) ·
> **ADR-026** (Admin/BFF) · **ADR-029** (pagamentos).
