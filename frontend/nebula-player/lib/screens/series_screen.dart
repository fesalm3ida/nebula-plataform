import 'package:flutter/material.dart';

import 'content_grid_screen.dart';

/// Tela "Séries" (VOD). O catálogo de séries virá da API de conteúdo
/// (Xtream/player_api) — ainda não modelado. Por ora mostra o grid vazio.
class SeriesScreen extends StatelessWidget {
  const SeriesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const ContentGridScreen(
      title: 'Séries',
      hint: 'Catálogo de séries em breve (VOD).',
    );
  }
}
