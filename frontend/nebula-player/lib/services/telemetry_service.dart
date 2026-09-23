import '../api/nebula_core_client.dart';

/// Envia telemetria para o Nebula Core (alimenta o Nebula Monitor).
///
/// O envio é **fire-and-forget**: uma falha de telemetria nunca pode
/// atrapalhar a reprodução.
class TelemetryService {
  TelemetryService._();

  static final TelemetryService instance = TelemetryService._();

  final NebulaCoreClient _client = NebulaCoreClient();

  String? _token;
  String? _sessionId;

  bool get isReady => _token != null && _sessionId != null;

  String? get sessionId => _sessionId;

  /// Chamado após iniciar a sessão no boot.
  void configure({required String token, required String sessionId}) {
    _token = token;
    _sessionId = sessionId;
  }

  void reset() {
    _token = null;
    _sessionId = null;
  }

  /// Registra um evento (`playback_started`, `buffer_underrun`, ...).
  void track(String eventType, [Map<String, dynamic> payload = const {}]) {
    final token = _token;
    final sessionId = _sessionId;

    if (token == null || sessionId == null) {
      return;
    }

    _send(token, sessionId, eventType, payload);
  }

  Future<void> _send(
    String token,
    String sessionId,
    String eventType,
    Map<String, dynamic> payload,
  ) async {
    try {
      await _client.sendTelemetry(token, sessionId, eventType, payload);
    } catch (_) {
      // Telemetria é melhor esforço: nunca interrompe o app.
    }
  }
}
