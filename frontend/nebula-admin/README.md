# Nebula Admin UI (Flutter Web)

Interface administrativa do Nebula Platform. Consome o **Nebula Admin**
(backend BFF em `backend/nebula-admin`), que por sua vez consome o **Nebula Core**.

```
Flutter Admin (Web) -> Nebula Admin (FastAPI BFF) -> Nebula Core
```

## Requisitos

- Flutter >= 3.22 (SDK 3.4+). Instale em: https://docs.flutter.dev/get-started/install

## Como gerar as plataformas e rodar (Web)

Este projeto é entregue como **código-fonte** (`lib/` + `pubspec.yaml`).
As pastas de plataforma (ex.: `web/`) são geradas pelo Flutter:

```bash
cd frontend/nebula-admin
flutter create . --platforms web   # gera web/
flutter pub get
flutter run -d chrome
```

Para apontar para o backend Admin:
- Por padrão usa `http://localhost:8001` (defina no `NEBULA_ADMIN_API`).
- Rode o `nebula-admin` na porta 8001 (ou ajuste): `uvicorn app.main:app --port 8001`
  (defina `ADMIN_JWT_SECRET_KEY`, `ADMIN_SEED_PASSWORD`, `NEBULA_CORE_BASE_URL`,
  `NEBULA_CORE_SERVICE_TOKEN` no `.env`).

```
flutter run -d chrome --dart-define=NEBULA_ADMIN_API=http://localhost:8001
```

## Fluxo de login

1. `POST /admin/auth/login` (credenciais de bootstrap) -> Admin JWT.
2. O token é usado como `Authorization: Bearer <jwt>` nas chamadas
   `/admin/playlists`.

> Observação: este scaffold não persiste o token entre sessões (YAGNI). Em
> produção pode-se adicionar armazenamento seguro do token de sessão.
