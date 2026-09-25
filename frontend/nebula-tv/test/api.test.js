/**
 * Teste do cliente HTTP do Core (js/api.js): o prazo (timeout) das
 * requisicoes.
 *
 * O fetch nao tem timeout proprio; sem o prazo, um servidor que aceita a
 * conexao e nunca responde deixa a promessa pendente e a TV congela em
 * 'Conectando...' sem chegar no .catch. Aqui o servidor mudo e simulado com um
 * fetch falso, entao o teste roda em Node — sem TV e sem rede.
 *
 * Roda com: node test/api.test.js
 */
const path = require('path');

let falhas = 0;

function check(nome, ok, detalhe) {
  console.log(`${ok ? '✅' : '❌'} ${nome}${ok ? '' : ' -> ' + detalhe}`);
  if (!ok) falhas++;
}

// js/api.js e um IIFE que recebe o `window`: em Node basta expor o global.
global.window = {};
require(path.join(__dirname, '..', 'js', 'api.js'));

const NebulaApi = global.window.NebulaApi;

/** Resposta falsa minima (o cliente so usa ok, status e text()). */
function resposta(status, corpo) {
  return {
    ok: status >= 200 && status < 300,
    status: status,
    text: function () {
      return Promise.resolve(corpo === undefined ? '' : corpo);
    }
  };
}

/** Servidor que aceita a conexao e nunca responde. */
function servidorMudo() {
  global.fetch = function () {
    return new Promise(function () { /* pendente para sempre */ });
  };
}

function novoApi() {
  return new NebulaApi('https://exemplo.invalido');
}

/** Caso principal: a requisicao pendurada precisa estourar o prazo. */
async function prazoEstoura() {
  servidorMudo();

  try {
    await novoApi()._request('GET', '/me/provisioning', null, 60);
    check('requisicao pendente estoura o prazo', false, 'resolveu em vez de estourar');
  } catch (error) {
    check('requisicao pendente estoura o prazo', error.timeout === true,
      'erro sem a marca .timeout: ' + error.message);
    check('a mensagem do prazo diz o limite',
      /timeout de 60ms/.test(error.message), error.message);
  }
}

/** Com AbortController (Chromium 66+, webOS 5+) a conexao e abortada de fato. */
async function abortaConexao() {
  servidorMudo();

  let abortado = false;

  global.window.AbortController = function () {
    this.signal = {};

    this.abort = function () { abortado = true; };
  };

  try {
    await novoApi()._request('GET', '/auth/device', {}, 60);
  } catch (error) {
    /* o prazo e o esperado aqui */
  }

  check('aborta a conexao quando ha AbortController', abortado === true,
    'abort() nao foi chamado');

  delete global.window.AbortController;
}

/** Uma resposta normal nao pode ser afetada pelo prazo. */
async function respostaNormal() {
  global.fetch = function () {
    return Promise.resolve(
      resposta(200, '{"content_endpoints":[{"source_url":"http://provedor/lista.m3u"}]}')
    );
  };

  const dados = await novoApi()._request('GET', '/me/provisioning');
  const url = dados && dados.content_endpoints && dados.content_endpoints[0].source_url;

  check('resposta 200 resolve o JSON normalmente',
    url === 'http://provedor/lista.m3u', JSON.stringify(dados));
}

/** 403 continua virando DEVICE_NOT_ACTIVE (o boot depende disso). */
async function dispositivoNaoAtivo() {
  global.fetch = function () {
    return Promise.resolve(resposta(403, '{"detail":"device not active"}'));
  };

  try {
    await novoApi()._request('GET', '/me/provisioning');
    check('403 vira DEVICE_NOT_ACTIVE', false, 'resolveu em vez de falhar');
  } catch (error) {
    check('403 vira DEVICE_NOT_ACTIVE', error.message === 'DEVICE_NOT_ACTIVE',
      error.message);
  }
}

/** 5xx preserva .status (a repeticao do boot classifica por ele). */
async function erroDeServidor() {
  global.fetch = function () {
    return Promise.resolve(resposta(503, 'indisponivel'));
  };

  try {
    await novoApi()._request('GET', '/me/provisioning');
    check('503 preserva o status no erro', false, 'resolveu em vez de falhar');
  } catch (error) {
    check('503 preserva o status no erro', error.status === 503,
      'status=' + error.status);
  }
}

(async function () {
  await prazoEstoura();
  await abortaConexao();
  await respostaNormal();
  await dispositivoNaoAtivo();
  await erroDeServidor();

  console.log(falhas === 0
    ? '\nTodos os testes do cliente passaram ✅'
    : `\n${falhas} problema(s) ❌`);

  process.exit(falhas === 0 ? 0 : 1);
})();
