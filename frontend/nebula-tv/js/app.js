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
    catalog: [],
    focus: { column: 0, index: 0 },
    playerVisible: false,
    hideTimer: null
  };

  var el = {};

  function $(id) { return document.getElementById(id); }

  function show(screenId) {
    ['screen-boot', 'screen-activation', 'screen-menu', 'screen-catalog', 'screen-player']
      .forEach(function (id) { $(id).classList.toggle('active', id === screenId); });
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

  function boot() {
    state.identity = loadIdentity();
    setStatus('Conectando…');

    resumeOrRegister()
      .then(function () {
        setStatus('Carregando lista…');

        return api.provisioning();
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

        setStatus('Erro: ' + (error && error.message ? error.message : error));
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

  function showActivation(message) {
    $('activation-mac').textContent = state.identity.macAddress;
    $('activation-code').textContent = state.identity.activationCode || '—';
    $('activation-status').textContent = message || 'Aguardando ativação…';
    show('screen-activation');
    focusFirst();
  }

  /* ----------------------------------------------------------- playlist --- */

  function loadPlaylist(sourceUrl) {
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
      node.classList.toggle('focused', entry.name === state.category);
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

  function renderItems() {
    var container = $('catalog-items');
    var items = filteredItems();
    var limit = Math.min(items.length, MAX_RENDER);

    container.innerHTML = '';
    $('catalog-count').textContent = state.query
      ? items.length + ' resultado(s)'
      : items.length + ' itens';

    for (var i = 0; i < limit; i++) {
      var channel = items[i];
      var node = document.createElement('div');

      node.className = 'poster focusable';
      node.dataset.url = channel.url || '';
      node.dataset.title = channel.name;

      var media = channel.logo
        ? '<div class="poster-media"><img src="' + channel.logo + '" alt="" ' +
          'onerror="this.parentNode.innerHTML=\'<span class=poster-fallback>' +
          'sem imagem</span>\'"></div>'
        : '<div class="poster-media"><span class="poster-fallback">' +
          (channel.group || 'Nebula') + '</span></div>';

      var badge = state.section === 'live' ? '' :
        '<div class="poster-badge">' + (channel.group || '') + '</div>';

      node.innerHTML = media +
        '<div class="poster-title">' + channel.name + '</div>' + badge;

      container.appendChild(node);
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

    state.focus = { column: 0, index: 0 };
  }

  function applyQuery(value) {
    state.query = value.trim();
    renderItems();

    var first = document.querySelector('#catalog-items .poster');

    if (first) {
      setFocus(first);
    }
  }

  /* -------------------------------------------------------------- player --- */

  function play(url, title) {
    var video = $('video');

    $('player-title').textContent = title;
    video.src = url;
    video.play().catch(function () { /* o usuario aperta OK */ });

    show('screen-player');
    state.playerVisible = true;
    api.telemetry('playback_started', { title: title, url: url, live: state.section === 'live' })
      .catch(function () { /* melhor esforço */ });
    scheduleOverlayHide();
  }

  function stopPlayer() {
    var video = $('video');

    video.pause();
    video.removeAttribute('src');
    video.load();
    state.playerVisible = false;

    api.telemetry('playback_ended', { title: $('player-title').textContent })
      .catch(function () { /* melhor esforço */ });

    show('screen-catalog');
    focusFirst();
  }

  function scheduleOverlayHide() {
    var overlay = $('player-overlay');

    overlay.classList.remove('hidden');
    clearTimeout(state.hideTimer);
    state.hideTimer = setTimeout(function () { overlay.classList.add('hidden'); }, 4000);
  }

  /* -------------------------------------------------- foco (controle remoto) --- */

  function focusableNodes() {
    var screen = document.querySelector('.screen.active');

    if (!screen) return [];

    return Array.prototype.slice.call(screen.querySelectorAll('.focusable'))
      .filter(function (node) { return node.offsetParent !== null; });
  }

  function setFocus(node) {
    focusableNodes().forEach(function (item) {
      item.classList.toggle('focused', item === node);
    });

    if (node && node.scrollIntoView) {
      node.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }
  }

  function focusFirst() {
    var nodes = focusableNodes();

    if (nodes.length) {
      setFocus(nodes[0]);
    }
  }

  /** Navegacao espacial: escolhe o vizinho mais proximo na direcao pedida. */
  function moveFocusDirection(direction) {
    var nodes = focusableNodes();
    var current = document.querySelector('.focusable.focused');

    if (!nodes.length) return;

    if (!current) {
      focusFirst();
      return;
    }

    var origin = current.getBoundingClientRect();
    var originX = origin.left + origin.width / 2;
    var originY = origin.top + origin.height / 2;

    var best = null;
    var bestScore = Infinity;

    nodes.forEach(function (node) {
      if (node === current) return;

      var rect = node.getBoundingClientRect();
      var dx = (rect.left + rect.width / 2) - originX;
      var dy = (rect.top + rect.height / 2) - originY;

      var primary = 0;
      var secondary = 0;

      if (direction === 'left') {
        if (dx > -4) return;
        primary = -dx; secondary = Math.abs(dy);
      } else if (direction === 'right') {
        if (dx < 4) return;
        primary = dx; secondary = Math.abs(dy);
      } else if (direction === 'up') {
        if (dy > -4) return;
        primary = -dy; secondary = Math.abs(dx);
      } else {
        if (dy < 4) return;
        primary = dy; secondary = Math.abs(dx);
      }

      // Prioriza a direcao principal e penaliza o desvio lateral.
      var score = primary + secondary * 4;

      if (score < bestScore) {
        bestScore = score;
        best = node;
      }
    });

    if (best) {
      setFocus(best);
    }
  }

  function activateFocused() {
    var node = document.querySelector('.focusable.focused');

    if (!node) return;

    if (node.id === 'activation-check') {
      boot();
      return;
    }

    if (node.classList.contains('tile')) {
      var item = MENU[Number(node.dataset.index)];

      if (item.id === 'reload') {
        location.reload();
        return;
      }

      openCatalog(item.id);
      return;
    }

    if (node.classList.contains('category')) {
      state.category = node.dataset.group || null;
      renderItems();
      return;
    }

    if (node.classList.contains('poster')) {
      if (node.dataset.url) {
        play(node.dataset.url, node.dataset.title || '');
      }
    }
  }

  /* ------------------------------------------------------------- eventos --- */

  document.addEventListener('keydown', function (event) {
    var code = event.keyCode;

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

      var active = document.querySelector('.screen.active');

      if (active && active.id === 'screen-catalog') {
        showMenu();
        focusFirst();
      }

      return;
    }

    // Digitando na busca: as setas movem o cursor do texto, nao o foco.
    if (document.activeElement === $('catalog-search')) {
      if (code === KEYS.ENTER) {
        event.preventDefault();
        document.activeElement.blur();
        moveFocusDirection('down');
      }

      return;
    }

    var directions = {
      37: 'left', 38: 'up', 39: 'right', 40: 'down'
    };

    if (directions[code]) {
      event.preventDefault();
      moveFocusDirection(directions[code]);
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

    // Busca: filtra enquanto digita (com debounce) e re-renderiza a grade.
    var search = $('catalog-search');
    var debounce = null;

    search.addEventListener('input', function () {
      clearTimeout(debounce);
      debounce = setTimeout(function () { applyQuery(search.value); }, 250);
    });

    boot();
  });
})();
