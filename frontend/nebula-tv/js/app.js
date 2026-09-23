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
    el.identity = state.identity = loadIdentity();
    setStatus('Registrando aparelho…');

    api.registerDevice(state.identity)
      .then(function (data) {
        state.identity.deviceId = data.device_id;
        state.identity.deviceKey = data.device_key;
        state.identity.activationCode = data.activation_code;
        state.identity.macAddress = data.mac_address || state.identity.macAddress;
        saveIdentity();

        return api.authenticate(state.identity);
      })
      .then(function () {
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

    $('catalog-title').textContent = kind === 'live' ? 'Ao vivo' : (kind === 'movie' ? 'Filmes' : 'Séries');

    renderCategories();
    renderItems();
    show('screen-catalog');
    state.focus = { column: 0, index: 0 };
    focusFirst();
  }

  function renderCategories() {
    var container = $('catalog-categories');
    var groups = window.NebulaM3u.categoriesOf(state.catalog);

    container.innerHTML = '';

    [{ name: null, label: 'Todas' }].concat(groups.map(function (group) {
      return { name: group, label: group };
    })).forEach(function (entry, index) {
      var node = document.createElement('div');

      node.className = 'category focusable';
      node.textContent = entry.label;
      node.dataset.index = index;
      node.dataset.group = entry.name || '';
      container.appendChild(node);
    });
  }

  function renderItems() {
    var container = $('catalog-items');

    container.innerHTML = '';

    var items = state.category
      ? state.catalog.filter(function (channel) { return channel.group === state.category; })
      : state.catalog;

    $('catalog-count').textContent = items.length + ' itens';

    items.slice(0, 400).forEach(function (channel, index) {
      var node = document.createElement('div');
      var logo = channel.logo
        ? '<img class="item-logo" src="' + channel.logo + '" alt="">'
        : '';

      node.className = 'item focusable';
      node.innerHTML = '<div class="item-row">' + logo + '<span>' + channel.name + '</span></div>';
      node.dataset.index = index;
      node.dataset.url = channel.url;
      container.appendChild(node);
    });
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

    return Array.prototype.slice.call(screen.querySelectorAll('.focusable'));
  }

  function focusFirst() {
    var nodes = focusableNodes();

    nodes.forEach(function (node, index) {
      node.classList.toggle('focused', index === 0);
    });

    var first = nodes[0];

    if (first && first.scrollIntoView) {
      first.scrollIntoView({ block: 'nearest' });
    }
  }

  function moveFocus(step) {
    var nodes = focusableNodes();

    if (!nodes.length) return;

    var current = 0;

    nodes.forEach(function (node, index) {
      if (node.classList.contains('focused')) current = index;
    });

    var next = Math.min(Math.max(current + step, 0), nodes.length - 1);

    nodes.forEach(function (node, index) {
      node.classList.toggle('focused', index === next);
    });

    nodes[next].scrollIntoView({ block: 'nearest' });
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

    if (node.classList.contains('item')) {
      play(node.dataset.url, node.textContent.trim());
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

    if (code === KEYS.UP || code === KEYS.LEFT) {
      event.preventDefault();
      moveFocus(-1);
      return;
    }

    if (code === KEYS.DOWN || code === KEYS.RIGHT) {
      event.preventDefault();
      moveFocus(1);
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
    boot();
  });
})();
