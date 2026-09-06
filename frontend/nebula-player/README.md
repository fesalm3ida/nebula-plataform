# Nebula Player (Flutter Android)

Cliente Android do Nebula Platform. Consome diretamente o **Nebula Core**
(API), seguindo o fluxo de inicialização em `docs/Modules/nebula-player/004-startup-flow.md`.

```
Nebula Player (Flutter) -> Nebula Core (FastAPI) -> PostgreSQL
```

## Requisitos

- Flutter >= 3.22 (SDK 3.4+). Instale: https://docs.flutter.dev/get-started/install

## Como gerar as plataformas e rodar (Android)

Este projeto é entregue como **código-fonte** (`lib/` + `pubspec.yaml`).
A pasta de plataforma `android/` é gerada pelo Flutter:

```bash
cd frontend/nebula-player
flutter create . --platforms android
flutter pub get
flutter run   # em um emulador/device Android
```

Para apontar para o Core:
- Por padrão usa `http://10.0.2.2:8000` (host da máquina a partir do emulador).
- Rode o `nebula-core` na porta 8000: `uvicorn app.main:app --port 8000`.

```
flutter run --dart-define=NEBULA_CORE_API=http://10.0.2.2:8000
```

## Fluxo implementado (scaffold)

1. Gera/persiste a `fingerprint` (NDF) localmente (`shared_preferences`).
2. **Registro:** `POST /devices/register` -> `device_id` + `device_key` (persistidos).
3. **Autenticação:** `POST /auth/device` -> access_token (Bearer).
4. **Sessão:** `POST /sessions` -> `session_id`.
5. **Provisionamento:** `GET /me/provisioning` -> ContentEndpoints (lista de playlists).
6. Botões de **Heartbeat** e **Telemetria** (exemplos de chamadas ao Core).

> Observação: é um robusto scaffold inicial. A reprodução de vídeo em si
> (player de mídia), o catálogo e o tratamento de fluxos alternativos
> (registro pendente/bloqueado/etc.) ficam para as próximas iterações.
