import 'dart:async';

import 'package:flutter/material.dart';

import '../api/nebula_core_client.dart';
import '../models/content_source.dart';
import '../services/telemetry_service.dart';
import '../theme/nebula_theme.dart';
import 'home_menu_screen.dart';

/// Tela inicial do Player: exibe **MAC Address** e **código de ativação**.
///
/// O usuário usa esses dados no portal web para ativar o aparelho e cadastrar
/// a lista. O app verifica periodicamente e, assim que o aparelho estiver
/// ativo, segue para o menu automaticamente.
class ActivationScreen extends StatefulWidget {
  const ActivationScreen({
    super.key,
    required this.deviceId,
    required this.deviceKey,
    required this.fingerprint,
    required this.macAddress,
    required this.activationCode,
  });

  final String deviceId;
  final String deviceKey;
  final String fingerprint;
  final String macAddress;
  final String activationCode;

  @override
  State<ActivationScreen> createState() => _ActivationScreenState();
}

class _ActivationScreenState extends State<ActivationScreen> {
  static const Duration _checkInterval = Duration(seconds: 10);

  final NebulaCoreClient _client = NebulaCoreClient();

  Timer? _timer;
  bool _checking = false;
  String _status = 'Aguardando ativação no portal...';

  @override
  void initState() {
    super.initState();
    _timer = Timer.periodic(_checkInterval, (_) => _check());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _check() async {
    if (_checking) return;

    setState(() => _checking = true);

    try {
      final token = await _client.authenticateDevice(
        deviceId: widget.deviceId,
        deviceKey: widget.deviceKey,
        fingerprint: widget.fingerprint,
      );

      final session = await _client.startSession(token);

      // Habilita a telemetria também neste caminho (ativação -> menu).
      TelemetryService.instance.configure(
        token: token,
        sessionId: session.sessionId,
        expiresAt: session.expiresAt,
      );

      var sources = <ContentSource>[];

      try {
        final provisioning = await _client.getProvisioning(token);
        sources = provisioning.contentEndpoints
            .map(
              (endpoint) => ContentSource(
                playlistId: endpoint.playlistId,
                name: endpoint.name,
                url: endpoint.sourceUrl,
              ),
            )
            .toList();
      } on NebulaCoreException {
        sources = <ContentSource>[];
      }

      _timer?.cancel();

      if (!mounted) return;

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => HomeMenuScreen(sources: sources),
        ),
      );
    } on NebulaCoreException catch (error) {
      if (!mounted) return;

      setState(() {
        _status = error.statusCode == 403
            ? 'Aguardando ativação no portal...'
            : 'Não foi possível verificar ($error)';
        _checking = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _status = 'Não foi possível verificar ($error)';
        _checking = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: Center(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24),
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  const Text(
                    'Nebula Player',
                    style: TextStyle(
                      fontSize: 30,
                      fontWeight: FontWeight.bold,
                      color: NebulaColors.textPrimary,
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Ative seu aparelho para começar',
                    style: TextStyle(color: NebulaColors.textSecondary),
                  ),
                  const SizedBox(height: 24),
                  _DataCard(
                    label: 'MAC Address',
                    value: widget.macAddress,
                  ),
                  const SizedBox(height: 12),
                  _DataCard(
                    label: 'Código de ativação',
                    value: widget.activationCode,
                    highlight: true,
                  ),
                  const SizedBox(height: 24),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      if (_checking)
                        const Padding(
                          padding: EdgeInsets.only(right: 12),
                          child: SizedBox(
                            height: 18,
                            width: 18,
                            child: CircularProgressIndicator(strokeWidth: 2),
                          ),
                        ),
                      Flexible(
                        child: Text(
                          _status,
                          textAlign: TextAlign.center,
                          style: const TextStyle(
                            color: NebulaColors.textPrimary,
                          ),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  FilledButton.icon(
                    onPressed: _checking ? null : _check,
                    icon: const Icon(Icons.refresh),
                    label: const Text('Verificar agora'),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _DataCard extends StatelessWidget {
  const _DataCard({
    required this.label,
    required this.value,
    this.highlight = false,
  });

  final String label;
  final String value;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: NebulaColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(
          color: highlight
              ? NebulaColors.primary
              : NebulaColors.surfaceBorder,
        ),
      ),
      child: Column(
        children: [
          Text(
            label,
            style: const TextStyle(
              color: NebulaColors.textSecondary,
              fontSize: 12,
            ),
          ),
          const SizedBox(height: 4),
          SelectableText(
            value.isEmpty ? '—' : value,
            textAlign: TextAlign.center,
            style: TextStyle(
              color: NebulaColors.textPrimary,
              fontSize: highlight ? 32 : 20,
              fontWeight: FontWeight.bold,
              letterSpacing: highlight ? 6 : 1,
            ),
          ),
        ],
      ),
    );
  }
}
