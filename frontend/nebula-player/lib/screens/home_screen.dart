import 'package:flutter/material.dart';

import '../api/nebula_core_client.dart';
import '../models/device_identity.dart';
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

  Future<DeviceIdentity> _register(String fingerprint) async {
    final macAddress = await _identity.getOrCreateMacAddress();

    final identity = await _client.registerDevice(
      fingerprint: fingerprint,
      macAddress: macAddress,
      platform: 'android_tv',
      appVersion: '0.1.0',
    );
    await _identity.saveDeviceIdentity(
      deviceId: identity.deviceId,
      deviceKey: identity.deviceKey,
    );

    return identity;
  }

  Future<String> _ensureToken(String fingerprint) async {
    var deviceId = await _identity.getDeviceId();
    var deviceKey = await _identity.getDeviceKey();

    if (deviceId == null || deviceKey == null) {
      final identity = await _register(fingerprint);
      deviceId = identity.deviceId;
      deviceKey = identity.deviceKey;
    }

    try {
      return await _client.authenticateDevice(
        deviceId: deviceId,
        deviceKey: deviceKey,
        fingerprint: fingerprint,
      );
    } on NebulaCoreException catch (error) {
      // 401 = o Core nao reconhece mais este device (ex.: banco recriado).
      // Descarta a identidade local e registra novamente.
      if (error.statusCode != 401) rethrow;

      await _identity.clear();
      final identity = await _register(fingerprint);

      return _client.authenticateDevice(
        deviceId: identity.deviceId,
        deviceKey: identity.deviceKey,
        fingerprint: fingerprint,
      );
    }
  }

  Future<void> _start() async {
    setState(() => _status = 'Registrando dispositivo...');

    try {
      final fingerprint = await _identity.getOrCreateFingerprint();

      setState(() => _status = 'Autenticando...');
      final token = await _ensureToken(fingerprint);

      setState(() => _status = 'Iniciando sessão...');
      try {
        await _client.startSession(token);
      } on NebulaCoreException {
        // A sessao e necessaria apenas para heartbeat/telemetria; o menu
        // pode ser aberto mesmo assim.
      }

      setState(() => _status = 'Sincronizando (provisionamento)...');
      String? sourceUrl;
      try {
        final provisioning = await _client.getProvisioning(token);
        if (provisioning.contentEndpoints.isNotEmpty) {
          sourceUrl = provisioning.contentEndpoints.first.sourceUrl;
        }
      } on NebulaCoreException {
        // Sem lista provisionada: abre o menu; o usuario pode adicionar
        // uma lista local em "Mudar lista".
        sourceUrl = null;
      }

      if (!mounted) return;

      Navigator.of(context).pushReplacement(
        MaterialPageRoute(
          builder: (_) => HomeMenuScreen(channelsSourceUrl: sourceUrl),
        ),
      );
    } on NebulaCoreException catch (error) {
      if (!mounted) return;

      if (error.statusCode == 403) {
        setState(
          () => _status =
              'Dispositivo aguardando ativação pelo administrador.',
        );
        return;
      }

      setState(() => _status = 'Erro: $error');
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
