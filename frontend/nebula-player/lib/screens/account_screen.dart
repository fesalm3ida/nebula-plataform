import 'package:flutter/material.dart';

import '../theme/nebula_theme.dart';

/// Tela "Conta": mostra os dados da conta/lista (sem dados sensíveis).
class AccountScreen extends StatelessWidget {
  const AccountScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final rows = [
      ('Status da conta', 'Activated'),
      ('Data de expiração', '—'),
      ('Expiração da lista', '—'),
      ('Endereço de MAC', '—'),
      ('Chave do dispositivo', '—'),
    ];

    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(title: const Text('Conta')),
        body: ListView(
          padding: const EdgeInsets.all(16),
          children: rows
              .map(
                (row) => Card(
                  color: NebulaColors.surface,
                  shape: RoundedRectangleBorder(
                    side: const BorderSide(color: NebulaColors.surfaceBorder),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: ListTile(
                    title: Text(
                      row.$1,
                      style: const TextStyle(color: NebulaColors.textSecondary),
                    ),
                    trailing: Text(
                      row.$2,
                      style: const TextStyle(color: NebulaColors.textPrimary),
                    ),
                  ),
                ),
              )
              .toList(),
        ),
      ),
    );
  }
}
