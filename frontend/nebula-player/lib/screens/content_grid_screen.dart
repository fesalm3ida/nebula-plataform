import 'package:flutter/material.dart';

import '../theme/nebula_theme.dart';

/// Grade de conteúdo (VOD/filmes/séries). Com o catálogo vazio, exibe um
/// placeholder; quando o catálogo for modelado, receberá os itens.
class ContentGridScreen extends StatelessWidget {
  const ContentGridScreen({super.key, required this.title, this.hint});

  final String title;
  final String? hint;

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(title: Text(title)),
        body: Center(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Text(
              hint ?? 'Sem conteúdo.',
              textAlign: TextAlign.center,
              style: const TextStyle(
                color: NebulaColors.textSecondary,
                fontSize: 16,
              ),
            ),
          ),
        ),
      ),
    );
  }
}
