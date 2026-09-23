/**
 * Testes do parser M3U do app webOS (mesmas regras do app Android).
 * Roda com Node: `node test/m3u.test.js`
 */
global.window = {};
require('../js/m3u.js');

const { parse, categoriesOf, classify } = global.window.NebulaM3u;

let falhas = 0;

function check(nome, obtido, esperado) {
  const ok = JSON.stringify(obtido) === JSON.stringify(esperado);
  console.log(`${ok ? '✅' : '❌'} ${nome}`);
  if (!ok) {
    console.log(`   esperado: ${JSON.stringify(esperado)}`);
    console.log(`   obtido  : ${JSON.stringify(obtido)}`);
    falhas++;
  }
}

// ---------------------------------------------------------------- amostra ---
const lista = `#EXTM3U
#EXTINF:-1 tvg-logo="http://logo/record.png" group-title="Canais",Record News +HD
http://servidor/live/user/pass/1234.ts
#EXTINF:-1 group-title="Canais",Globo SP
http://servidor/live/user/pass/1235.ts
#EXTINF:-1 tvg-logo="http://logo/m1.png" group-title="Filmes",Matrix
http://servidor/movie/user/pass/501.mp4
#EXTINF:-1,Series:Breaking Bad S01E01
http://servidor/series/user/pass/9001.mkv
#EXTGRP:Documentarios
#EXTINF:-1,Planeta Terra
http://servidor/live/user/pass/2001.ts
# comentario ignorado
`;

const canais = parse(lista);

check('total de itens', canais.length, 5);
check('classifica ao vivo', canais[0].kind, 'live');
check('classifica filme', canais[2].kind, 'movie');
check('classifica serie', canais[3].kind, 'series');
check('logo do tvg-logo', canais[0].logo, 'http://logo/record.png');
check('grupo do group-title', canais[0].group, 'Canais');
check('nome limpo (sem o grupo)', canais[0].name, 'Record News +HD');
check('titulo com "Grupo:Nome" vira grupo + nome', [canais[3].group, canais[3].name],
  ['Series', 'Breaking Bad S01E01']);
check('EXTGRP agrupa a entrada seguinte', [canais[4].group, canais[4].name],
  ['Documentarios', 'Planeta Terra']);
check('url capturada', canais[1].url, 'http://servidor/live/user/pass/1235.ts');

const categorias = categoriesOf(canais);
check('categorias unicas e ordenadas', categorias, ['Canais', 'Documentarios', 'Filmes', 'Series']);

check('classificacao por URL (/movie/)', classify('http://x/movie/a/b.mp4'), 'movie');
check('classificacao por URL (/series/)', classify('http://x/series/a/b.mkv'), 'series');
check('classificacao por URL (resto = live)', classify('http://x/live/a/b.ts'), 'live');
check('lista vazia', parse('').length, 0);

console.log(falhas === 0 ? '\nTodos os testes passaram ✅' : `\n${falhas} teste(s) falharam ❌`);
process.exit(falhas === 0 ? 0 : 1);
