import 'package:flutter/material.dart';

/// Paleta do Nebula Player: roxo + preto, texto branco, fundo em degrade
/// que termina em azul escuro celeste.
class NebulaColors {
  static const Color primary = Color(0xFF9C27B0);
  static const Color primaryDark = Color(0xFF5E0B8A);

  static const Color backgroundTop = Color(0xFF1A0B2E);
  static const Color backgroundMid = Color(0xFF3A0C6E);
  static const Color backgroundBottom = Color(0xFF0E2A5A);

  static const Color surface = Color(0x2EFFFFFF);
  static const Color surfaceBorder = Color(0x59FFFFFF);

  static const Color textPrimary = Colors.white;
  static const Color textSecondary = Colors.white70;
}

class NebulaTheme {
  static const LinearGradient backgroundGradient = LinearGradient(
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
    colors: [
      NebulaColors.backgroundBottom,
      NebulaColors.backgroundMid,
      NebulaColors.backgroundTop,
    ],
  );

  static ThemeData get theme => ThemeData(
        useMaterial3: true,
        brightness: Brightness.dark,
        colorScheme: ColorScheme.fromSeed(
          seedColor: NebulaColors.primary,
          brightness: Brightness.dark,
        ).copyWith(
          primary: NebulaColors.primary,
          surface: NebulaColors.backgroundTop,
        ),
        scaffoldBackgroundColor: Colors.transparent,
        textTheme: const TextTheme(
          bodyLarge: TextStyle(color: NebulaColors.textPrimary),
          bodyMedium: TextStyle(color: NebulaColors.textPrimary),
        ),
        appBarTheme: const AppBarTheme(
          backgroundColor: Colors.transparent,
          foregroundColor: NebulaColors.textPrimary,
          elevation: 0,
        ),
      );

  /// Envolve o conteúdo no degrade de fundo.
  static Widget background({required Widget child}) => DecoratedBox(
        decoration: const BoxDecoration(gradient: backgroundGradient),
        child: child,
      );
}
