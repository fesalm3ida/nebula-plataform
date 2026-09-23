import 'dart:convert';

import 'package:http/http.dart' as http;

import '../config/api_config.dart';
import '../models/auth_session.dart';
import '../models/device.dart';
import '../models/monitor.dart';
import '../models/playlist.dart';

class AdminApiClient {
  AdminApiClient({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<AuthSession> login(String email, String password) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/admin/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({'email': email, 'password': password}),
    );

    if (response.statusCode != 200) {
      throw AdminApiException(
        'Falha no login (${response.statusCode}).',
      );
    }

    return AuthSession.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  Future<List<Playlist>> listPlaylists(String token) async {
    final response = await _client.get(
      Uri.parse('${ApiConfig.baseUrl}/admin/playlists'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 200) {
      throw AdminApiException(
        'Falha ao listar playlists (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final list = data['playlists'] as List<dynamic>;

    return list
        .map((item) => Playlist.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  Future<Playlist> createPlaylist(
    String token,
    String name,
    String format,
    String sourceUrl,
  ) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/admin/playlists'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'name': name,
        'format': format,
        'source_url': sourceUrl,
      }),
    );

    if (response.statusCode != 201) {
      throw AdminApiException(
        'Falha ao criar playlist (${response.statusCode}).',
      );
    }

    return Playlist.fromJson(jsonDecode(response.body) as Map<String, dynamic>);
  }

  Future<List<Device>> listDevices(String token) async {
    final response = await _client.get(
      Uri.parse('${ApiConfig.baseUrl}/admin/devices'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 200) {
      throw AdminApiException(
        'Falha ao listar devices (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final list = data['devices'] as List<dynamic>;

    return list
        .map((item) => Device.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Aplica uma ação de ciclo de vida: activate, block ou revoke.
  Future<String> setDeviceStatus(
    String token,
    String deviceId,
    String action,
  ) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/admin/devices/$deviceId/$action'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 404) {
      throw AdminApiException('Device não encontrado.');
    }

    if (response.statusCode == 409) {
      throw AdminApiException(
        'Transição de status inválida para este device.',
      );
    }

    if (response.statusCode != 200) {
      throw AdminApiException(
        'Falha em "$action" (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return data['status'] as String;
  }

  /// Resumo do Nebula Monitor (telemetria + logs).
  Future<MonitorSummary> monitorSummary(String token, int hours) async {
    final response = await _client.get(
      Uri.parse('${ApiConfig.baseUrl}/admin/monitor/summary?hours=$hours'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 200) {
      throw AdminApiException(
        'Falha ao carregar o monitor (${response.statusCode}).',
      );
    }

    return MonitorSummary.fromJson(
      jsonDecode(response.body) as Map<String, dynamic>,
    );
  }

  /// Eventos de telemetria recentes.
  Future<List<TelemetryEvent>> listTelemetry(
    String token, {
    int hours = 24,
    int limit = 100,
    String? eventType,
  }) async {
    final filter = eventType == null ? '' : '&event_type=$eventType';

    final response = await _client.get(
      Uri.parse(
        '${ApiConfig.baseUrl}/admin/monitor/telemetry'
        '?hours=$hours&limit=$limit$filter',
      ),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 200) {
      throw AdminApiException(
        'Falha ao listar telemetria (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return (data['events'] as List<dynamic>)
        .map((item) => TelemetryEvent.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Logs técnicos recentes.
  Future<List<LogEntry>> listLogs(
    String token, {
    int hours = 24,
    int limit = 100,
    String? level,
  }) async {
    final filter = level == null ? '' : '&level=$level';

    final response = await _client.get(
      Uri.parse(
        '${ApiConfig.baseUrl}/admin/monitor/logs'
        '?hours=$hours&limit=$limit$filter',
      ),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode != 200) {
      throw AdminApiException(
        'Falha ao listar logs (${response.statusCode}).',
      );
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;

    return (data['logs'] as List<dynamic>)
        .map((item) => LogEntry.fromJson(item as Map<String, dynamic>))
        .toList();
  }

  /// Remove o aparelho do cadastro.
  ///
  /// O servidor recusa (409) quando existem pagamentos registrados.
  Future<void> deleteDevice(String token, String deviceId) async {
    final response = await _client.delete(
      Uri.parse('${ApiConfig.baseUrl}/admin/devices/$deviceId'),
      headers: {'Authorization': 'Bearer $token'},
    );

    if (response.statusCode == 409) {
      throw AdminApiException(
        'Este aparelho possui pagamentos registrados e não pode ser '
        'excluído. Use Bloquear ou Revogar.',
      );
    }

    if (response.statusCode != 204) {
      throw AdminApiException(
        'Falha ao remover o aparelho (${response.statusCode}).',
      );
    }
  }

  Future<void> assignPlaylist(
    String token,
    String deviceId,
    String playlistId,
  ) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/admin/playlists/assignments'),
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer $token',
      },
      body: jsonEncode({
        'device_id': deviceId,
        'playlist_id': playlistId,
      }),
    );

    if (response.statusCode == 409) {
      throw AdminApiException(
        'Este device já possui uma playlist associada.',
      );
    }

    if (response.statusCode == 404) {
      throw AdminApiException('Device ou playlist não encontrado.');
    }

    if (response.statusCode != 200 && response.statusCode != 201) {
      throw AdminApiException(
        'Falha ao associar playlist (${response.statusCode}).',
      );
    }
  }
}

class AdminApiException implements Exception {
  AdminApiException(this.message);

  final String message;

  @override
  String toString() => message;
}
