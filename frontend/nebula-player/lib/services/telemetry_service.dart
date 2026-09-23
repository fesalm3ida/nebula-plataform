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
  DateTime? _expiresAt;

  bool _renewing = false;

  bool get isReady => _token != null && _sessionId != null;

  String? get sessionId => _sessionId;

  /// Chamado após iniciar a sessão no boot.
  void configure({
    required String token,
    required String sessionId,
    DateTime? expiresAt,
  }) {
    _token = token;
    _sessionId = sessionId;
    _expiresAt = expiresAt;
  }

  bool get _isExpired {
    final expiresAt = _expiresAt;

    return expiresAt != null && DateTime.now().toUtc().isAfter(expiresAt);
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

  /// Abre uma nova sessão quando a atual expirou (a telemetria exige sessão
  /// ativa; a sessão dura ~30 min).
  Future<void> _renew(String token) async {
    if (_renewing) return;

    _renewing = true;

    try {
      final session = await _client.startSession(token);

      _sessionId = session.sessionId;
      _expiresAt = session.expiresAt;
    } catch (_) {
      // Sem sessão nova: a telemetria segue melhor esforço.
    } finally {
      _renewing = false;
    }
  }

  Future<void> _send(
    String token,
    String sessionId,
    String eventType,
    Map<String, dynamic> payload,
  ) async {
    try {
      if (_isExpired) {
        await _renew(token);

        final renewed = _sessionId;

        if (renewed == null) {
          return;
        }

        await _client.sendTelemetry(token, renewed, eventType, payload);

        return;
      }

      await _client.sendTelemetry(token, sessionId, eventType, payload);
    } catch (_) {
      // Telemetria é melhor esforço: nunca interrompe o app.
    }
  }
}
