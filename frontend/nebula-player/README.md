# Nebula Player (Flutter Android)

Cliente Android do Nebula Platform. Consome diretamente o **Nebula Core**
(API), seguindo o fluxo de inicialização em `docs/Modules/nebula-player/004-startup-flow.md`.

```
Nebula Player (Flutter) -> Nebula Core (FastAPI) -> PostgreSQL
```

## Identidade visual

A marca é a do logotipo oficial do projeto (`assets/logo.png`, na raiz do
repositório) e é a **mesma** do app da TV: os dois clientes saem de
`tools/brand/build_brand_assets.py`, ninguém redesenha nada à mão.

### Paleta

Os tokens ficam em `lib/theme/nebula_theme.dart` (`NebulaColors`) e são os
mesmos do `frontend/nebula-tv/css/brand.css`:

| Token | Cor | De onde vem no logotipo |
|---|---|---|
| `NebulaColors.space` | `#05000F` | fundo preto-violeta |
| `NebulaColors.night` | `#150033` | violeta profundo da nebulosa |
| `NebulaColors.violet` | `#8B02FA` | violeta da marca, a cor dominante |
| `NebulaColors.magenta` | `#C42BFF` | magenta do anel e do "play" |
| `NebulaColors.glow` | `#E9A6FF` | halo claro das bordas |
| `NebulaColors.textPrimary` | `#F7F7FA` | wordmark NEBULA |

O app inteiro já lia `NebulaColors.*`, então os nomes antigos (`primary`,
`backgroundTop`, `surface`…) foram mantidos **apontando para a marca**: a
identidade chega a todas as telas sem reescrever cada uma. Trocar a paleta é
trocar um bloco só — e o mesmo bloco existe no app da TV.

### Onde a marca aparece

| Elemento | Onde | Arquivo |
|---|---|---|
| **Lockup** (marca + NEBULA PLAY + assinatura) | abertura e ativação | `assets/brand/logo-nebula.png` |
| **Selo** | barra de título de toda tela (`NebulaAppBar`) | `assets/brand/mark.png` |
| **Wordmark** | topo do menu: `Nebula` branco + `Player` violeta | `NebulaWordmark` |
| **Marca d'água** | canto do vídeo, junto com os controles | `NebulaMark` |
| **Fundo** | fundo de todas as telas + fio de luz no topo | `assets/brand/bg-app.jpg` |
| **Ícone e splash** | lançador e abertura do Android | `android/app/src/main/res/` |

Os widgets de marca estão em `lib/widgets/brand.dart`. O `_Arte` deles tem
`errorBuilder`: um asset ausente deixa a tela sem a arte em vez de virar
exceção de renderização (e os testes não dependem do bundle).

### Ícone e splash do Android

O ícone do lançador sai em todas as densidades, mais a **camada de frente do
ícone adaptativo** (API 26+, com a folga da área segura que o Android recorta) e
o `monochrome` do Android 13+. O splash nativo deixou de ser **branco** — o app
abria com um clarão e só depois ficava escuro — e agora traz o "espaço" da marca
com a marca ao centro, em `drawable-<densidade>/splash_logo.png` (sem densidade
o Android trataria o PNG como mdpi e o esticaria).

### Regerar a arte

```bash
python3 tools/brand/build_brand_assets.py     # precisa de Pillow
```

O script escreve **nos dois apps** de uma vez (TV e Android). Ele reproduz byte
a byte o que já está instalado na TV, então rodar de novo não muda nada por
acidente.

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

## Build do APK (importante)

O aparelho precisa apontar para o **Core publicado**. Sem os `--dart-define` o
APK usa `http://10.0.2.2:8000` (endereco do emulador) e o app exibe
*"Nao foi possivel falar com o servidor"* em celulares.

```bash
flutter build apk --release --target-platform android-arm64 \
  --dart-define=NEBULA_CORE_API=https://nebula-core-6hq4.onrender.com \
  --dart-define=NEBULA_PORTAL_URL=https://nebula-plataform-portal.onrender.com
```

Para conferir o que foi gravado no APK:

```bash
unzip -p build/app/outputs/flutter-apk/app-release.apk \
  lib/arm64-v8a/libapp.so | strings | grep -oE "https://nebula-[a-z0-9.-]+" | sort -u
```
