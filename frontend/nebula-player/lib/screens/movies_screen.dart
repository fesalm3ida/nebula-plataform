import 'package:flutter/material.dart';

import '../theme/nebula_theme.dart';
import 'content_grid_screen.dart';

/// Tela "Filmes" (VOD). O catálogo de filmes virá da API de conteúdo
/// (Xtream/player_api) — ainda não modelado. Por ora mostra o grid vazio.
class MoviesScreen extends StatelessWidget {
  const MoviesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return const ContentGridScreen(
      title: 'Filmes',
      hint: 'Catálogo de filmes em breve (VOD).',
    );
  }
}
