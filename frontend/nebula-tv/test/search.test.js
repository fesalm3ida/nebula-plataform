/** Testes da busca do app webOS. Roda com: node test/search.test.js */
global.window = {};
require('../js/search.js');

const { normalize, matches } = global.window.NebulaSearch;

let falhas = 0;

function check(nome, obtido, esperado) {
  const ok = JSON.stringify(obtido) === JSON.stringify(esperado);
  console.log(`${ok ? '✅' : '❌'} ${nome}`);
  if (!ok) {
    console.log(`   esperado: ${JSON.stringify(esperado)} | obtido: ${JSON.stringify(obtido)}`);
    falhas++;
  }
}

check('normaliza acentos', normalize('Órfãos da Terra'), 'orfaos da terra');
check('termo vazio combina com tudo', matches('Qualquer', ''), true);
check('ignora maiusculas', matches('O Poderoso Chefao', 'PODEROSO'), true);
check('ignora acentos nos dois lados', matches('Órfãos da Terra', 'orfaos'), true);
check('encontra com acento na busca', matches('Orfaos da Terra', 'órfãos'), true);
check('varios termos em qualquer ordem', matches('Star Wars: Uma Nova Esperanca', 'wars star'), true);
check('termo ausente nao combina', matches('Matrix', 'avatar'), false);
check('casa com parte do titulo', matches('Velozes e Furiosos 10', 'furios'), true);

console.log(falhas === 0 ? '\nTodos os testes de busca passaram ✅' : `\n${falhas} falha(s) ❌`);
process.exit(falhas === 0 ? 0 : 1);
