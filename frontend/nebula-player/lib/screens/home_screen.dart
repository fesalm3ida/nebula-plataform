import 'package:flutter/material.dart';

import '../api/nebula_core_client.dart';
import '../services/device_identity_service.dart';
import '../theme/nebula_theme.dart';
import 'home_menu_screen.dart';

/// Tela de boot: executa o fluxo de inicialização (registro -> autenticação ->
/// sessão -> provisionamento) e navega para o [HomeMenuScreen] com a URL da
/// lista de reprodução provisionada.
class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final NebulaCoreClient _client = NebulaCoreClient();
  final DeviceIdentityService _identity = DeviceIdentityService();

  String _status = 'Inicializando...';

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
          macAddress: 'AA:BB:CC:DD:EE:FF',
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

      setState(() => _status = 'Iniciando sessão...');
      await _client.startSession(token);

      setState(() => _status = 'Sincronizando (provisionamento)...');
      final provisioning = await _client.getProvisioning(token);

      if (!mounted) return;

      final sourceUrl = provisioning.contentEndpoints.isNotEmpty
          ? provisioning.contentEndpoints.first.sourceUrl
          : null;

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => HomeMenuScreen(channelsSourceUrl: sourceUrl),
        ),
      );
    } catch (error) {
      if (!mounted) return;
      setState(() => _status = 'Erro: $error');
    }
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: Center(
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const CircularProgressIndicator(color: NebulaColors.textPrimary),
              const SizedBox(height: 16),
              Text(
                _status,
                style: const TextStyle(color: NebulaColors.textPrimary),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
