import 'package:flutter/material.dart';

import 'api/portal_api_client.dart';
import 'config/portal_config.dart';
import 'models/portal.dart';
import 'screens/login_screen.dart';
import 'screens/user_login_screen.dart';
import 'screens/user_portal_screen.dart';
import 'services/session_store.dart';

/// Portal web da Nebula.
///
/// - **Usuário**: acessa a raiz (`http://host:3000`) e entra com MAC Address
///   + código de ativação.
/// - **Administrador**: acessa a URL secreta (`.../#/<ADMIN_PATH>`), que só a
///   equipe conhece.
class NebulaAdminApp extends StatelessWidget {
  const NebulaAdminApp({super.key, this.initialLocation});

  /// URL do navegador capturada no `main()` (antes do roteamento do Flutter).
  final String? initialLocation;

  @override
  Widget build(BuildContext context) {
    final location = initialLocation ?? Uri.base.toString();
    final isAdmin = PortalConfig.isAdminLocation(location);

    return MaterialApp(
      title: isAdmin ? 'Nebula Admin' : 'Nebula Player',
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
      ),
      home: isAdmin ? const LoginScreen() : const _UserSessionGate(),
    );
  }
}

/// Retoma a sessão salva do usuário, quando existir.
///
/// O retorno do Mercado Pago (`back_url`) recarrega a página; sem restaurar a
/// sessão o usuário voltaria para a tela de login depois de pagar.
class _UserSessionGate extends StatefulWidget {
  const _UserSessionGate();

  @override
  State<_UserSessionGate> createState() => _UserSessionGateState();
}

class _UserSessionGateState extends State<_UserSessionGate> {
  final PortalApiClient _api = PortalApiClient();
  final SessionStore _store = SessionStore();

  bool _loading = true;
  PortalSession? _session;

  @override
  void initState() {
    super.initState();
    _restore();
  }

  Future<void> _restore() async {
    final stored = await _store.load();

    if (stored != null) {
      try {
        // Confirma que o token guardado ainda vale.
        await _api.device(stored.accessToken);

        if (!mounted) return;

        setState(() {
          _session = stored;
          _loading = false;
        });

        return;
      } catch (_) {
        await _store.clear();
      }
    }

    if (!mounted) return;

    setState(() => _loading = false);
  }

  @override
  Widget build(BuildContext context) {
    if (_loading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    final session = _session;

    if (session == null) {
      return const UserLoginScreen();
    }

    return UserPortalScreen(api: _api, session: session);
  }
}
