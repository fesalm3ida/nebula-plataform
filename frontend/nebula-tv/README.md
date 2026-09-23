# Nebula TV (LG Smart TV / webOS)

App do Nebula Player para **LG Smart TV**, em **web nativo** (HTML/CSS/JS)
empacotado como app webOS (`.ipk`).

## Por que web nativo (e não Flutter)

| | App web nativo | Flutter Web |
|---|---|---|
| Compatibilidade | **todas** as versões (webOS 3+) | só webOS 6+ (exige WASM + WebGL2) |
| Vídeo | **pipeline de hardware da TV** (HLS no hardware) | renderização no Chromium da TV |
| Peso | leve (poucos KB) | CanvasKit (MB) em hardware fraco |

O runtime web do webOS é um Chromium e o app usa o mesmo backend do app
Android (`Nebula Core`), então a escolha é só de camada de apresentação.

## Estrutura

```
appinfo.json     metadados do app webOS (id, ícone, resolução)
index.html       telas: boot, ativação, menu, catálogo, player
css/tv.css       tema roxo/preto e foco para controle remoto (10-foot UI)
js/api.js        cliente da API do Nebula Core (registro, auth, sessão, telemetria)
js/m3u.js        parser M3U/M3U_PLUS (mesmas regras do app Android)
js/app.js        fluxo do app e navegação por controle remoto
test/            testes do parser (Node)
icons/           ícones e fundo exigidos pelo pacote
```

## Desenvolvimento

```bash
# A CLI oficial do webOS (comandos ares):
npm install -g @webos-tools/cli

npm test                    # parser M3U + busca + consistência
```

### Instalar na TV (modo desenvolvedor)

1. Na TV: loja de apps → instale **Developer Mode** → ative → anote **IP**,
   **porta** e a **passphrase**;
2. No PC (a CLI roda em Linux/WSL, macOS e Windows):
   ```bash
   npm install -g @webos-tools/cli

   npm run device:add       # name: tv | host: <IP> | port: 9922 | passphrase: <da TV>
   npm run device:list      # confere
   npm run device:info      # a TV responde?

   npm test                 # testes do app
   npm run package          # gera dist/com.nebula.tv_0.1.0_all.ipk
   npm run install:tv
   npm run launch
   ```
3. A "sessão" do modo desenvolvedor expira periodicamente — reative no app
   **Developer Mode** da TV e repita `install`/`launch`.

### API do Core

O endereço do backend é definido em `js/app.js` (`CORE_API`) e pode ser
sobrescrito definindo `window.NEBULA_CORE_API` antes do script:

```html
<script>window.NEBULA_CORE_API = 'http://192.168.15.10:8000';</script>
```

## Catálogo (busca + grade de pôsteres)

- **Grade de pôsteres** para Filmes e Séries (usa o `tvg-logo` da lista) e grade
  de canais para o Ao vivo, com agrupamento por categoria na coluna da esquerda;
- **Busca por título**: selecione o campo de busca e aperte **OK** — o webOS abre
  o **teclado virtual da TV**; o filtro aplica enquanto você digita (debounce de
  250 ms) e ignora acentos e maiúsculas, aceitando vários termos em qualquer
  ordem (mesmas regras do app Android);
- **Navegação espacial**: as setas do controle escolhem o vizinho mais próximo
  na direção (funciona em grade, lista e colunas);
- Listas gigantes (dezenas de milhares de itens) renderizam no máximo **240**
  cards por vez, com aviso para refinar pela busca.

## Testes

```bash
npm test    # parser M3U + busca + consistência da estrutura (Node)
```

## Fluxo do app

1. **Registro**: gera uma identidade local (pseudo-MAC, como no Android — o
   webOS não expõe o MAC real) e registra no Core;
2. **Ativação**: exibe **MAC + código de 6 dígitos**; o usuário ativa no portal;
3. **Provisionamento**: baixa as listas provisionadas e faz o parse do M3U;
4. **Catálogo**: Ao vivo · Filmes · Séries, com categorias e navegação por
   setas do controle;
5. **Player**: `<video>` em tela cheia; **OK** pausa/retoma, **Voltar** sai;
6. **Telemetria**: envia `playback_started` / `playback_ended` ao Nebula Monitor.

## Atalhos do controle

| Tecla | Ação |
|---|---|
| ↑ ↓ ← → | navegar |
| OK (Enter) | selecionar / pausar-retomar no player |
| Voltar (461) | voltar de tela / sair do player |
