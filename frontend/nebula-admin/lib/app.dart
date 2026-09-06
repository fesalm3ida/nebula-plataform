import 'package:flutter/material.dart';

import 'screens/login_screen.dart';

class NebulaAdminApp extends StatelessWidget {
  const NebulaAdminApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nebula Admin',
      theme: ThemeData(
        colorSchemeSeed: Colors.indigo,
        useMaterial3: true,
      ),
      home: const LoginScreen(),
    );
  }
}
