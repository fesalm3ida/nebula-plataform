import 'package:flutter/material.dart';

import 'screens/home_screen.dart';
import 'theme/nebula_theme.dart';

class NebulaPlayerApp extends StatelessWidget {
  const NebulaPlayerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nebula Player',
      theme: NebulaTheme.theme,
      home: const HomeScreen(),
    );
  }
}
