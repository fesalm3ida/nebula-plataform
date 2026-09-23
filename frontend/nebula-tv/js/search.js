/**
 * Busca por título (mesmas regras do app Android): ignora acentos e
 * maiúsculas/minúsculas, e aceita vários termos em qualquer ordem.
 */
(function (global) {
  'use strict';

  var ACCENTS = {
    'á':'a','à':'a','ã':'a','â':'a','ä':'a',
    'é':'e','è':'e','ê':'e','ë':'e',
    'í':'i','ì':'i','î':'i','ï':'i',
    'ó':'o','ò':'o','õ':'o','ô':'o','ö':'o',
    'ú':'u','ù':'u','û':'u','ü':'u',
    'ç':'c','ñ':'n',
    'Á':'a','À':'a','Ã':'a','Â':'a','Ä':'a',
    'É':'e','È':'e','Ê':'e','Ë':'e',
    'Í':'i','Ì':'i','Î':'i','Ï':'i',
    'Ó':'o','Ò':'o','Õ':'o','Ô':'o','Ö':'o',
    'Ú':'u','Ù':'u','Û':'u','Ü':'u',
    'Ç':'c','Ñ':'n'
  };

  function normalize(value) {
    var text = String(value || '').trim().toLowerCase();
    var out = '';

    for (var i = 0; i < text.length; i++) {
      var char = text[i];
      out += ACCENTS[char] || char;
    }

    return out;
  }

  /** Um termo vazio combina com tudo; todos os termos precisam aparecer. */
  function matches(title, query) {
    var term = normalize(query);

    if (!term) {
      return true;
    }

    var normalizedTitle = normalize(title);

    return term.split(/\s+/).filter(Boolean).every(function (word) {
      return normalizedTitle.indexOf(word) !== -1;
    });
  }

  global.NebulaSearch = { normalize: normalize, matches: matches };
})(window);
