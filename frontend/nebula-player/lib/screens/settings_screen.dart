import 'package:flutter/material.dart';

import '../theme/nebula_theme.dart';

/// Tela "Configurações": lista de opções (maioria placeholders).
class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  static const _options = [
    'Mudar lista de reprodução',
    'Mudar idioma',
    'Mudar layout',
    'Ocultar categorias ao vivo',
    'Ocultar categorias VOD',
    'Apagar histórico de canais',
    'Formato de transmissão ao vivo',
    'Formato de hora',
    'Configurações de legenda',
    'Atualizar agora',
  ];

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(title: const Text('Configurações')),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: _options
              .map(
                (option) => Card(
                  color: NebulaColors.surface,
                  shape: RoundedRectangleBorder(
                    side: const BorderSide(color: NebulaColors.surfaceBorder),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: ListTile(
                    leading: const Icon(Icons.settings_suggest,
                        color: NebulaColors.textSecondary),
                    title: Text(
                      option,
                      style: const TextStyle(color: NebulaColors.textPrimary),
                    ),
                    trailing: const Icon(Icons.chevron_right,
                        color: NebulaColors.textSecondary),
                  ),
                ),
              )
              .toList(),
        ),
      ),
    );
  }
}
