import 'package:flutter/material.dart';

import '../api/nebula_core_client.dart';
import '../models/content_source.dart';
import '../services/device_identity_service.dart';
import '../services/telemetry_service.dart';
import 'tv_activation_screen.dart';
import 'tv_home_screen.dart';

/// Boot do app: registra/autentica o aparelho, abre sessao e busca as listas.
class TvBootScreen extends StatefulWidget {
  const TvBootScreen({super.key});

  @override
  State<TvBootScreen> createState() => _TvBootScreenState();
}

class _TvBootScreenState extends State<TvBootScreen> {
  final DeviceIdentityService _identity = DeviceIdentityService();
  final NebulaCoreClient _client = NebulaCoreClient();

  String _status = 'Inicializando…';
  bool _failed = false;

  @override
  void initState() {
    super.initState();
    _boot();
  }

  Future<void> _boot() async {
    setState(() {
      _failed = false;
      _status = 'Conectando ao Nebula…';
    });

    try {
      final mac = await _identity.getOrCreateMacAddress();
      final fingerprint = await _identity.getOrCreateFingerprint();
      var deviceId = await _identity.getDeviceId();
      var deviceKey = await _identity.getDeviceKey();

      if (deviceId == null || deviceKey == null) {
        final registered = await _client.registerDevice(
          fingerprint: fingerprint,
          macAddress: mac,
          platform: 'android_tv',
          appVersion: '0.1.0',
        );

        deviceId = registered.deviceId;
        deviceKey = registered.deviceKey;

        await _identity.saveDeviceIdentity(
          deviceId: registered.deviceId,
          deviceKey: registered.deviceKey,
          activationCode: registered.activationCode,
        );
      }

      setState(() => _status = 'Autenticando…');

      final token = await _client.authenticateDevice(
        deviceId: deviceId,
        deviceKey: deviceKey,
        fingerprint: fingerprint,
      );

      try {
        final session = await _client.startSession(token);

        TelemetryService.instance.configure(
          token: token,
          sessionId: session.sessionId,
          expiresAt: session.expiresAt,
        );
      } catch (_) {
        // Sessao e opcional (telemetria).
      }

      setState(() => _status = 'Carregando listas…');

      final provisioning = await _client.getProvisioning(token);
      final sources = provisioning.contentEndpoints
          .map(
            (endpoint) => ContentSource(
              playlistId: endpoint.playlistId,
              name: endpoint.name,
              url: endpoint.sourceUrl,
            ),
          )
          .toList();

      if (!mounted) return;

      if (sources.isEmpty) {
        _openActivation(
          'Nenhuma lista cadastrada. Ative o aparelho no portal e cadastre sua lista.',
        );
        return;
      }

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => TvHomeScreen(sources: sources),
        ),
      );
    } on NebulaCoreException catch (error) {
      if (!mounted) return;

      if (error.statusCode == 403) {
        _openActivation('');
        return;
      }

      if (error.statusCode == 404) {
        _openActivation(
          'Nenhuma lista cadastrada para este aparelho. Cadastre uma lista no portal.',
        );
        return;
      }

      setState(() {
        _failed = true;
        _status = '$error';
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _failed = true;
        _status = '$error';
      });
    }
  }

  Future<void> _openActivation(String message) async {
    final mac = await _identity.getOrCreateMacAddress();
    final code = await _identity.getActivationCode();

    if (!mounted) return;

    Navigator.of(context).pushReplacement(
      MaterialPageRoute(
        builder: (_) => TvActivationScreen(
          macAddress: mac,
          activationCode: code ?? '',
          message: message,
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (_failed)
              const Icon(Icons.cloud_off, size: 72, color: Colors.white70)
            else
              const CircularProgressIndicator(),
            const SizedBox(height: 28),
            Text(
              _status,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 26),
            ),
            if (_failed) ...[
              const SizedBox(height: 28),
              FilledButton(
                autofocus: true,
                onPressed: _boot,
                child: const Text('Tentar novamente'),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
