import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';

import 'screens/tv_boot_screen.dart';

/// Nebula TV — app de Smart TV em Flutter.
///
/// Mesma stack do Ibo Player Pro: Flutter + media_kit (libmpv), o que garante
/// decodificacao de MPEG-TS e HLS no proprio aparelho.
void main() {
  WidgetsFlutterBinding.ensureInitialized();
  MediaKit.ensureInitialized();

  runApp(const NebulaTvApp());
}

class NebulaTvApp extends StatelessWidget {
  const NebulaTvApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Nebula TV',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        colorSchemeSeed: const Color(0xFF8B3FFD),
        scaffoldBackgroundColor: const Color(0xFF0B0618),
        useMaterial3: true,
      ),
      home: const TvBootScreen(),
    );
  }
}
