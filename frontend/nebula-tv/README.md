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
index.html       as telas do app: boot, ativação, menu, trocar lista, ao vivo,
                 catálogo, séries, episódios e player (ver "Telas")
css/tv.css       tema roxo/preto e foco para controle remoto (10-foot UI)
js/api.js        cliente do Nebula Core (registro, auth, sessão, telemetria, timeout)
js/m3u.js        parser M3U/M3U_PLUS (mesmas regras do app Android)
js/app.js        fluxo do app e navegação por controle remoto
test/            testes do parser, da busca, do cliente HTTP e da estrutura (Node)
icons/           ícones e fundo exigidos pelo pacote
```

## Desenvolvimento

```bash
# A CLI oficial do webOS (comandos ares):
npm install -g @webos-tools/cli

npm test                    # parser M3U + busca + cliente HTTP + estrutura
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
- **Enquanto você digita o foco permanece no campo** (o webOS fecha o teclado
  virtual quando o input perde o foco); **OK** fecha o texto digitado e desce
  para o primeiro resultado;
- **Como chegar ao campo**: em **Ao vivo**, com o foco na lista de canais, o `→`
  já alcança o campo. Em **Filmes** e **Séries** a grade tem 6 colunas por linha,
  então o `→` apenas anda dentro da grade — o caminho é o **`↑`** a partir da
  primeira linha, e o `↓` volta para o card de onde você saiu;
- **Navegação espacial**: as setas do controle escolhem o vizinho mais próximo
  na direção (funciona em grade, lista e colunas);
- Listas gigantes (dezenas de milhares de itens) renderizam no máximo **240**
  cards por vez, com aviso para refinar pela busca.

## Testes

```bash
npm test    # parser M3U + busca + cliente HTTP (prazo) + consistência da estrutura
```

Os testes rodam em **Node**, sem TV e sem rede. O do cliente
(`test/api.test.js`) usa um `fetch` falso simulando um servidor que aceita a
conexão e nunca responde, para provar que a requisição pendente estoura o prazo,
que o `AbortController` é acionado quando existe, e que respostas normais
(200/403/503) mantêm o tratamento anterior.

## Fluxo do app

1. **Registro**: gera uma identidade local (pseudo-MAC, como no Android — o
   webOS não expõe o MAC real) e registra no Core;
2. **Ativação**: exibe **MAC + código de 6 dígitos**; o usuário ativa no portal;
3. **Provisionamento**: recebe do Core **todas** as listas vinculadas ao aparelho
   e faz o parse da escolhida em **Trocar lista** (ou da primeira, na primeira
   execução). A escolha fica no `localStorage` e sobrevive ao boot; listas já
   baixadas saem do cache, sem novo download;
4. **Catálogo**: Ao vivo · Filmes · Séries, com categorias e navegação por
   setas do controle;
5. **Player**: `<video>` em tela cheia; **OK** pausa/retoma, **Voltar** sai;
6. **Telemetria**: envia `playback_started` / `playback_ended` ao Nebula Monitor.

### Quando o Core não responde

O boot é a única parte do app que precisa da rede para chegar ao catálogo, então
tem prazo e repetição próprios:

- **prazo por requisição:** 15 s (`REQUEST_TIMEOUT` em `js/api.js`), ajustável por
  chamada no 4º argumento. O `fetch` não tem timeout próprio: sem ele, um servidor
  que aceita a conexão e não responde (instância dormindo, portal de wifi, TCP
  meio-aberto) deixa a promessa pendente por minutos — a TV congelava em
  "Conectando…" e nem o tratamento de erro chegava a rodar;
- **repetição:** até **3 tentativas** com 2 s de intervalo, com o motivo na tela
  ("Conectando: sem resposta, tentando de novo — restam 2 tentativa(s)…"). Somado
  ao prazo, cobre ~49 s de indisponibilidade, que é a ordem de grandeza de uma
  instância do Core acordando na nuvem;
- **o que não se repete:** 401/403/404/409. Repetir não mudaria o resultado e, em
  401/403, o app ainda regeneraria a identidade (novo MAC e novo código),
  desfazendo a ativação do aparelho por causa de uma oscilação de rede;
- **saída:** esgotadas as tentativas aparecem **"Tentar novamente"** (refaz o boot
  inteiro) e o **Voltar** fecha o app. Antes disso a tela de boot não tinha nada
  focável, e nem as setas nem o Voltar faziam algo — a TV ficava presa;
- **download da lista (~80 MB):** o prazo é de **inatividade**, não de duração
  total — `DOWNLOAD_IDLE` (20 s em `js/app.js`, ajustável por
  `window.NEBULA_DOWNLOAD_IDLE`) reinicia a cada bloco recebido e cobre também a
  conexão e os cabeçalhos, então um host que aceita e nunca responde cai no mesmo
  prazo. Um teto de tempo total derrubaria download legítimo numa TV. Sem stream
  ou sem `Content-Length` não há progresso observável, e aí vale `DOWNLOAD_TOTAL`
  (5 min). Se o provedor engasgar, o download é encerrado e a tela de boot mostra
  o motivo com a saída de sempre ("Tentar novamente" / Voltar).

## Telas

Todas ficam no `index.html` como `<section class="screen">`. O app mostra uma por
vez pela classe `active` (`SCREEN_IDS` em `js/app.js`) e monta a navegação a
partir dos containers marcados com `data-nav` — o número ali é o passo do ↑/↓,
então ele tem de casar com as colunas reais do CSS.

| Tela | `id` | O que faz |
|---|---|---|
| Boot | `screen-boot` | progresso do carregamento, mensagens de repetição e o botão **"Tentar novamente"**; **Voltar** fecha o app |
| Ativação | `screen-activation` | MAC + código de 6 dígitos para ativar no portal, com **"Verificar agora"** |
| Menu | `screen-menu` | 5 botões agrupados no centro: Ao vivo · Filmes · Séries · **Trocar lista** · Recarregar lista; o topo mostra a lista em uso e o total de itens |
| Trocar lista | `screen-playlists` | as playlists vinculadas ao aparelho, com **"em uso"** na ativa; **OK** troca, **Voltar** volta ao menu |
| Ao vivo | `screen-live` | categorias ‖ lista de canais ‖ preview retangular |
| Catálogo | `screen-catalog` | grade de pôsteres (Filmes), com categorias e busca |
| Séries | `screen-series` | uma capa por série, com os episódios agrupados |
| Episódios | `screen-episodes` | episódios da série escolhida, em ordem de temporada |
| Player | `screen-player` | vídeo em tela cheia, overlay com título, dica e a **barra de progresso** dos títulos |

### Trocar lista

As opções vêm do **vínculo do aparelho**: o `GET /me/provisioning` devolve
`content_endpoints` com **todas** as playlists associadas ao Device (`name`,
`format`, `source_url` e `status`), e o app guarda a lista inteira — a primeira
versão usava só o `[0]`. A escolha é gravada no `localStorage`
(`nebula.tv.source_url`) e consultada a cada boot, então o app reabre na lista que
o usuário deixou. Como o cache do IndexedDB é indexado pela URL, alternar entre
listas já baixadas não baixa nada de novo.

> Para a troca ter o que mostrar, o aparelho precisa de **duas ou mais** listas
> vinculadas; com uma só, a tela lista um único item (o que ainda é útil, porque
> identifica a lista em uso).

## Atalhos do controle

| Tecla | Ação |
|---|---|
| ↑ ↓ ← → | navegar |
| OK (Enter) | selecionar / pausar-retomar no player |
| Voltar (461) | voltar de tela / sair do player / fechar o app na tela de boot |

## Melhorias pendentes (UX)

- **Preview no catálogo:** exibir o preview do título focado em um painel
  **retangular**, no **mesmo padrão já usado na seção de canais ao vivo** —
  *(o Ibo usa um preview circular; aqui o padrão do projeto é retangular)*.
- Ordenação ("Ordem por número") na grade.
- EPG (guia de programação) quando houver fonte XMLTV.
