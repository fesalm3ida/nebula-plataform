import 'package:flutter/material.dart';

import 'screens/home_screen.dart';

class NebulaPlayerApp extends StatelessWidget {
  const NebulaPlayerApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nebula Player',
      theme: ThemeData(
        colorSchemeSeed: Colors.teal,
        useMaterial3: true,
      ),
      home: const HomeScreen(),
    );
  }
}
