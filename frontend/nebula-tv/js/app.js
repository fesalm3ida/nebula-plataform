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

  function play(url, title) {
    var video = $('video');

    // IMPORTANTE: gravar a origem ANTES de trocar de tela (senao gravariamos
    // 'screen-player' e o Voltar cairia numa tela preta).
    var active = activeScreen();

    state.playReturn = active && active.id !== 'screen-player'
      ? active.id
      : 'screen-catalog';

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
      var items = Array.prototype.slice
        .call(container.querySelectorAll('.focusable'))
        .filter(function (node) { return node.offsetParent !== null; });

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
        return node.offsetParent !== null && nav.nodes.indexOf(node) === -1;
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
      var step = direction === 'up' ? -1 : 1;
      var distance = column.cols > 1 ? column.cols : 1;
      var target = nav.row + step * distance;

      if (target >= 0 && target < column.nodes.length) {
        nav.row = target;
        setFocus(nodeAt(nav.col, nav.row));
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

    nav.nodes.forEach(function (item) {
      item.classList.toggle('focused', item === node);

      if (item.tagName === 'INPUT' && item !== node) {
        item.blur();
      }
    });

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

    var active = activeScreen();

    if (!active) return;

    if (active.id === 'screen-live') {
      renderLiveChannels();
    } else if (active.id === 'screen-series') {
      renderSeries();
    } else if (active.id === 'screen-catalog') {
      renderItems();
    }

    rebuildNav();
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
    // A classe .focused e a unica fonte da verdade (so setFocus a aplica).
    var node = document.querySelector('.focusable.focused');

    if (!node) return;

    if (node.id === 'activation-check') {
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
      'tela=' + ((screen || {}).id));

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

        moveFocus('down');
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
