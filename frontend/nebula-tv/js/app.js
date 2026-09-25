/**
 * Nebula TV — app para LG Smart TV (webOS).
 *
 * Fluxo: registra o aparelho (MAC + código) -> ativação no portal ->
 * provisionamento das listas -> catálogo (Ao vivo / Filmes / Séries) ->
 * reprodução com o pipeline de vídeo da TV.
 *
 * Navegação: setas do controle remoto + OK (Enter) + Voltar (461).
 */
(function () {
  'use strict';

  var CORE_API = window.NEBULA_CORE_API || 'https://nebula-core-6hq4.onrender.com';
  var IDENTITY_KEY = 'nebula.tv.identity';
  var PLAYLIST_KEY = 'nebula.tv.source_url';

  var KEYS = {
    LEFT: 37, UP: 38, RIGHT: 39, DOWN: 40,
    ENTER: 13, BACK: 461, ESC: 27
  };

  var api = new window.NebulaApi(CORE_API);

  var state = {
    identity: null,
    channels: [],
    categories: [],
    category: null,
    section: 'live',
    query: '',
    searchActive: false,
    catalog: [],
    focusIndex: 0,
    playerVisible: false,
    playReturn: 'screen-catalog',
    previewTimer: null,
    scrollTimer: null,
    filterTimer: null,
    searchTimer: null,
    listNode: null,
    hintTimer: null,
    seriesGroups: [],
    episodeGroup: null,
    hideTimer: null
  };

  var el = {};

  function $(id) { return document.getElementById(id); }

  var SCREEN_IDS = [
    'screen-boot', 'screen-activation', 'screen-menu', 'screen-live',
    'screen-catalog', 'screen-series', 'screen-episodes', 'screen-player'
  ];

  /**
   * Tela ativa por ID (nunca por consulta de classe: a busca por classe pode
   * casar com outro elemento e foi o que montou a navegacao com elementos de
   * TODAS as telas, deixando o foco preso em um tile invisivel do menu).
   */
  function activeScreen() {
    for (var i = 0; i < SCREEN_IDS.length; i++) {
      var element = $(SCREEN_IDS[i]);

      if (element && element.classList.contains('active')) {
        return element;
      }
    }

    return null;
  }

  function activeScreenId() {
    var screen = activeScreen();

    return screen ? screen.id : 'NENHUMA';
  }

  /**
   * Escala o palco de 1920x1080 para o viewport real da TV e centraliza.
   * Muitas LG expoem 1280x720 no runtime web — sem isso o layout vaza da tela.
   */
  function fitStage() {
    var stage = $('app');
    var width = window.innerWidth || 1920;
    var height = window.innerHeight || 1080;
    var scale = Math.min(width / 1920, height / 1080);
    var offsetX = Math.round((width - 1920 * scale) / 2);
    var offsetY = Math.round((height - 1080 * scale) / 2);

    stage.style.transform =
      'translate(' + offsetX + 'px,' + offsetY + 'px) scale(' + scale + ')';
  }

  function show(screenId) {
    // Ao trocar de tela, nenhum input deve manter o foco (as setas precisam
    // navegar) — no webOS o runtime costuma focar o primeiro campo sozinho.
    state.searchActive = false;

    if (document.activeElement && document.activeElement.tagName === 'INPUT') {
      document.activeElement.blur();
    }

    nav.nodes = [];
    nav.place = [];

    // Reconstroi no proximo frame, quando o layout da tela ja esta aplicado
    // (medir com a tela oculta retornava zero elementos focaveis).
    if (window.requestAnimationFrame) {
      window.requestAnimationFrame(rebuildNav);
    } else {
      setTimeout(rebuildNav, 0);
    }

    SCREEN_IDS.forEach(function (id) {
      $(id).classList.toggle('active', id === screenId);
    });

    console.log('[nebula] show:', screenId, '-> ativa:', activeScreenId());
  }

  /* ---------------------------------------------------------- identidade --- */

  function pseudoMac() {
    // O webOS nao expoe o MAC real: geramos um identificador estavel local
    // (mesma abordagem do app Android).
    var hex = '0123456789ABCDEF';
    var parts = [];

    for (var i = 0; i < 6; i++) {
      parts.push(hex[Math.floor(Math.random() * 16)] + hex[Math.floor(Math.random() * 16)]);
    }

    return '02:' + parts.slice(1).join(':');
  }

  function loadIdentity() {
    var raw = localStorage.getItem(IDENTITY_KEY);

    if (raw) {
      try {
        return JSON.parse(raw);
      } catch (error) {
        /* ignora */
      }
    }

    var identity = {
      fingerprint: (function () {
        var value = '';

        for (var i = 0; i < 64; i++) {
          value += '0123456789abcdef'[Math.floor(Math.random() * 16)];
        }

        return value;
      })(),
      macAddress: pseudoMac(),
      deviceId: null,
      deviceKey: null,
      activationCode: null
    };

    localStorage.setItem(IDENTITY_KEY, JSON.stringify(identity));

    return identity;
  }

  function saveIdentity() {
    localStorage.setItem(IDENTITY_KEY, JSON.stringify(state.identity));
  }

  /* --------------------------------------------------------------- boot --- */

  var BOOT_ATTEMPTS = 3;
  var RETRY_DELAY = 2000;

  /** Vale repetir a chamada? Falha de rede, prazo estourado ou 5xx. */
  function retryable(error) {
    if (!error) {
      return false;
    }

    if (error.timeout) {
      return true;                  // prazo do cliente (js/api.js)
    }

    if (!error.status) {
      return true;                  // rede, DNS, CORS, conexao que caiu
    }

    return error.status >= 500 || error.status === 429;
  }

  /**
   * Repete a tarefa enquanto o erro for de infraestrutura, avisando na tela.
   *
   * 401/403/404/409 NAO repetem: o resultado nao muda, e repetir 401/403 ainda
   * faria o resumeOrRegister regenerar a identidade (novo MAC e novo codigo) a
   * toa — trocando a ativacao do aparelho por causa de uma oscilacao de rede.
   */
  function withRetry(task, attempts, label) {
    return task().catch(function (error) {
      if (attempts <= 1 || !retryable(error)) {
        throw error;
      }

      setStatus(label + ': sem resposta, tentando de novo — restam ' +
        (attempts - 1) + ' tentativa(s)…');

      return new Promise(function (resolve) {
        setTimeout(resolve, RETRY_DELAY);
      }).then(function () {
        return withRetry(task, attempts - 1, label);
      });
    });
  }

  function boot() {
    state.identity = loadIdentity();

    // As mensagens de repeticao aparecem na tela de boot: vindo da ativacao
    // (botao 'Verificar agora') elas ficariam invisiveis.
    show('screen-boot');
    hideBootRetry();
    setStatus('Conectando…');

    withRetry(resumeOrRegister, BOOT_ATTEMPTS, 'Conectando')
      .then(function () {
        setStatus('Carregando lista…');

        return withRetry(function () {
          return api.provisioning();
        }, BOOT_ATTEMPTS, 'Carregando a lista');
      })
      .then(function (provisioning) {
        var endpoints = provisioning.content_endpoints || [];

        if (!endpoints.length) {
          return showActivation('Nenhuma lista cadastrada. Ative no portal e cadastre uma lista.');
        }

        return loadPlaylist(endpoints[0].source_url);
      })
      .catch(function (error) {
        if (error && error.message === 'DEVICE_NOT_ACTIVE') {
          return showActivation('');
        }

        // 404: aparelho ativo, porem sem lista associada. Em vez do erro cru,
        // mostra MAC + codigo para o usuario cadastrar a lista no portal.
        if (error && error.status === 404) {
          return showActivation(
            'Nenhuma lista cadastrada para este aparelho. Acesse o portal, ' +
            'informe o MAC e o código abaixo e cadastre sua lista.'
          );
        }

        // Esgotou as tentativas: diz o motivo e deixa uma saida focavel, em vez
        // de abandonar a TV numa tela sem nada para apertar.
        setStatus('Erro: ' + (error && error.message ? error.message : error) +
          ' — aperte "Tentar novamente" ou Voltar para sair.');
        showBootRetry();
      });
  }

  /**
   * Retoma o aparelho ja registrado neste dispositivo.
   *
   * O Core recusa (409) um fingerprint repetido, entao so registramos quando
   * ainda nao temos as credenciais locais. Se elas nao valerem mais (aparelho
   * removido ou resetado no admin), geramos uma identidade nova.
   */
  function resumeOrRegister() {
    var identity = state.identity;

    if (identity.deviceId && identity.deviceKey) {
      return api.authenticate(identity).catch(function (error) {
        if (error && (error.status === 401 || error.status === 403)) {
          resetIdentity();

          return registerFresh(1);
        }

        throw error;
      });
    }

    return registerFresh(1);
  }

  function registerFresh(attempt) {
    return api.registerDevice(state.identity)
      .then(function (data) {
        state.identity.deviceId = data.device_id;
        state.identity.deviceKey = data.device_key;
        state.identity.activationCode = data.activation_code;
        state.identity.macAddress = data.mac_address || state.identity.macAddress;
        saveIdentity();

        return api.authenticate(state.identity);
      })
      .catch(function (error) {
        // 409: o fingerprint ja existe, mas perdemos as credenciais locais.
        // Gera uma identidade nova (novo MAC + codigo) e registra de novo.
        if (error && error.status === 409 && attempt < 3) {
          resetIdentity();

          return registerFresh(attempt + 1);
        }

        throw error;
      });
  }

  function resetIdentity() {
    localStorage.removeItem(IDENTITY_KEY);
    localStorage.removeItem(PLAYLIST_KEY);
    state.identity = loadIdentity();
  }

  function setStatus(text) {
    $('boot-status').textContent = text;
  }

  /** Mostra a saida da tela de boot quando o servidor nao responde. */
  function showBootRetry() {
    var button = $('boot-retry');

    button.hidden = false;
    button.classList.add('focusable');
    focusFirst();
  }

  /**
   * Esconde o botao enquanto uma nova tentativa esta em curso.
   *
   * A classe 'focusable' sai junto de proposito: o rebuildNav monta a navegacao
   * so pelos '.focusable' da tela ativa, sem checar visibilidade, e um botao
   * escondido continuaria recebendo o foco das setas.
   */
  function hideBootRetry() {
    var button = $('boot-retry');

    button.hidden = true;
    button.classList.remove('focusable', 'focused');
  }

  function showActivation(message) {
    $('activation-mac').textContent = state.identity.macAddress;
    $('activation-code').textContent = state.identity.activationCode || '—';
    $('activation-status').textContent = message || 'Aguardando ativação…';
    show('screen-activation');
    focusFirst();
  }

  /* ----------------------------------------------------------- playlist --- */

  // ------------------------------------------------- cache da lista (IDB) --
  //
  // A lista do provedor tem ~80 MB: baixar e parsear a cada boot deixa a TV
  // minutos em "Carregando lista...". Guardamos o resultado em IndexedDB
  // (quota bem maior que o localStorage) e usamos na hora, atualizando em
  // segundo plano.

  var CACHE_DB = 'nebula.tv.cache';
  var CACHE_STORE = 'playlists';
  var CACHE_MAX_AGE = 12 * 60 * 60 * 1000; // 12 horas

  function openCache() {
    return new Promise(function (resolve, reject) {
      if (!window.indexedDB) {
        reject(new Error('sem indexedDB'));
        return;
      }

      var request = window.indexedDB.open(CACHE_DB, 1);

      request.onupgradeneeded = function () {
        request.result.createObjectStore(CACHE_STORE);
      };
      request.onsuccess = function () { resolve(request.result); };
      request.onerror = function () { reject(request.error); };
    });
  }

  function cacheRead(sourceUrl) {
    return openCache().then(function (db) {
      return new Promise(function (resolve) {
        var tx = db.transaction(CACHE_STORE, 'readonly');
        var get = tx.objectStore(CACHE_STORE).get(sourceUrl);

        get.onsuccess = function () { resolve(get.result || null); };
        get.onerror = function () { resolve(null); };
      });
    }).catch(function () { return null; });
  }

  function cacheWrite(sourceUrl, channels) {
    return openCache().then(function (db) {
      return new Promise(function (resolve) {
        var tx = db.transaction(CACHE_STORE, 'readwrite');

        tx.objectStore(CACHE_STORE).put({
          savedAt: Date.now(),
          channels: channels
        }, sourceUrl);

        tx.oncomplete = function () { resolve(true); };
        tx.onerror = function () { resolve(false); };
      });
    }).catch(function () { return false; });
  }

  /** Baixa (informando a % do progresso) e parseia a lista. */
  function fetchPlaylist(sourceUrl) {
    function parseText(text) {
      var channels = window.NebulaM3u.parse(text);

      if (!channels.length) {
        throw new Error('A lista está vazia ou em formato não suportado.');
      }

      cacheWrite(sourceUrl, channels);

      return channels;
    }

    return fetch(sourceUrl).then(function (response) {
      var total = Number(response.headers.get('Content-Length')) || 0;

      // Sem suporte a stream ou sem Content-Length: cai no caminho simples.
      if (!response.body || !response.body.getReader || !total) {
        setStatus('Carregando lista…');

        return response.text().then(parseText);
      }

      var reader = response.body.getReader();
      var received = 0;
      var chunks = [];
      var lastPercent = -1;

      function read() {
        return reader.read().then(function (result) {
          if (result.done) {
            var merged = new Uint8Array(received);
            var offset = 0;

            chunks.forEach(function (chunk) {
              merged.set(chunk, offset);
              offset += chunk.length;
            });

            setStatus('Processando lista…');

            return parseText(new TextDecoder('utf-8').decode(merged));
          }

          chunks.push(result.value);
          received += result.value.length;

          var percent = Math.floor((received / total) * 100);

          if (percent !== lastPercent && percent % 5 === 0) {
            lastPercent = percent;
            setStatus('Carregando lista… ' + percent + '%');
          }

          return read();
        });
      }

      setStatus('Carregando lista… 0%');

      return read();
    });
  }

  /** Usa o cache quando estiver fresco; atualiza em segundo plano. */
  function loadPlaylist(sourceUrl) {
    return cacheRead(sourceUrl).then(function (cached) {
      var fresh = cached && cached.channels && cached.channels.length &&
        (Date.now() - (cached.savedAt || 0)) < CACHE_MAX_AGE;

      if (fresh) {
        state.channels = cached.channels;
        state.categories = window.NebulaM3u.categoriesOf(state.channels);
        localStorage.setItem(PLAYLIST_KEY, sourceUrl);
        showMenu();

        // Atualiza silenciosamente para a proxima abertura.
        fetchPlaylist(sourceUrl).catch(function () { /* mantem o cache */ });

        return;
      }

      setStatus('Carregando lista…');
      show('screen-boot');

      return fetchPlaylist(sourceUrl).then(function (channels) {
        state.channels = channels;
        state.categories = window.NebulaM3u.categoriesOf(channels);
        localStorage.setItem(PLAYLIST_KEY, sourceUrl);
        showMenu();
      });
    });
  }

  function loadPlaylistLegacy(sourceUrl) {
    setStatus('Carregando lista…');
    show('screen-boot');

    return fetch(sourceUrl)
      .then(function (response) { return response.text(); })
      .then(function (text) {
        state.channels = window.NebulaM3u.parse(text);
        state.categories = window.NebulaM3u.categoriesOf(state.channels);

        if (!state.channels.length) {
          return showActivation('A lista está vazia ou em formato não suportado.');
        }

        localStorage.setItem(PLAYLIST_KEY, sourceUrl);
        showMenu();
      });
  }

  /* --------------------------------------------------------------- menu --- */

  var MENU = [
    { id: 'live', label: 'Ao vivo' },
    { id: 'movie', label: 'Filmes' },
    { id: 'series', label: 'Séries' },
    { id: 'reload', label: 'Recarregar lista' }
  ];

  function showMenu() {
    var grid = $('menu-grid');

    grid.innerHTML = '';
    $('menu-list-name').textContent = state.channels.length + ' itens na lista';

    MENU.forEach(function (item, index) {
      var tile = document.createElement('div');

      tile.className = 'tile focusable';
      tile.textContent = item.label;
      tile.dataset.index = index;
      grid.appendChild(tile);
    });

    show('screen-menu');
    state.focus = { column: 0, index: 0 };
    focusFirst();
  }

  /* ------------------------------------------------------------- ao vivo --- */

  var PREVIEW_DELAY = 900;

  function openLive() {
    state.section = 'live';
    state.catalog = state.channels.filter(function (item) {
      return item.kind === 'live';
    });
    state.category = null;
    state.query = '';

    var search = $('live-search');

    if (search) {
      search.value = '';
    }

    renderLiveCategories();
    renderLiveChannels();
    rebuildNav();
    show('screen-live');
    focusFirst();

    var first = liveItems()[0];

    if (first) {
      updatePreview(first, 300);
    }
  }

  function liveItems() {
    var items = state.category
      ? state.catalog.filter(function (item) { return item.group === state.category; })
      : state.catalog;

    if (state.query) {
      items = items.filter(function (item) {
        return window.NebulaSearch.matches(item.name, state.query);
      });
    }

    return items;
  }

  function renderLiveCategories() {
    var container = $('live-categories');
    var groups = window.NebulaM3u.categoriesOf(state.catalog);

    container.innerHTML = '';

    var entries = [{ name: null, label: 'Todos (' + state.catalog.length + ')' }];

    groups.forEach(function (group) {
      var total = state.catalog.filter(function (item) {
        return item.group === group;
      }).length;

      entries.push({ name: group, label: group + ' (' + total + ')' });
    });

    entries.forEach(function (entry) {
      var node = document.createElement('div');

      node.className = 'category focusable';
      node.textContent = entry.label;
      node.dataset.group = entry.name || '';
      container.appendChild(node);
    });
  }

  function renderLiveChannels() {
    var container = $('live-channels');
    var items = liveItems();
    var limit = Math.min(items.length, MAX_RENDER);

    container.innerHTML = '';

    var liveLabel = state.category ? state.category + ' · ' : '';

    $('live-count').textContent = liveLabel + items.length + ' canais';

    for (var i = 0; i < limit; i++) {
      container.appendChild(buildChannelRow(items[i], i + 1));
    }

    if (items.length > limit) {
      var hint = document.createElement('div');

      hint.className = 'limit-hint';
      hint.textContent = 'Mostrando ' + limit + ' de ' + items.length +
        ' — use a busca para refinar.';
      container.appendChild(hint);
    }

    if (!items.length) {
      var empty = document.createElement('div');

      empty.className = 'limit-hint';
      empty.textContent = 'Nenhum canal encontrado.';
      container.appendChild(empty);
    }

    state.focus = { column: 0, index: 0 };
  }

  function buildChannelRow(channel, position) {
    var row = document.createElement('div');
    var number = document.createElement('span');
    var name = document.createElement('span');

    row.className = 'channel focusable';
    row.dataset.url = channel.url || '';
    row.dataset.title = channel.name || '';
    row.dataset.group = channel.group || '';

    number.className = 'channel-num';
    number.textContent = String(position);

    row.appendChild(number);

    var logo = buildLogo(channel.logo, 'channel-logo', function () {
      var empty = logoPlaceholder(channel);

      if (logo && logo.parentNode) {
        logo.parentNode.replaceChild(empty, logo);
      }
    });

    row.appendChild(logo || logoPlaceholder(channel));

    name.className = 'channel-name';
    name.textContent = channel.name || 'Sem nome';
    row.appendChild(name);

    return row;
  }

  function logoPlaceholder(channel) {
    var box = document.createElement('div');

    box.className = 'channel-logo-empty';
    box.textContent = channel.name ? channel.name.charAt(0).toUpperCase() : 'N';

    return box;
  }

  /** Atualiza o preview (video mudo) do canal em foco, com debounce. */
  function updatePreview(channel, delay) {
    var video = $('preview-video');

    $('preview-title').textContent = channel.name || '';
    $('preview-group').textContent = channel.group || '';

    if (!channel.url) {
      return;
    }

    if (video.dataset.url === channel.url) {
      return;
    }

    clearTimeout(state.previewTimer);
    state.previewTimer = setTimeout(function () {
      video.dataset.url = channel.url;
      video.src = channel.url;
      video.play().catch(function () { /* o usuario decide no OK */ });
    }, delay === undefined ? PREVIEW_DELAY : delay);
  }

  /* ------------------------------------------------------------ catalogo --- */

  function openCatalog(kind) {
    state.section = kind;
    state.catalog = state.channels.filter(function (channel) { return channel.kind === kind; });
    state.category = null;
    state.query = '';

    var search = $('catalog-search');

    if (search) {
      search.value = '';
    }

    $('catalog-title').textContent =
      kind === 'live' ? 'Ao vivo' : (kind === 'movie' ? 'Filmes' : 'Séries');

    renderCategories();
    renderItems();
    rebuildNav();
    show('screen-catalog');
    focusFirst();
  }

  function renderCategories() {
    var container = $('catalog-categories');
    var groups = window.NebulaM3u.categoriesOf(state.catalog);

    container.innerHTML = '';

    var entries = [{ name: null, label: 'Todas (' + state.catalog.length + ')' }];

    groups.forEach(function (group) {
      var total = state.catalog.filter(function (item) { return item.group === group; }).length;

      entries.push({ name: group, label: group + ' (' + total + ')' });
    });

    entries.forEach(function (entry) {
      var node = document.createElement('div');

      node.className = 'category focusable';
      node.textContent = entry.label;
      node.dataset.group = entry.name || '';
      container.appendChild(node);
    });
  }

  /** Itens do catalogo apos o filtro de categoria e o termo de busca. */
  function filteredItems() {
    var items = state.category
      ? state.catalog.filter(function (channel) { return channel.group === state.category; })
      : state.catalog;

    if (state.query) {
      items = items.filter(function (channel) {
        return window.NebulaSearch.matches(channel.name, state.query);
      });
    }

    return items;
  }

  var MAX_RENDER = 240;

  /** Card da grade: capa (com fallback) + titulo + categoria. */
  function buildCard(channel) {
    var card = document.createElement('div');
    var media = document.createElement('div');
    var title = document.createElement('div');

    card.className = 'poster focusable';
    card.dataset.url = channel.url || '';
    card.dataset.title = channel.name || '';

    media.className = 'poster-media';

    var poster = buildLogo(channel.logo, '', function () {
      // Capa indisponivel: mantem o card legivel.
      media.innerHTML = '';
      media.appendChild(fallbackLabel(channel));
    });

    if (poster) {
      media.appendChild(poster);
    } else {
      media.appendChild(fallbackLabel(channel));
    }

    title.className = 'poster-title';
    title.textContent = channel.name || 'Sem nome';

    card.appendChild(media);
    card.appendChild(title);

    if (state.section !== 'live' && channel.group) {
      var badge = document.createElement('div');

      badge.className = 'poster-badge';
      badge.textContent = channel.group;
      card.appendChild(badge);
    }

    return card;
  }

  function fallbackLabel(channel) {
    var label = document.createElement('span');

    label.className = 'poster-fallback';
    label.textContent = channel.name ? channel.name.charAt(0).toUpperCase() : 'N';

    return label;
  }

  function renderItems() {
    var startedAt = Date.now();
    var container = $('catalog-items');
    var items = filteredItems();
    var limit = Math.min(items.length, MAX_RENDER);

    container.innerHTML = '';

    var catalogLabel = state.category ? state.category + ' · ' : '';

    $('catalog-count').textContent = state.query
      ? catalogLabel + items.length + ' resultado(s)'
      : catalogLabel + items.length + ' itens';

    for (var i = 0; i < limit; i++) {
      container.appendChild(buildCard(items[i]));
    }

    if (items.length > limit) {
      var hint = document.createElement('div');

      hint.className = 'limit-hint';
      hint.textContent = 'Mostrando ' + limit + ' de ' + items.length +
        ' — use a busca para refinar.';
      container.appendChild(hint);
    }

    if (!items.length) {
      var empty = document.createElement('div');

      empty.className = 'limit-hint';
      empty.textContent = 'Nenhum título encontrado.';
      container.appendChild(empty);
    }

    console.log('[nebula] renderItems: ' + (container.children.length - 1) +
      ' cards em ' + (Date.now() - startedAt) + 'ms');

    state.focus = { column: 0, index: 0 };
  }

  /**
   * Aplica a busca de uma tela: re-renderiza a lista e MANTEM o foco no campo.
   *
   * O comportamento anterior movia o foco para o primeiro resultado a cada
   * tecla (via debounce). Como o webOS fecha o teclado virtual quando o input
   * perde o foco — e o `setFocus` desfoca todo input que nao seja o no focado —
   * digitar exigia re-selecionar o campo a cada letra digitada ou apagada.
   */
  function applySearch(input, render) {
    state.query = input.value.trim();
    render();

    // O render trocou os cards: reconstroi o nav para apontar para os nos
    // novos. Enquanto o usuario digita, o proprio campo continua sendo o no
    // focado (setFocus reaplica o '.focused' e o focus() sem perder o cursor).
    refreshNav(document.activeElement === input ? input : null);
  }

  /**
   * Campo de busca, lista de conteudo e render de cada tela.
   *
   * O campo fica no topbar, FORA de qualquer container [data-nav], entao o
   * rebuildNav o coloca numa coluna "extras" no FIM da navegacao. Numa lista
   * (cols=1) o 'right' troca de coluna e chega nele; numa grade (cols=6, como
   * Filmes e Series) o 'right' nunca sai da coluna, e o campo so e alcancavel
   * pela ponte vertical do moveFocus (seta para cima na primeira linha).
   */
  var SCREEN_CONTENT = {
    'screen-live': { search: 'live-search', list: 'live-channels', render: renderLiveChannels },
    'screen-catalog': { search: 'catalog-search', list: 'catalog-items', render: renderItems },
    'screen-series': { search: 'series-search', list: 'series-items', render: renderSeries }
  };

  /** Configuracao da tela ativa (null nas telas sem busca, como o menu). */
  function screenContent() {
    var screen = activeScreen();

    return screen ? SCREEN_CONTENT[screen.id] || null : null;
  }

  /** Campo de busca da tela ativa. */
  function searchNodeOf() {
    var map = screenContent();

    return map ? $(map.search) : null;
  }

  /** Lista de conteudo (grade ou lista) da tela ativa. */
  function contentListOf() {
    var map = screenContent();

    return map ? $(map.list) : null;
  }

  /** Primeiro item da lista de conteudo da tela ativa (destino do OK na busca). */
  function firstContentNode() {
    var container = contentListOf();

    return container ? container.querySelector('.focusable') : null;
  }

  /** O no pertence a lista de conteudo da tela ativa? */
  function isInContentList(node) {
    var container = contentListOf();

    return Boolean(node && container && container.contains(node));
  }

  /** Fecha o texto do campo ativo na lista e cancela o debounce pendente. */
  function commitSearch() {
    var input = document.activeElement;
    var map = screenContent();

    if (!map || !input || input.id !== map.search) {
      return;
    }

    clearTimeout(state.searchTimer);
    state.searchTimer = null;
    applySearch(input, map.render);
  }

  /* -------------------------------------------------------------- series --- */

  var MAX_SERIES = 300;

  /** Agrupa os episodios em uma entrada por serie (como o IBO). */
  function groupSeries(items) {
    var groups = {};
    var order = [];

    items.forEach(function (episode) {
      var name = window.NebulaM3u.seriesNameOf(episode.name) || episode.name;
      var key = window.NebulaSearch.normalize(name);
      var group = groups[key];

      if (!group) {
        group = {
          name: name,
          poster: '',
          category: episode.group || '',
          episodes: []
        };
        groups[key] = group;
        order.push(group);
      }

      if (!group.poster && episode.logo) {
        group.poster = episode.logo;
      }

      group.episodes.push(episode);
    });

    order.forEach(function (group) {
      group.episodes.sort(function (a, b) {
        return window.NebulaM3u.episodeOrder(
          window.NebulaM3u.seasonEpisodeOf(a.name)
        ) - window.NebulaM3u.episodeOrder(
          window.NebulaM3u.seasonEpisodeOf(b.name)
        );
      });
    });

    return order;
  }

  function openSeries() {
    state.section = 'series';
    state.catalog = state.channels.filter(function (item) {
      return item.kind === 'series';
    });
    state.seriesGroups = groupSeries(state.catalog);
    state.category = null;
    state.query = '';
    state.episodeGroup = null;

    var search = $('series-search');

    if (search) {
      search.value = '';
    }

    renderSeriesCategories();
    renderSeries();
    rebuildNav();
    show('screen-series');
    focusFirst();
  }

  function seriesItems() {
    var groups = state.seriesGroups;

    if (state.category) {
      groups = groups.filter(function (group) {
        return group.category === state.category;
      });
    }

    if (state.query) {
      groups = groups.filter(function (group) {
        return window.NebulaSearch.matches(group.name, state.query);
      });
    }

    return groups;
  }

  function renderSeriesCategories() {
    var container = $('series-categories');
    var seen = {};
    var categories = [];

    state.seriesGroups.forEach(function (group) {
      if (group.category && !seen[group.category]) {
        seen[group.category] = 0;
      }

      if (group.category) {
        seen[group.category] += 1;
      }
    });

    Object.keys(seen).sort(function (a, b) {
      return a.localeCompare(b);
    }).forEach(function (name) {
      categories.push({ name: name, total: seen[name] });
    });

    container.innerHTML = '';

    [{ name: null, label: 'Todas (' + state.seriesGroups.length + ')' }]
      .concat(categories.map(function (entry) {
        return { name: entry.name, label: entry.name + ' (' + entry.total + ')' };
      }))
      .forEach(function (entry) {
        var node = document.createElement('div');

        node.className = 'category focusable';
        node.textContent = entry.label;
        node.dataset.group = entry.name || '';
        container.appendChild(node);
      });
  }

  function renderSeries() {
    var startedAt = Date.now();
    var container = $('series-items');
    var groups = seriesItems();
    var limit = Math.min(groups.length, MAX_SERIES);

    container.innerHTML = '';

    var seriesLabel = state.category ? state.category + ' · ' : '';

    $('series-count').textContent = seriesLabel + groups.length + ' séries';

    for (var i = 0; i < limit; i++) {
      container.appendChild(buildSeriesCard(groups[i]));
    }

    if (!groups.length) {
      var empty = document.createElement('div');

      empty.className = 'limit-hint';
      empty.textContent = 'Nenhuma série encontrada.';
      container.appendChild(empty);
    }

    console.log('[nebula] renderSeries: ' + (container.children.length - 1) +
      ' cards em ' + (Date.now() - startedAt) + 'ms');
  }

  function buildSeriesCard(group) {
    var card = document.createElement('div');
    var media = document.createElement('div');
    var title = document.createElement('div');
    var sub = document.createElement('div');

    card.className = 'poster focusable';
    card.dataset.group = window.NebulaSearch.normalize(group.name);

    media.className = 'poster-media';

    var poster = buildLogo(group.poster, '', function () {
      media.innerHTML = '';
      media.appendChild(fallbackLabel({ name: group.name }));
    });

    if (poster) {
      media.appendChild(poster);
    } else {
      media.appendChild(fallbackLabel({ name: group.name }));
    }

    title.className = 'poster-title';
    title.textContent = group.name;

    sub.className = 'poster-sub';
    sub.textContent = group.episodes.length === 1
      ? '1 episódio'
      : group.episodes.length + ' episódios';

    card.appendChild(media);
    card.appendChild(title);
    card.appendChild(sub);

    return card;
  }

  /** Lista os episódios da serie selecionada. */
  function openEpisodes(group) {
    state.episodeGroup = group;

    $('episodes-title').textContent = group.name;
    $('episodes-count').textContent = group.episodes.length + ' episódios';

    renderEpisodes();
    rebuildNav();
    show('screen-episodes');
    focusFirst();
  }

  function renderEpisodes() {
    var container = $('episode-list');
    var group = state.episodeGroup;

    container.innerHTML = '';

    if (!group) return;

    group.episodes.forEach(function (episode, index) {
      var row = document.createElement('div');
      var number = document.createElement('span');
      var name = document.createElement('span');
      var label = document.createElement('span');

      row.className = 'channel focusable';
      row.dataset.url = episode.url || '';
      row.dataset.title = episode.name || '';

      number.className = 'channel-num';
      number.textContent = String(index + 1);

      name.className = 'channel-name';
      name.textContent = window.NebulaM3u.seriesNameOf(episode.name) || episode.name;

      label.className = 'episode-label';
      label.textContent = window.NebulaM3u.seasonEpisodeOf(episode.name);

      row.appendChild(number);
      row.appendChild(name);
      row.appendChild(label);
      container.appendChild(row);
    });
  }

  /* -------------------------------------------------------------- player --- */

  /** Texto legivel do erro de video (aparece na tela e no console). */
  function videoErrorText() {
    var error = $('video').error;

    if (!error) return 'sem detalhe';

    var codes = {
      1: 'ABORTED (cancelado)',
      2: 'NETWORK (rede/CORS)',
      3: 'DECODE (codec)',
      4: 'SRC_NOT_SUPPORTED (formato nao suportado)'
    };

    return (codes[error.code] || ('codigo ' + error.code)) +
      (error.message ? ' · ' + error.message : '');
  }

  /** Liga os avisos do elemento de video (uma vez). */
  function watchVideoEvents() {
    var video = $('video');

    if (video.dataset.watched) return;

    video.dataset.watched = '1';

    video.addEventListener('error', function () {
      var detail = videoErrorText();

      $('player-hint').textContent = 'ERRO: ' + detail;
      showKeyHint('ERRO VIDEO: ' + detail);
      console.log('[nebula] erro de video:', detail, video.currentSrc || video.src);
    });

    video.addEventListener('stalled', function () {
      $('player-hint').textContent = 'Carregando (conexão lenta)…';
    });

    video.addEventListener('waiting', function () {
      $('player-hint').textContent = 'Carregando…';
    });

    video.addEventListener('playing', function () {
      $('player-hint').textContent = 'OK: pausar · Voltar: sair';
      showKeyHint('▶ reproduzindo');
      console.log('[nebula] reproduzindo:', video.currentSrc || video.src);
    });
  }

  function play(url, title) {
    var video = $('video');

    // IMPORTANTE: gravar a origem ANTES de trocar de tela (senao gravariamos
    // 'screen-player' e o Voltar cairia numa tela preta).
    var active = activeScreen();

    state.playReturn = active && active.id !== 'screen-player'
      ? active.id
      : 'screen-catalog';

    pausePreview();

    watchVideoEvents();
    $('player-title').textContent = title;
    $('player-hint').textContent = 'Conectando ao canal…';
    video.src = url;
    video.play().catch(function () { /* o usuario aperta OK */ });

    show('screen-player');
    state.playerVisible = true;
    api.telemetry('playback_started', { title: title, url: url, live: state.section === 'live' })
      .catch(function () { /* melhor esforço */ });
    scheduleOverlayHide();
  }

  /** Pausa o video de preview (ao sair do Ao vivo). */
  function pausePreview() {
    var video = $('preview-video');

    if (!video) return;

    clearTimeout(state.previewTimer);
    video.pause();
    video.removeAttribute('src');
    video.dataset.url = '';
    video.load();
  }

  function stopPlayer() {
    var video = $('video');

    video.pause();
    video.removeAttribute('src');
    video.load();
    state.playerVisible = false;

    api.telemetry('playback_ended', { title: $('player-title').textContent })
      .catch(function () { /* melhor esforço */ });

    show(state.playReturn || 'screen-catalog');
    focusFirst();
  }

  function scheduleOverlayHide() {
    var overlay = $('player-overlay');

    overlay.classList.remove('hidden');
    clearTimeout(state.hideTimer);
    state.hideTimer = setTimeout(function () { overlay.classList.add('hidden'); }, 4000);
  }

  /* -------------------------------------------------- foco (controle remoto) --- */

  // --------------------------------------------------------- navegacao ------
  //
  // Modelo DETERMINISTICO de colunas (padrao de TV): nada de geometria.
  // Cada container marcado com data-nav="N" e uma coluna com N itens por
  // linha (grade) ou 1 (lista). Isso torna a navegacao previsivel e rapida
  // na CPU da TV.

  var nav = { columns: [], nodes: [], place: [], col: 0, row: 0 };

  // Muitos logos de listas IPTV apontam para dominios mortos: sem este cache o
  // navegador refaz a resolucao DNS (e falha) a cada re-render, travando a TV.
  var failedImages = {};

  /**
   * Cria a imagem da capa com carregamento sob demanda.
   * URLs que ja falharam nao sao tentadas de novo.
   */
  function buildLogo(url, className, onFail) {
    if (!url || failedImages[url]) {
      return null;
    }

    var image = document.createElement('img');

    image.className = className || '';
    image.alt = '';
    image.loading = 'lazy';
    image.decoding = 'async';
    image.src = url;
    image.addEventListener('error', function () {
      failedImages[url] = true;

      if (onFail) {
        onFail();
      }
    });

    return image;
  }

  /** Reconstroi as colunas a partir do DOM da tela ativa (em cache). */
  function rebuildNav() {
    var screen = activeScreen();

    nav.columns = [];
    nav.nodes = [];
    nav.place = [];

    if (!screen) return;

    var columns = screen.querySelectorAll('[data-nav]');

    Array.prototype.slice.call(columns).forEach(function (container) {
      var cols = Number(container.getAttribute('data-nav')) || 1;
      // Sem offsetParent: a leitura forca layout em centenas de elementos.
      // Como a busca ja esta limitada a tela ATIVA, todos sao visiveis.
      var items = Array.prototype.slice
        .call(container.querySelectorAll('.focusable'));

      if (!items.length) return;

      var columnIndex = nav.columns.length;

      nav.columns.push({ nodes: items, cols: cols });

      items.forEach(function (node, row) {
        nav.place.push({ col: columnIndex, row: row });
        nav.nodes.push(node);
      });
    });

    // Elementos focaveis fora de qualquer coluna (ex.: campo de busca).
    var extras = Array.prototype.slice
      .call(screen.querySelectorAll('.focusable'))
      .filter(function (node) {
        return nav.nodes.indexOf(node) === -1;
      });

    if (extras.length) {
      var extraIndex = nav.columns.length;

      nav.columns.push({ nodes: extras, cols: 1 });

      extras.forEach(function (node, row) {
        nav.place.push({ col: extraIndex, row: row });
        nav.nodes.push(node);
      });
    }

    if (nav.col >= nav.columns.length) {
      nav.col = 0;
      nav.row = 0;
    }

    console.log('[nebula] tela=' + activeScreenId() + ' · ' + nav.columns.length +
      ' colunas · ' + nav.nodes.length + ' itens');

    setTimeout(ensureFocus, 0);
  }

  /**
   * Garante a invariante do foco: SEMPRE existe exatamente um elemento com
   * '.focused' quando ha itens navegaveis. Sem isso o app fica em "SEM FOCO"
   * (as setas nao movem nada) apos um re-render ou troca de tela.
   */
  function ensureFocus() {
    if (document.querySelector('.focusable.focused')) {
      return;
    }

    if (!nav.nodes.length) {
      rebuildNav();
    }

    if (nav.nodes.length) {
      nav.col = 0;
      nav.row = 0;
      setFocus(nav.nodes[0]);
    }
  }

  /**
   * Reconstroi a navegacao DEPOIS de um re-render e mantem o foco onde estava.
   *
   * Todo render recria os cards (innerHTML = ''), mas o `nav` continuava
   * apontando para os nos ANTIGOS ja desanexados: a seta movia o foco para um
   * elemento fora do documento (nada se destacava, o container rolava para o
   * topo) e o OK seguinte tocava o item antigo. O `ensureFocus` nao resolvia
   * porque ele so age quando NAO existe '.focused' no documento.
   */
  function refreshNav(keepNode) {
    rebuildNav();

    var node = keepNode || document.querySelector('.focusable.focused');
    var screen = activeScreen();

    // O no preservado sobreviveu ao render (ex.: a categoria): reindexa a
    // posicao nele com as colunas novas, para que a grade aponte para os
    // cards recem-criados.
    if (node && screen && screen.contains(node)) {
      setFocus(node);
      return;
    }

    ensureFocus();
  }

  function focusableNodes() {
    if (!nav.nodes.length) {
      rebuildNav();
    }

    return nav.nodes;
  }

  function nodeAt(col, row) {
    var column = nav.columns[col];

    if (!column) return null;

    var index = Math.min(Math.max(row, 0), column.nodes.length - 1);

    return column.nodes[index];
  }

  function moveFocus(direction) {
    if (!nav.columns.length) {
      rebuildNav();
    }

    if (!nav.columns.length) return;

    var column = nav.columns[nav.col];

    if (direction === 'up' || direction === 'down') {
      var current = nodeAt(nav.col, nav.row);
      var search = searchNodeOf();

      // O campo de busca fica na barra ACIMA da lista: descer dele volta para
      // a lista, na posicao exata de onde o usuario saiu.
      if (current && search && current === search) {
        if (direction === 'down') {
          var back = state.listNode;

          setFocus(isInContentList(back) ? back : firstContentNode());
        }

        return;
      }

      var step = direction === 'up' ? -1 : 1;
      var distance = column.cols > 1 ? column.cols : 1;
      var target = nav.row + step * distance;

      if (target >= 0 && target < column.nodes.length) {
        nav.row = target;
        setFocus(nodeAt(nav.col, nav.row));
        return;
      }

      // Ponte com o campo de busca: subir da PRIMEIRA linha da lista leva ao
      // campo. Sem ela a grade de Filmes/Series prendia o foco (numa grade o
      // 'right' nao troca de coluna) e o campo era inalcancavel pelas setas.
      if (direction === 'up' && search && isInContentList(current)) {
        state.listNode = current;
        setFocus(search);
        return;
      }

      // Lista: se sair dos limites, sobe/desce uma linha mesmo assim.
      if (column.cols === 1) {
        nav.row = target < 0 ? 0 : column.nodes.length - 1;
        setFocus(nodeAt(nav.col, nav.row));
      }

      return;
    }

    // left / right
    var delta = direction === 'right' ? 1 : -1;

    if (column.cols > 1) {
      var next = nav.row + delta;

      if (next >= 0 && next < column.nodes.length) {
        nav.row = next;
        setFocus(nodeAt(nav.col, nav.row));
        return;
      }
    }

    // Muda de coluna (mantendo a posicao relativa).
    var targetCol = nav.col + delta;

    if (targetCol < 0 || targetCol >= nav.columns.length) {
      return;
    }

    nav.col = targetCol;
    nav.row = Math.min(nav.row, nav.columns[targetCol].nodes.length - 1);
    setFocus(nodeAt(nav.col, nav.row));
  }

  /** Foco com rolagem sob medida (scrollIntoView e caro na TV). */
  function setFocus(node) {
    if (!node) return;

    if (nav.nodes.indexOf(node) === -1) {
      rebuildNav();
    }

    var place = nav.place[nav.nodes.indexOf(node)];

    if (place) {
      nav.col = place.col;
      nav.row = place.row;
    }

    // Limpa a classe em TODO o documento: um elemento que saiu da navegacao
    // (ex.: tile do menu apos trocar de tela) mantinha '.focused' e o
    // activateFocused acabava ativando ele, nao o item visivel.
    var previous = document.querySelectorAll('.focusable.focused');

    for (var i = 0; i < previous.length; i++) {
      if (previous[i] !== node) {
        previous[i].classList.remove('focused');
      }
    }

    nav.nodes.forEach(function (item) {
      if (item !== node) {
        item.classList.toggle('focused', false);
      }

      if (item.tagName === 'INPUT' && item !== node) {
        item.blur();
      }
    });

    node.classList.add('focused');

    if (node.tagName === 'INPUT') {
      node.focus();
    }

    scrollIntoViewIfNeeded(node);

    if (node.classList.contains('channel')) {
      updatePreview({
        name: node.dataset.title,
        group: node.dataset.group,
        url: node.dataset.url
      });
    }

    if (node.classList.contains('category')) {
      syncCategoryFocus(node);
    }
  }

  /**
   * Padrao do IBO: mover o cursor na coluna de categorias filtra a grade na
   * hora, sem precisar apertar OK. O cursor permanece na categoria.
   */
  function syncCategoryFocus(node) {
    var group = node.dataset.group || null;

    if (state.category === group) {
      return;
    }

    state.category = group;

    // Re-renderiza com um pequeno atraso: percorrer varias categorias com a
    // seta nao deve reconstruir 240 cards a cada passo.
    clearTimeout(state.filterTimer);
    state.filterTimer = setTimeout(function () {
      var active = activeScreen();

      if (!active) return;

      if (active.id === 'screen-live') {
        renderLiveChannels();
      } else if (active.id === 'screen-series') {
        renderSeries();
      } else if (active.id === 'screen-catalog') {
        renderItems();
      }
      // Depois do re-render o `nav` precisa apontar para os cards NOVOS; a
      // categoria continua sendo o no focado.
      refreshNav(node);
    }, 160);

    rebuildNav();
    ensureFocus();
    setFocus(node);
  }

  /** Rola apenas o container necessario, e somente se preciso. */
  function scrollIntoViewIfNeeded(node) {
    var scroller = node.parentNode;

    while (scroller && scroller !== document) {
      var style = window.getComputedStyle(scroller);

      if (style.overflowY === 'auto' || style.overflowY === 'scroll') {
        break;
      }

      scroller = scroller.parentNode;
    }

    if (!scroller || scroller === document) {
      scroller = null;
    }

    if (!scroller) {
      node.scrollIntoView({ block: 'nearest' });
      return;
    }

    var nodeRect = node.getBoundingClientRect();
    var boxRect = scroller.getBoundingClientRect();

    if (nodeRect.top < boxRect.top) {
      scroller.scrollTop -= boxRect.top - nodeRect.top + 12;
    } else if (nodeRect.bottom > boxRect.bottom) {
      scroller.scrollTop += nodeRect.bottom - boxRect.bottom + 12;
    }
  }

  function focusFirst() {
    rebuildNav();

    if (!nav.nodes.length) return;

    nav.col = 0;
    nav.row = 0;
    setFocus(nodeAt(0, 0));
  }

  function activateFocused() {
    // Fonte da verdade: a POSICAO na navegacao (nao uma consulta no documento,
    // que podia retornar um elemento invisivel de outra tela).
    var column = nav.columns[nav.col];
    var node = column ? column.nodes[nav.row] : null;

    if (!node) {
      node = document.querySelector('.focusable.focused');
    }

    if (!node) return;

    // 'Verificar agora' (ativacao) e 'Tentar novamente' (boot sem resposta)
    // refazem o boot inteiro.
    if (node.id === 'activation-check' || node.id === 'boot-retry') {
      boot();
      return;
    }

    showKeyHint('ATIVAR: ' + node.className +
      ' | ' + String(node.dataset.title || node.textContent || '')
        .trim().slice(0, 22) +
      (node.dataset.url ? ' | URL ok' : ' | SEM URL'));

    if (node.classList.contains('tile')) {
      var item = MENU[Number(node.dataset.index)];

      if (item.id === 'reload') {
        location.reload();
        return;
      }

      if (item.id === 'live') {
        openLive();
        return;
      }

      if (item.id === 'series') {
        openSeries();
        return;
      }

      openCatalog(item.id);
      return;
    }

    if (node.classList.contains('category')) {
      state.category = node.dataset.group || null;

      var active = activeScreen();

      if (active && active.id === 'screen-live') {
        renderLiveChannels();
      } else if (active && active.id === 'screen-series') {
        renderSeries();
      } else {
        renderItems();
      }

      // Sem isto a grade ficava apontando para os cards antigos e a seta
      // seguinte nao movia o destaque (o no focado saia do documento).
      refreshNav(node);

      return;
    }

    if (node.classList.contains('poster') && document.querySelector('#screen-series.active')) {
      var wanted = node.dataset.group;

      for (var i = 0; i < state.seriesGroups.length; i++) {
        if (window.NebulaSearch.normalize(state.seriesGroups[i].name) === wanted) {
          openEpisodes(state.seriesGroups[i]);
          return;
        }
      }

      return;
    }

    if (node.classList.contains('channel')) {
      play(node.dataset.url, node.dataset.title || '');
      return;
    }

    console.log('[nebula] ativar:', node.className, node.dataset.url || '');

    if (node.classList.contains('poster')) {
      if (node.dataset.url) {
        play(node.dataset.url, node.dataset.title || '');
      }
    }
  }

  /* ------------------------------------------------------------- eventos --- */

  /** Elemento focavel sob o ponteiro (Magic Remote, mouse ou DevTools). */
  function focusableFrom(target) {
    var node = target;

    while (node && node !== document) {
      if (node.classList && node.classList.contains('focusable')) {
        return node;
      }

      node = node.parentNode;
    }

    return null;
  }

  // O "Magic Remote" envia eventos de mouse, mas o webOS tambem dispara um
  // ponteiro FANTASMA (parado, muitas vezes no canto superior esquerdo =
  // sobre a categoria "Todos"). Sem filtrar isso, cada tecla do controle
  // movia o foco para onde o ponteiro estivesse e a categoria era resetada.
  var pointer = { x: null, y: null, active: false, mutedUntil: 0 };

  document.addEventListener('mousemove', function (event) {
    if (pointer.x === null) {
      // Primeiro evento: apenas guarda a posicao de referencia.
      pointer.x = event.clientX;
      pointer.y = event.clientY;
      return;
    }

    var moved = Math.abs(event.clientX - pointer.x) >= 4 ||
      Math.abs(event.clientY - pointer.y) >= 4;

    pointer.x = event.clientX;
    pointer.y = event.clientY;

    if (!moved) {
      return;
    }

    // Logo apos uma tecla do controle, o webOS costuma emitir um movimento
    // fantasma: ignoramos para nao roubar o foco de quem esta navegando.
    if (Date.now() < pointer.mutedUntil) {
      return;
    }

    // So a partir do primeiro movimento real consideramos o ponteiro ativo.
    pointer.active = true;

    var node = focusableFrom(event.target);

    if (node && !node.classList.contains('focused')) {
      setFocus(node);
    }
  });

  document.addEventListener('click', function (event) {
    // ATENCAO: o OK do Magic Remote chega como CLIQUE na posicao do ponteiro.
    // Se ativassemos o elemento sob o ponteiro, apertar OK com o ponteiro
    // parado sobre uma categoria (ex.: "Todos") ativaria a categoria errada.
    // Portanto o clique apenas MOVE O FOCO; a ativacao e sempre pela tecla OK.
    event.preventDefault();

    if (!pointer.active) {
      return;
    }

    var node = focusableFrom(event.target);

    if (node) {
      setFocus(node);
    }
  });

  // Evita o menu de contexto do botao direito no controle.
  document.addEventListener('contextmenu', function (event) {
    event.preventDefault();
  });

  /** Mostra a ultima tecla por 1,4s (diagnostico visivel na TV). */
  function showKeyHint(text) {
    var hint = $('key-hint');

    if (!hint) return;

    hint.textContent = text;
    hint.classList.add('visible');
    clearTimeout(state.hintTimer);
    state.hintTimer = setTimeout(function () {
      hint.classList.remove('visible');
    }, 1400);
  }

  /** Converte event.key (norma moderna) em keyCode, como fallback. */
  function keyCodeFromName(name) {
    var map = {
      ArrowLeft: KEYS.LEFT, ArrowUp: KEYS.UP,
      ArrowRight: KEYS.RIGHT, ArrowDown: KEYS.DOWN,
      Enter: KEYS.ENTER, Escape: KEYS.ESC, Backspace: KEYS.BACK,
      GoBack: KEYS.BACK
    };

    return map[name] || 0;
  }

  document.addEventListener('keydown', function (event) {
    var code = event.keyCode || event.which || keyCodeFromName(event.key);

    // Silencia o ponteiro por 600ms apos qualquer tecla do controle.
    pointer.mutedUntil = Date.now() + 600;

    // Auto-correcao: se o estado de busca ficou "preso" (sem nenhum input
    // realmente focado), as setas voltam a navegar.
    if (state.searchActive) {
      var active = document.activeElement;

      if (!active || active.tagName !== 'INPUT') {
        state.searchActive = false;
      }
    }

    var focused = document.querySelector('.focusable.focused');
    var what = focused
      ? '[' + nav.col + ',' + nav.row + '] ' + focused.className +
        ' "' + String(focused.dataset.title || focused.textContent || '')
          .trim().slice(0, 14) + '"'
      : 'SEM FOCO (nav ' + nav.nodes.length + ')';

    showKeyHint('tecla ' + code + ' · ' + what +
      (state.searchActive ? ' · BUSCA' : ''));

    console.log('[nebula] key=' + code, 'busca=' + state.searchActive,
      'tela=' + activeScreenId());

    if (state.playerVisible) {
      if (code === KEYS.BACK || code === KEYS.ESC) {
        event.preventDefault();
        stopPlayer();
        return;
      }

      if (code === KEYS.ENTER) {
        event.preventDefault();

        var video = $('video');

        if (video.paused) {
          video.play();
        } else {
          video.pause();
        }

        scheduleOverlayHide();
        return;
      }

      // Qualquer tecla mostra o overlay novamente.
      scheduleOverlayHide();
      return;
    }

    if (code === KEYS.BACK || code === KEYS.ESC) {
      event.preventDefault();

      var active = activeScreen();

      // A tela de boot nao tem nada focavel enquanto o servidor nao responde:
      // sem tratar aqui, o preventDefault acima cancelava o default do webOS e a
      // TV ficava presa — sem setas e sem Voltar. Voltar precisa fechar o app.
      if (active && active.id === 'screen-boot') {
        window.close();
        return;
      }

      if (active && active.id === 'screen-episodes') {
        show('screen-series');
        focusFirst();
        return;
      }

      if (active && (active.id === 'screen-catalog' || active.id === 'screen-live' ||
          active.id === 'screen-series')) {
        pausePreview();
        showMenu();
        focusFirst();
      }

      return;
    }

    // Digitando na busca: as setas movem o cursor do texto, nao o foco.
    // Digitando na busca: as setas movem o cursor do texto, nao o foco.
    if (state.searchActive) {
      if (code === KEYS.ENTER) {
        event.preventDefault();

        // Fecha o texto atual na lista e cancela o debounce pendente: um
        // re-render depois daqui roubaria o foco de volta para o primeiro card.
        commitSearch();

        if (document.activeElement && document.activeElement.blur) {
          document.activeElement.blur();
        }

        // O campo de busca e uma coluna de um no so — o moveFocus('down')
        // ficava preso nele. Desce direto para o primeiro resultado.
        var target = firstContentNode();

        if (target) {
          setFocus(target);
        } else {
          moveFocus('down');
        }

        return;
      }

      if (code === KEYS.BACK || code === KEYS.ESC) {
        event.preventDefault();

        if (document.activeElement && document.activeElement.blur) {
          document.activeElement.blur();
        }

        return;
      }

      return;
    }

    var directions = {
      37: 'left', 38: 'up', 39: 'right', 40: 'down'
    };

    if (directions[code]) {
      event.preventDefault();
      moveFocus(directions[code]);
      return;
    }

    if (code === KEYS.ENTER) {
      event.preventDefault();
      activateFocused();
    }
  });

  window.addEventListener('load', function () {
    el.activationCheck = $('activation-check');
    el.activationCheck.addEventListener('click', function () { boot(); });

    // Saida da tela de boot quando o servidor nao responde.
    $('boot-retry').addEventListener('click', function () { boot(); });

    // Busca: filtra enquanto digita (com debounce) mantendo o foco no campo, e
    // marca quando o usuario esta digitando (para as setas nao roubarem o foco).
    Object.keys(SCREEN_CONTENT).forEach(function (screenId) {
      var map = SCREEN_CONTENT[screenId];
      var input = $(map.search);

      input.addEventListener('input', function () {
        clearTimeout(state.searchTimer);
        state.searchTimer = setTimeout(function () {
          state.searchTimer = null;
          applySearch(input, map.render);
        }, 250);
      });

      input.addEventListener('focus', function () { state.searchActive = true; });
      input.addEventListener('blur', function () { state.searchActive = false; });
    });

    document.addEventListener('scroll', function () {
      clearTimeout(state.scrollTimer);
      state.scrollTimer = setTimeout(rebuildNav, 120);
    }, true);

    state.scrollTimer = null;

    fitStage();
    window.addEventListener('resize', function () {
      fitStage();
      rebuildNav();
    });

    boot();
  });
})();
