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
    focus: { column: 0, index: 0 },
    playerVisible: false,
    previewTimer: null,
    seriesGroups: [],
    episodeGroup: null,
    hideTimer: null
  };

  var el = {};

  function $(id) { return document.getElementById(id); }

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

    ['screen-boot', 'screen-activation', 'screen-menu', 'screen-live',
     'screen-catalog', 'screen-series', 'screen-episodes', 'screen-player']
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

        // 404: aparelho ativo, porem sem lista associada. Em vez do erro cru,
        // mostra MAC + codigo para o usuario cadastrar a lista no portal.
        if (error && error.status === 404) {
          return showActivation(
            'Nenhuma lista cadastrada para este aparelho. Acesse o portal, ' +
            'informe o MAC e o código abaixo e cadastre sua lista.'
          );
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
      node.classList.toggle('focused', entry.name === state.category);
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
    $('live-count').textContent = items.length + ' canais';

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

    if (channel.logo) {
      var image = document.createElement('img');

      image.className = 'channel-logo';
      image.alt = '';
      image.src = channel.logo;
      image.addEventListener('error', function () {
        image.replaceWith(logoPlaceholder(channel));
      });
      row.appendChild(number);
      row.appendChild(image);
    } else {
      row.appendChild(number);
      row.appendChild(logoPlaceholder(channel));
    }

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

  /** Card da grade: capa (com fallback) + titulo + categoria. */
  function buildCard(channel) {
    var card = document.createElement('div');
    var media = document.createElement('div');
    var title = document.createElement('div');

    card.className = 'poster focusable';
    card.dataset.url = channel.url || '';
    card.dataset.title = channel.name || '';

    media.className = 'poster-media';

    if (channel.logo) {
      var image = document.createElement('img');

      image.alt = '';
      image.src = channel.logo;
      image.addEventListener('error', function () {
        // Capa indisponivel: mantem o card legivel com o nome do grupo.
        media.innerHTML = '';
        media.appendChild(fallbackLabel(channel));
      });
      media.appendChild(image);
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
    var container = $('catalog-items');
    var items = filteredItems();
    var limit = Math.min(items.length, MAX_RENDER);

    container.innerHTML = '';
    $('catalog-count').textContent = state.query
      ? items.length + ' resultado(s)'
      : items.length + ' itens';

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
        node.classList.toggle('focused', entry.name === state.category);
        node.textContent = entry.label;
        node.dataset.group = entry.name || '';
        container.appendChild(node);
      });
  }

  function renderSeries() {
    var container = $('series-items');
    var groups = seriesItems();
    var limit = Math.min(groups.length, MAX_SERIES);

    container.innerHTML = '';
    $('series-count').textContent = groups.length + ' séries';

    for (var i = 0; i < limit; i++) {
      container.appendChild(buildSeriesCard(groups[i]));
    }

    if (!groups.length) {
      var empty = document.createElement('div');

      empty.className = 'limit-hint';
      empty.textContent = 'Nenhuma série encontrada.';
      container.appendChild(empty);
    }
  }

  function buildSeriesCard(group) {
    var card = document.createElement('div');
    var media = document.createElement('div');
    var title = document.createElement('div');
    var sub = document.createElement('div');

    card.className = 'poster focusable';
    card.dataset.group = window.NebulaSearch.normalize(group.name);

    media.className = 'poster-media';

    if (group.poster) {
      var image = document.createElement('img');

      image.alt = '';
      image.src = group.poster;
      image.addEventListener('error', function () {
        media.innerHTML = '';
        media.appendChild(fallbackLabel({ name: group.name }));
      });
      media.appendChild(image);
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

  function play(url, title) {
    var video = $('video');

    pausePreview();

    $('player-title').textContent = title;
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

      // Sincroniza o foco real: evita divergencia entre o destaque visual e o
      // elemento realmente focado (o que travava a navegacao no controle).
      if (item.tagName === 'INPUT' && item !== node) {
        item.blur();
      }
    });

    if (node && node.tagName === 'INPUT') {
      node.focus();
    }

    if (node && node.scrollIntoView) {
      node.scrollIntoView({ block: 'nearest', inline: 'nearest' });
    }

    // Canal em foco no Ao vivo: atualiza o preview.
    if (node && node.classList.contains('channel')) {
      updatePreview({
        name: node.dataset.title,
        group: node.dataset.group,
        url: node.dataset.url
      });
    }
  }

  function focusFirst() {
    var nodes = focusableNodes();

    if (!nodes.length) return;

    // O campo de busca vem primeiro no HTML, mas o foco inicial deve ir para
    // o conteudo (categorias/itens) — a busca e opcional.
    var content = nodes.filter(function (node) {
      return node.tagName !== 'INPUT';
    });

    setFocus(content.length ? content[0] : nodes[0]);
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
      console.log('[nebula] foco ->', best.className,
        (best.dataset.title || best.textContent || '').slice(0, 30));
      setFocus(best);
      return;
    }

    console.log('[nebula] sem vizinho para', direction,
      '| focaveis=' + nodes.length, '| atual=' + current.className);

    // Sem vizinho naquela direcao (ex.: fim da grade): nao trava o usuario —
    // cai para o vizinho na ordem do documento.
    var index = nodes.indexOf(current);
    var fallback = { left: -1, up: -1, right: 1, down: 1 }[direction];

    if (fallback && nodes[index + fallback]) {
      setFocus(nodes[index + fallback]);
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

      var active = document.querySelector('.screen.active');

      if (active && active.id === 'screen-live') {
        renderLiveChannels();
      } else if (active && active.id === 'screen-series') {
        renderSeries();
      } else {
        renderItems();
      }

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

  // O controle "Magic Remote" da LG envia eventos de mouse: passar o ponteiro
  // move o foco e clicar equivale a apertar OK.
  document.addEventListener('mousemove', function (event) {
    var node = focusableFrom(event.target);

    if (node && !node.classList.contains('focused')) {
      setFocus(node);
    }
  });

  document.addEventListener('click', function (event) {
    var node = focusableFrom(event.target);

    if (!node) return;

    event.preventDefault();
    setFocus(node);
    activateFocused();
  });

  // Evita o menu de contexto do botao direito no controle.
  document.addEventListener('contextmenu', function (event) {
    event.preventDefault();
  });

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

    // Auto-correcao: se o estado de busca ficou "preso" (sem nenhum input
    // realmente focado), as setas voltam a navegar.
    if (state.searchActive) {
      var active = document.activeElement;

      if (!active || active.tagName !== 'INPUT') {
        state.searchActive = false;
      }
    }

    console.log('[nebula] key=' + code, 'busca=' + state.searchActive,
      'tela=' + (document.querySelector('.screen.active') || {}).id);

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

        if (document.activeElement && document.activeElement.blur) {
          document.activeElement.blur();
        }

        moveFocusDirection('down');
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

    // Marca quando o usuario esta digitando (para as setas nao roubarem o foco).
    search.addEventListener('focus', function () { state.searchActive = true; });
    search.addEventListener('blur', function () { state.searchActive = false; });

    var liveSearch = $('live-search');
    var liveDebounce = null;

    liveSearch.addEventListener('input', function () {
      clearTimeout(liveDebounce);
      liveDebounce = setTimeout(function () {
        state.query = liveSearch.value.trim();
        renderLiveChannels();

        var first = document.querySelector('#live-channels .channel');

        if (first) {
          setFocus(first);
        }
      }, 250);
    });

    liveSearch.addEventListener('focus', function () { state.searchActive = true; });
    liveSearch.addEventListener('blur', function () { state.searchActive = false; });

    var seriesSearch = $('series-search');
    var seriesDebounce = null;

    seriesSearch.addEventListener('input', function () {
      clearTimeout(seriesDebounce);
      seriesDebounce = setTimeout(function () {
        state.query = seriesSearch.value.trim();
        renderSeries();

        var first = document.querySelector('#series-items .poster');

        if (first) {
          setFocus(first);
        }
      }, 250);
    });

    seriesSearch.addEventListener('focus', function () { state.searchActive = true; });
    seriesSearch.addEventListener('blur', function () { state.searchActive = false; });

    fitStage();
    window.addEventListener('resize', fitStage);

    boot();
  });
})();
