---
tipo: Guia
id: IOS
projeto: Nebula Platform
status: Ativo
atualizacao: '2026-09-23'
relacionados:
- '[[STARTUP]]'
- '[[DEPLOY-RENDER]]'
- '[[ADR-028]]'
tags:
- ios
- player
- build
aliases:
- Nebula Player no iPhone
---

# Nebula Player no iPhone (iOS)

Guia do app do Player para **iOS**: o que já está pronto, o que exige macOS e
como instalar no aparelho sem ter um Mac.

---

## 1. ⚠️ A restrição que define tudo

**Compilar, assinar e instalar iOS exige macOS + Xcode.** Não existe toolchain
de iOS para Windows/Linux — portanto o WSL **não** consegue gerar nem instalar o
app no iPhone.

O que **é** possível de qualquer sistema:

| Tarefa | Onde roda |
|---|---|
| Escrever/configurar o projeto iOS (`ios/`) | ✅ WSL/Linux (já feito) |
| Validar o build (`flutter build ios --no-codesign`) | ✅ **CI macOS** (GitHub Actions — workflow já no repositório) |
| Assinar e instalar no iPhone | ❌ exige Mac **ou** ferramenta de sideload com Apple ID |
| Publicar no TestFlight / App Store | ❌ exige Mac (Xcode) ou CI com a conta Apple |

---

## 2. O que já está pronto no repositório

Pasta `frontend/nebula-player/ios/` gerada e configurada:

| Item | Valor |
|---|---|
| **Bundle Identifier** | `com.nebula.player` |
| **Nome exibido** | `Nebula Player` |
| **iOS mínimo** | **15.0** |
| **ATS (http)** | `NSAllowsArbitraryLoads` + `…InMedia` — **essencial**: as listas M3U e os streams de IPTV costumam ser `http://` (equivale ao `usesCleartextTraffic` do Android) |
| **Áudio em segundo plano** | `UIBackgroundModes: audio` |
| **Orientações** | retrato + paisagem (vídeo em tela cheia) |
| **Player de vídeo** | `media_kit` com `media_kit_libs_ios_video` (libmpv) — suporte a iOS já resolvido pelo pubspec |

O código do app é **portável**: a única API de sistema usada é
`SocketException` (`dart:io`), e a identidade do aparelho já é um **pseudo-MAC
gerado e persistido localmente** (o iOS não expõe o MAC real) — o mesmo
comportamento do Android.

**CI:** `.github/workflows/ios-build.yml` roda no `macos-latest`:

- `flutter pub get` → `flutter analyze` → `flutter test`;
- `pod install`;
- `flutter build ios --release --no-codesign`;
- publica como *artifact* o **`Runner.app`** e um **IPA sem assinatura**.

> Dispare em **Actions → iOS build → Run workflow**.
> ⚠️ Em repositório privado, runner macOS consome minutos com **multiplicador
> 10×** (cota de 2.000 min/mês ≈ **200 min de macOS**) — por isso ele só roda
> manualmente ou quando `frontend/nebula-player/**` muda.

---

## 3. Caminhos para ter o app no iPhone

### 🅰️ Com um Mac (o caminho oficial)
```bash
cd frontend/nebula-player
flutter pub get
cd ios && pod install && cd ..

# com o iPhone conectado e confiado no Mac:
flutter run -d <device-id> \
  --dart-define=NEBULA_CORE_API=https://nebula-core-6hq4.onrender.com \
  --dart-define=NEBULA_PORTAL_URL=https://nebula-plataform-portal.onrender.com
```
No Xcode: **Runner → Signing & Capabilities → Team** (seu Apple ID).
- **Apple ID gratuito:** o app instalado **expira em 7 dias** e precisa ser
  reinstalado (cabo + Xcode) — serve para testes;
- **Apple Developer Program (US$ 99/ano):** builds válidos por 1 ano,
  **TestFlight** e distribuição.

### 🅱️ Sem Mac — IPA do CI + sideload no Windows
1. Rode o workflow **iOS build** e baixe o artifact
   **`nebula-player-ios-ipa`** (`nebula-player-unsigned.ipa`);
2. No Windows, use **Sideloadly** (ou AltStore) com o seu **Apple ID** — a
   ferramenta assina o IPA na hora e instala no iPhone conectado por USB;
3. Mesma limitação do Apple ID gratuito: **expira em 7 dias** (basta re-assinar
   e reinstalar).

### 🅲 Serviços de Mac na nuvem
**Codemagic** (free tier com minutos macOS, feito para Flutter), **Xcode Cloud**
(Apple) ou **MacinCloud/MacStadium** — úteis para assinar, subir ao TestFlight e
automatizar releases.

---

## 4. Antes de publicar na App Store (atenção)

- A Apple **rejeita com frequência** apps que apenas reproduzem listas de IPTV de
  terceiros (violação de direitos autorais / diretriz 5.2.3). Para distribuir
  oficialmente, o app precisa de **conteúdo próprio/licenciado**, demonstração
  clara de conteúdo livre e política de privacidade;
- **Privacidade:** declarar em *App Privacy* os dados coletados (MAC, eventos de
  telemetria do Nebula Monitor);
- **Tamanho:** o libmpv (media_kit) aumenta o bundle; avalie *thinning* e
  revisão de codecs.

> Para uso **interno/testes** (o objetivo agora), o caminho A ou B resolve sem
> esse debate — a revisão só vale para distribuição pública.

---

## 5. Próximos passos sugeridos

1. Rodar o CI iOS e corrigir o que aparecer (é o primeiro build da plataforma);
2. **Ícone do app** a partir de `assets/logo.png` (o iOS exige 1024×1024 sem
   transparência) — hoje está o ícone padrão do Flutter;
3. Ajustes de UX específicos de iOS: gesto de voltar pela borda, *safe areas*,
   orientação travada no player;
4. Testar o ciclo completo no aparelho: registro → ativação (MAC + código) →
   lista provisionada → reprodução → telemetria aparecendo no Monitor.
