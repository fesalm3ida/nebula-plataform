import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/device_identity.dart';
import '../models/provisioning.dart';

class NebulaCoreClient {
  NebulaCoreClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<DeviceIdentity> registerDevice({
    required String fingerprint,
    required String macAddress,
    required String platform,
    required String appVersion,
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/devices/register'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'fingerprint': fingerprint,
        'mac_address': macAddress,
        'platform': platform,
        'app_version': appVersion,
      }),
    );

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
    );
  }

  Future<String> authenticateDevice({
    required String deviceId,
    required String deviceKey,
    required String fingerprint,
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/auth/device'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'device_id': deviceId,
        'device_key': deviceKey,
        'fingerprint': fingerprint,
      }),
    );

    if (response.statusCode != 200) {
      throw NebulaCoreException(
        'Falha na autenticação (${response.statusCode}).',
        statusCode: response.statusCode,
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return data['access_token'] as String;
  }

  Future<String> startSession(String token) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/sessions'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 201) {
      throw NebulaCoreException(
        'Falha ao iniciar sessão (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return data['session_id'] as String;
  }

  Future<Provisioning> getProvisioning(String token) async {
    final response = await _client.get(
      Uri.parse('${ApiConfig.baseUrl}/me/provisioning'),
      headers: {'Authorization': 'Bearer $token'},
    );

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
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/sessions/$sessionId/heartbeat'),
      headers: {'Authorization': 'Bearer $token'},
    );

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
    final response = await _client.post(
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
    );

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
