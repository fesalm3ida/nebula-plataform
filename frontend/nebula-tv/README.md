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

Siga a documentação oficial
([App Testing with Developer Mode App](https://webostv.developer.lge.com/develop/getting-started/developer-mode-app)).

**Pré-requisitos:** TV e PC na **mesma rede**; CLI webOS no PC
(`npm install -g @webos-tools/cli`); **conta no LG Developer site**
(https://developer.lge.com — gratuita).

1. **Instalar o app Developer Mode na TV**: LG Apps → buscar *Developer Mode* →
   Install;
2. **Ativar**: abrir o app → entrar com **e-mail e senha da conta LG Developer** →
   botão **Dev Mode Status** → a TV **reinicia**;
   > ⚠️ Ao expirar a sessão (ou após 10 reinícios sem rede), o Developer Mode é
   > desativado e **os apps instalados por ele são desinstalados**.
3. **Registrar a TV no PC**:
   ```bash
   npm run device:add
   #  Device Name ...... tv
   #  Device IP ........ <IP mostrado na TV>       (ex.: 192.168.15.4)
   #  Device Port ...... 9922
   #  ssh user ......... prisoner                  <-- usuario fixo
   #  description ...... nebula tv
   #  Set default? ..... Yes
   #  Save? ............ Yes
   #  Password ......... NAO e necessario (o Developer Mode nao usa senha)
   npm run device:list
   ```
4. **Autorizar o PC (Key Server)**: no app Developer Mode da TV clique em
   **Key Server** e depois, no PC:
   ```bash
   npm run device:key      # ares-novacom --device tv --getkey
   # input passphrase: <os 6 caracteres no canto inferior esquerdo da TV>
   ```
5. **Conferir a conexão**:
   ```bash
   npm run device:info     # ares-device --system-info --device tv
   # modelName / sdkVersion / firmwareVersion ...
   ```
6. **Empacotar e instalar o Nebula TV**:
   ```bash
   npm test
   npm run package         # dist/com.nebula.tv_0.1.0_all.ipk
   npm run install:tv
   npm run launch
   ```

> 💡 Os comandos usam o device marcado como **(default)** em
> `ares-setup-device --list`. Para escolher outro, acrescente
> `--device <nome>` (ex.: `ares-install ... --device lg-sala`).

### Como o app chega na TV

O app **não atualiza sozinho**: ele é um pacote instalado (como um app de
loja). Toda alteração precisa ser **reempacotada e reinstalada**:

```bash
npm run deploy        # package -> install -> launch (preserva a ativação)
npm run version:tv    # confere a versão que está instalada na TV
npm run running       # lista os apps rodando na TV
```

### Atualizar o app na TV

O webOS reaproveita o pacote instalado quando a **versão não muda** — por isso,
a cada alteração **suba a versão em `appinfo.json`** e reinstale:

```bash
npm run deploy         # package -> install -> launch (preserva a ativação)
npm run deploy:clean   # inclui uninstall (limpa os dados do app)
```

> ⚠️ `deploy:clean` apaga o `localStorage` do app — o aparelho gera um
> **novo MAC + código** e precisa ser ativado novamente. Prefira `deploy`.

> O app da TV **não** depende de `git push`: ele é instalado direto da pasta
> local pela CLI. O push serve só para versionar o código no repositório.

**Renovar a sessão:** no app Developer Mode, clique em **EXTEND** (a TV precisa
estar online). O campo *Remain Session* mostra o tempo restante.

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
