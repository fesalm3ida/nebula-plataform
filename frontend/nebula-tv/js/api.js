/**
 * Cliente da API do Nebula Core.
 *
 * Endpoints usados pelo app da TV:
 *   POST /devices/register      -> registra o aparelho (MAC + código)
 *   POST /auth/device           -> autentica (token)
 *   POST /sessions              -> abre sessão (telemetria)
 *   GET  /me/provisioning       -> listas de conteúdo
 *   GET  /me/playlists          -> listas (portal)
 */
(function (global) {
  'use strict';

  /** Prazo padrao de uma chamada ao Core (ms). */
  var REQUEST_TIMEOUT = 15000;

  function NebulaApi(baseUrl) {
    this.baseUrl = (baseUrl || '').replace(/\/+$/, '');
    this.token = null;
    this.sessionId = null;
    this.expiresAt = null;
    this.timeout = REQUEST_TIMEOUT;
  }

  /**
   * Corre a promessa com um prazo, marcando o erro com `.timeout`.
   *
   * O fetch NAO tem timeout proprio: quando o servidor aceita a conexao e nao
   * responde (instancia dormindo na nuvem, portal de wifi, TCP meio-aberto), a
   * promessa fica pendente por minutos — a TV congela em 'Conectando...' e o
   * .catch do chamador nem chega a rodar. `onTimeout` permite abortar a
   * requisicao de fato, liberando a conexao.
   */
  function withTimeout(promise, ms, onTimeout) {
    return new Promise(function (resolve, reject) {
      var timer = setTimeout(function () {
        if (onTimeout) {
          onTimeout();
        }

        var error = new Error('sem resposta do servidor (timeout de ' +
          (ms < 1000 ? ms + 'ms' : Math.round(ms / 1000) + 's') + ')');

        error.timeout = true;
        reject(error);
      }, ms);

      promise.then(function (value) {
        clearTimeout(timer);
        resolve(value);
      }, function (error) {
        clearTimeout(timer);
        reject(error);
      });
    });
  }

  NebulaApi.prototype._request = function (method, path, body, timeoutMs) {
    var options = {
      method: method,
      headers: this._headers(body),
      body: body ? JSON.stringify(body) : undefined
    };

    // AbortController existe a partir do Chromium 66 (webOS 5+): aborta de
    // fato e libera a conexao. Nas TVs antigas (webOS 3/4) o prazo sozinho ja
    // devolve o controle ao app — a requisicao segue em segundo plano ate o
    // browser desistir.
    var controller = window.AbortController ? new window.AbortController() : null;

    if (controller) {
      options.signal = controller.signal;
    }

    return withTimeout(
      fetch(this.baseUrl + path, options),
      timeoutMs || this.timeout,
      function () {
        if (controller) {
          controller.abort();
        }
      }
    ).then(function (response) {
      return response.text().then(function (text) {
        var data = null;

        try {
          data = text ? JSON.parse(text) : null;
        } catch (error) {
          data = { detail: text };
        }

        if (!response.ok) {
          var message = (data && (data.detail || data.message)) || response.status;

          if (response.status === 403) {
            var pending = new Error('DEVICE_NOT_ACTIVE');
            pending.detail = message;
            throw pending;
          }

          var failure = new Error('HTTP ' + response.status + ': ' + message);
          failure.status = response.status;
          failure.payload = data;
          throw failure;
        }

        return data;
      });
    });
  };

  NebulaApi.prototype._headers = function (withBody) {
    var headers = {};

    if (withBody) {
      headers['Content-Type'] = 'application/json';
    }

    if (this.token) {
      headers['Authorization'] = 'Bearer ' + this.token;
    }

    return headers;
  };

  NebulaApi.prototype.registerDevice = function (identity) {
    return this._request('POST', '/devices/register', {
      fingerprint: identity.fingerprint,
      mac_address: identity.macAddress,
      platform: 'webos_tv',
      app_version: identity.appVersion || '0.1.0'
    });
  };

  NebulaApi.prototype.authenticate = function (identity) {
    var self = this;

    return this._request('POST', '/auth/device', {
      device_id: identity.deviceId,
      device_key: identity.deviceKey,
      fingerprint: identity.fingerprint
    }).then(function (data) {
      self.token = data.access_token;

      return data;
    });
  };

  NebulaApi.prototype.startSession = function () {
    var self = this;

    return this._request('POST', '/sessions').then(function (data) {
      self.sessionId = data.session_id;
      self.expiresAt = data.expires_at ? Date.parse(data.expires_at) : null;

      return data;
    });
  };

  /** Garante uma sessão válida antes de enviar telemetria (durar ~30 min). */
  NebulaApi.prototype.ensureSession = function () {
    if (this.sessionId && this.expiresAt && Date.now() < this.expiresAt - 60000) {
      return Promise.resolve(this.sessionId);
    }

    return this.startSession().then(function (data) {
      return data.session_id;
    });
  };

  NebulaApi.prototype.provisioning = function () {
    return this._request('GET', '/me/provisioning');
  };

  NebulaApi.prototype.telemetry = function (eventType, payload) {
    var self = this;

    return this.ensureSession().then(function (sessionId) {
      return self._request('POST', '/me/telemetry', {
        session_id: sessionId,
        event_type: eventType,
        payload: payload || {}
      });
    });
  };

  global.NebulaApi = NebulaApi;
})(window);
