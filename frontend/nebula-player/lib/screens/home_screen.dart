import 'package:flutter/material.dart';

import '../api/nebula_core_client.dart';
import '../models/provisioning.dart';
import '../services/device_identity_service.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final NebulaCoreClient _client = NebulaCoreClient();
  final DeviceIdentityService _identity = DeviceIdentityService();

  String _status = 'Inicializando...';
  String? _sessionId;
  String? _token;
  Provisioning? _provisioning;

  @override
  void initState() {
    super.initState();
    _start();
  }

  Future<void> _start() async {
    setState(() => _status = 'Registrando dispositivo...');

    try {
      final fingerprint = await _identity.getOrCreateFingerprint();
      var deviceId = await _identity.getDeviceId();
      var deviceKey = await _identity.getDeviceKey();

      if (deviceId == null || deviceKey == null) {
        final identity = await _client.registerDevice(
          fingerprint: fingerprint,
          macAddress: 'AA:BB:CC:DD:EE:FF', // identificar no dispositivo real
          platform: 'android_tv',
          appVersion: '0.1.0',
        );
        await _identity.saveDeviceIdentity(
          deviceId: identity.deviceId,
          deviceKey: identity.deviceKey,
        );
        deviceId = identity.deviceId;
        deviceKey = identity.deviceKey;
      }

      setState(() => _status = 'Autenticando...');
      final token = await _client.authenticateDevice(
        deviceId: deviceId!,
        deviceKey: deviceKey!,
        fingerprint: fingerprint,
      );
      _token = token;

      setState(() => _status = 'Iniciando sessão...');
      final sessionId = await _client.startSession(token);
      _sessionId = sessionId;

      setState(() => _status = 'Sincronizando (provisionamento)...');
      final provisioning = await _client.getProvisioning(token);
      _provisioning = provisioning;

      setState(() => _status = 'Player pronto.');
    } catch (error) {
      if (!mounted) return;
      setState(() => _status = 'Erro: $error');
    }
  }

  Future<void> _heartbeat() async {
    try {
      await _client.heartbeat(_token!, _sessionId!);
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Heartbeat enviado.')),
      );
    } catch (_) {
      // ignore
    }
  }

  Future<void> _sendTelemetry() async {
    try {
      await _client.sendTelemetry(
        _token!,
        _sessionId!,
        'playback_started',
        {'duration_ms': 0},
      );
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Evento de telemetria enviado.')),
      );
    } catch (_) {
      // ignore
    }
  }

  @override
  Widget build(BuildContext context) {
    final endpoints = _provisioning?.contentEndpoints ?? [];

    return Scaffold(
      appBar: AppBar(title: const Text('Nebula Player')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              _status,
              style: Theme.of(context).textTheme.titleMedium,
            ),
            const SizedBox(height: 24),
            const Text('ContentEndpoints autorizados:'),
            ...endpoints.map(
              (endpoint) => ListTile(
                contentPadding: EdgeInsets.zero,
                title: Text(endpoint.name),
                subtitle: Text(endpoint.sourceUrl),
                trailing: Chip(label: Text(endpoint.format)),
              ),
            ),
            const SizedBox(height: 24),
            Row(
              children: [
                FilledButton(
                  onPressed: _token == null || _sessionId == null
                      ? null
                      : _heartbeat,
                  child: const Text('Heartbeat'),
                ),
                const SizedBox(width: 12),
                OutlinedButton(
                  onPressed: _token == null || _sessionId == null
                      ? null
                      : _sendTelemetry,
                  child: const Text('Telemetria'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
