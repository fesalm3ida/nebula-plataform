/**
 * Verificacao estatica: todo id usado pelo app existe no HTML e todos os
 * scripts/estilos referenciados existem no disco.
 * Roda com: node test/structure.test.js
 */
const fs = require('fs');
const path = require('path');

const raiz = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(raiz, 'index.html'), 'utf8');
const app = fs.readFileSync(path.join(raiz, 'js/app.js'), 'utf8');

let falhas = 0;

function check(nome, ok, detalhe) {
  console.log(`${ok ? '✅' : '❌'} ${nome}${ok ? '' : ' -> ' + detalhe}`);
  if (!ok) falhas++;
}

// 1) ids do HTML
const idsHtml = new Set([...html.matchAll(/id="([^"]+)"/g)].map((m) => m[1]));
const idsJs = new Set([...app.matchAll(/\$\('([^']+)'\)/g)].map((m) => m[1]));

const ausentes = [...idsJs].filter((id) => !idsHtml.has(id));
check(`ids usados pelo app existem no HTML (${idsJs.size} verificados)`,
  ausentes.length === 0, ausentes.join(', '));

// 2) arquivos referenciados
const refs = [
  ...html.matchAll(/<script src="([^"]+)"/g),
  ...html.matchAll(/<link rel="stylesheet" href="([^"]+)"/g)
].map((m) => m[1]);

const faltando = refs.filter((ref) => !fs.existsSync(path.join(raiz, ref)));
check(`scripts/estilos existem (${refs.length} referencias)`,
  faltando.length === 0, faltando.join(', '));

// 3) appinfo.json coerente
const appinfo = JSON.parse(fs.readFileSync(path.join(raiz, 'appinfo.json'), 'utf8'));

for (const campo of ['id', 'version', 'main', 'title', 'icon', 'largeIcon']) {
  check(`appinfo.json tem "${campo}"`, Boolean(appinfo[campo]), 'ausente');
}

check('appinfo aponta para um main existente',
  fs.existsSync(path.join(raiz, appinfo.main)), appinfo.main);
check('appinfo aponta para icones existentes',
  fs.existsSync(path.join(raiz, appinfo.icon)) &&
  fs.existsSync(path.join(raiz, appinfo.largeIcon)),
  `${appinfo.icon} / ${appinfo.largeIcon}`);

console.log(falhas === 0 ? '\nEstrutura consistente ✅' : `\n${falhas} problema(s) ❌`);
process.exit(falhas === 0 ? 0 : 1);
