import 'package:flutter/material.dart';

import 'config/portal_config.dart';
import 'screens/login_screen.dart';
import 'screens/user_login_screen.dart';

/// Portal web da Nebula.
///
/// - **Usuário**: acessa a raiz (`http://host:3000`) e entra com MAC Address
///   + código de ativação.
/// - **Administrador**: acessa a URL secreta (`.../#/<ADMIN_PATH>`), que só a
///   equipe conhece.
class NebulaAdminApp extends StatelessWidget {
  const NebulaAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    final isAdmin = PortalConfig.isAdminUrl;

    return MaterialApp(
      title: isAdmin ? 'Nebula Admin' : 'Nebula Player',
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
      ),
      home: isAdmin ? const LoginScreen() : const UserLoginScreen(),
    );
  }
}
