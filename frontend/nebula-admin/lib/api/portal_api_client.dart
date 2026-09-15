import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/portal_config.dart';
import '../models/portal.dart';

/// Cliente do portal do **usuário** (MAC + código de ativação).
class PortalApiClient {
  PortalApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  String get _base => PortalConfig.apiBaseUrl;

  Future<PortalSession> login(
    String macAddress,
    String activationCode,
  ) async {
    final response = await _client.post(
      Uri.parse('$_base/portal/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'mac_address': macAddress,
        'activation_code': activationCode,
      }),
    );

    if (response.statusCode == 401 || response.statusCode == 404) {
      throw PortalApiException(
        'MAC Address ou código de ativação inválidos.',
      );
    }

    if (response.statusCode != 200) {
      throw PortalApiException(
        'Falha no login (${response.statusCode}).',
      );
    }

    return PortalSession.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<PortalDevice> device(String token) async {
    final response = await _client.get(
      Uri.parse('$_base/portal/device'),
      headers: _headers(token),
    );

    _ensureOk(response, 'carregar o aparelho');

    return PortalDevice.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<PortalDevice> activate(String token) async {
    final response = await _client.post(
      Uri.parse('$_base/portal/device/activation'),
      headers: _headers(token),
    );

    if (response.statusCode == 409) {
      throw PortalApiException(
        'A licença expirou. Adquira uma licença para continuar.',
      );
    }

    _ensureOk(response, 'ativar o aparelho');

    return PortalDevice.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<PortalPlaylist> registerPlaylist(
    String token,
    String name,
    String sourceUrl,
  ) async {
    final response = await _client.post(
      Uri.parse('$_base/portal/playlist'),
      headers: {
        'Content-Type': 'application/json',
        ..._headers(token),
      },
      body: jsonEncode({
        'name': name,
        'source_url': sourceUrl,
        'format': 'm3u',
      }),
    );

    if (response.statusCode != 201) {
      throw PortalApiException(
        'Falha ao cadastrar a lista (${response.statusCode}).',
      );
    }

    return PortalPlaylist.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  /// Confirma pagamentos pendentes junto ao provedor e devolve o aparelho.
  Future<PortalDevice> syncPayments(String token) async {
    final response = await _client.post(
      Uri.parse('$_base/portal/payments/sync'),
      headers: _headers(token),
    );

    _ensureOk(response, 'verificar o pagamento');

    return PortalDevice.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<List<PortalPlan>> listPlans(String token) async {
    final response = await _client.get(
      Uri.parse('$_base/portal/plans'),
      headers: _headers(token),
    );

    _ensureOk(response, 'carregar os planos');

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final list = data['plans'] as List<dynamic>;

    return list
        .map((item) => PortalPlan.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Inicia a compra e devolve a URL do checkout.
  Future<String> purchase(String token, String product) async {
    final response = await _client.post(
      Uri.parse('$_base/portal/purchase'),
      headers: {
        'Content-Type': 'application/json',
        ..._headers(token),
      },
      body: jsonEncode({'product': product}),
    );

    if (response.statusCode != 201) {
      throw PortalApiException(
        'Falha ao iniciar a compra (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return data['checkout_url'] as String;
  }

  Map<String, String> _headers(String token) => {
        'Authorization': 'Bearer $token',
      };

  void _ensureOk(http.Response response, String action) {
    if (response.statusCode == 401) {
      throw PortalApiException('Sessão expirada. Entre novamente.');
    }

    if (response.statusCode != 200) {
      throw PortalApiException(
        'Falha ao $action (${response.statusCode}).',
      );
    }
  }
}

class PortalApiException implements Exception {
  PortalApiException(this.message);

  final String message;

  @override
  String toString() => message;
}
