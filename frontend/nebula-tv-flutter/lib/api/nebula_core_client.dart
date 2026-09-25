import 'dart:async';
import 'dart:convert';
import 'dart:io';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/device_identity.dart';
import '../models/provisioning.dart';

/// Sessão aberta no Core (a telemetria exige sessão ativa).
class DeviceSession {
  const DeviceSession({required this.sessionId, required this.expiresAt});

  final String sessionId;
  final DateTime? expiresAt;

  bool get isExpired =>
      expiresAt != null && DateTime.now().toUtc().isAfter(expiresAt!);
}

class NebulaCoreClient {
  NebulaCoreClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  /// Tempo maximo de cada tentativa. O Core no plano free do Render "dorme" e
  /// a primeira chamada dispara o cold start (~25 s).
  static const Duration _timeout = Duration(seconds: 45);

  static const int _attempts = 3;

  /// Envia a requisicao com timeout e reenvio em falhas de rede.
  ///
  /// Sem isso, um cold start (conexao abortada) ou uma oscilacao de rede
  /// derrubava o boot do app com o erro cru do socket.
  Future<http.Response> _send(
    Future<http.Response> Function() request,
  ) async {
    for (var attempt = 1; attempt <= _attempts; attempt++) {
      try {
        return await request().timeout(_timeout);
      } on TimeoutException {
        // Tenta de novo (cold start do servidor).
      } on SocketException {
        // Rede instavel ou conexao abortada: tenta de novo.
      } on http.ClientException {
        // Idem.
      }

      if (attempt < _attempts) {
        await Future<void>.delayed(Duration(seconds: 2 * attempt));
      }
    }

    throw NebulaCoreException(
      'Nao foi possivel falar com o servidor. '
      'Verifique a conexao e tente novamente.',
    );
  }

  Future<DeviceIdentity> registerDevice({
    required String fingerprint,
    required String macAddress,
    required String platform,
    required String appVersion,
  }) async {
    final response = await _send(() => _client.post(
      Uri.parse('${ApiConfig.baseUrl}/devices/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'fingerprint': fingerprint,
        'mac_address': macAddress,
        'platform': platform,
        'app_version': appVersion,
      }),
    ));

    if (response.statusCode != 201) {
      throw NebulaCoreException(
        'Falha no registro (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return DeviceIdentity(
      fingerprint: fingerprint,
      deviceId: data['device_id'] as String,
      deviceKey: data['device_key'] as String,
      activationCode: (data['activation_code'] as String?) ?? '',
      macAddress: (data['mac_address'] as String?) ?? macAddress,
    );
  }

  Future<String> authenticateDevice({
    required String deviceId,
    required String deviceKey,
    required String fingerprint,
  }) async {
    final response = await _send(() => _client.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/device'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'device_id': deviceId,
        'device_key': deviceKey,
        'fingerprint': fingerprint,
      }),
    ));

    if (response.statusCode != 200) {
      throw NebulaCoreException(
        'Falha na autenticação (${response.statusCode}).',
        statusCode: response.statusCode,
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return data['access_token'] as String;
  }

  Future<DeviceSession> startSession(String token) async {
    final response = await _send(() => _client.post(
      Uri.parse('${ApiConfig.baseUrl}/sessions'),
      headers: {'Authorization': 'Bearer $token'},
    ));

    if (response.statusCode != 201) {
      throw NebulaCoreException(
        'Falha ao iniciar sessão (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final expiresAt = data['expires_at'] as String?;

    return DeviceSession(
      sessionId: data['session_id'] as String,
      expiresAt: expiresAt == null ? null : DateTime.parse(expiresAt).toUtc(),
    );
  }

  Future<Provisioning> getProvisioning(String token) async {
    final response = await _send(() => _client.get(
      Uri.parse('${ApiConfig.baseUrl}/me/provisioning'),
      headers: {'Authorization': 'Bearer $token'},
    ));

    if (response.statusCode != 200) {
      throw NebulaCoreException(
        'Falha no provisionamento (${response.statusCode}).',
      );
    }

    return Provisioning.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<void> heartbeat(String token, String sessionId) async {
    final response = await _send(() => _client.post(
      Uri.parse('${ApiConfig.baseUrl}/sessions/$sessionId/heartbeat'),
      headers: {'Authorization': 'Bearer $token'},
    ));

    if (response.statusCode != 200) {
      throw NebulaCoreException(
        'Falha no heartbeat (${response.statusCode}).',
      );
    }
  }

  Future<void> sendTelemetry(
    String token,
    String sessionId,
    String eventType,
    Map<String, dynamic> payload,
  ) async {
    final response = await _send(() => _client.post(
      Uri.parse('${ApiConfig.baseUrl}/me/telemetry'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'session_id': sessionId,
        'event_type': eventType,
        'payload': payload,
      }),
    ));

    if (response.statusCode != 201) {
      throw NebulaCoreException(
        'Falha na telemetria (${response.statusCode}).',
      );
    }
  }
}

class NebulaCoreException implements Exception {
  NebulaCoreException(this.message, {this.statusCode});

  final String message;
  final int? statusCode;

  @override
  String toString() => message;
}
