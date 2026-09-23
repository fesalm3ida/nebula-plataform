/**
 * Parser de listas M3U/M3U_PLUS.
 *
 * Mesmas regras do app Android:
 *   - #EXTINF: duração, atributos (tvg-logo, group-title) e nome
 *   - #EXTGRP: agrupa as entradas seguintes
 *   - classificacao por URL: /movie/ -> filme, /series/ -> serie, resto -> ao vivo
 */
(function (global) {
  'use strict';

  function parseAttributes(line) {
    var attributes = {};
    var pattern = /([a-zA-Z0-9_-]+)="([^"]*)"/g;
    var match;

    while ((match = pattern.exec(line)) !== null) {
      attributes[match[1].toLowerCase()] = match[2];
    }

    return attributes;
  }

  function classify(url) {
    var target = String(url || '').toLowerCase();

    if (target.indexOf('/movie/') !== -1) {
      return 'movie';
    }

    if (target.indexOf('/series/') !== -1) {
      return 'series';
    }

    return 'live';
  }

  function parse(text) {
    var channels = [];
    var pending = null;
    var stickyGroup = '';

    String(text || '').split(/\r?\n/).forEach(function (rawLine) {
      var line = rawLine.trim();

      if (!line) {
        return;
      }

      if (line.indexOf('#EXTINF:') === 0) {
        var attributes = parseAttributes(line);
        var commaIndex = line.lastIndexOf(',');
        var title = commaIndex !== -1 ? line.substring(commaIndex + 1).trim() : '';

        // "Grupo:Nome" no titulo (comum em listas IPTV).
        var group = attributes['group-title'] || stickyGroup || '';
        var name = title;

        if (!attributes['group-title'] && title.indexOf(':') !== -1) {
          var parts = title.split(':');

          if (parts[0].length <= 24 && parts.length > 1) {
            group = parts[0].trim();
            name = parts.slice(1).join(':').trim();
          }
        }

        pending = {
          name: name || title || 'Sem nome',
          group: group,
          logo: attributes['tvg-logo'] || attributes['logo'] || ''
        };

        return;
      }

      if (line.indexOf('#EXTGRP:') === 0) {
        stickyGroup = line.substring(8).trim();

        if (pending) {
          pending.group = stickyGroup;
        }

        return;
      }

      if (line.charAt(0) === '#') {
        return;
      }

      if (pending) {
        pending.url = line;
        pending.kind = classify(line);
        channels.push(pending);
        pending = null;
      }
    });

    return channels;
  }

  function categoriesOf(channels) {
    var seen = {};
    var categories = [];

    channels.forEach(function (channel) {
      if (channel.group && !seen[channel.group]) {
        seen[channel.group] = true;
        categories.push(channel.group);
      }
    });

    return categories.sort(function (a, b) {
      return a.localeCompare(b);
    });
  }

  global.NebulaM3u = { parse: parse, categoriesOf: categoriesOf, classify: classify };
})(window);
