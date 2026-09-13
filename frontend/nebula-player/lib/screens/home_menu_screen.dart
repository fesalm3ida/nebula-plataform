import 'package:flutter/material.dart';

import '../theme/nebula_theme.dart';
import 'account_screen.dart';
import 'change_playlist_screen.dart';
import 'home_screen.dart';
import 'live_screen.dart';
import 'movies_screen.dart';
import 'series_screen.dart';
import 'settings_screen.dart';

/// Menu inicial do Nebula Player.
class HomeMenuScreen extends StatelessWidget {
  const HomeMenuScreen({super.key, this.channelsSourceUrl});

  final String? channelsSourceUrl;

  void _reload(BuildContext context) {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const HomeScreen()),
      (route) => false,
    );
  }

  @override
  Widget build(BuildContext context) {
    final items = <_MenuItem>[
      _MenuItem('Ao vivo', Icons.live_tv,
          (sourceUrl) => LiveScreen(sourceUrl: sourceUrl)),
      _MenuItem('Filmes', Icons.movie, (_) => const MoviesScreen()),
      _MenuItem('Séries', Icons.video_library, (_) => const SeriesScreen()),
      _MenuItem('Conta', Icons.person, (_) => const AccountScreen()),
      _MenuItem('Mudar lista', Icons.playlist_add,
          (_) => const ChangePlaylistScreen()),
      _MenuItem('Configurações', Icons.settings_suggest,
          (_) => const SettingsScreen()),
    ];

    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        body: SafeArea(
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  children: [
                    const Expanded(
                      child: Text(
                        'Nebula Player',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.bold,
                          color: NebulaColors.textPrimary,
                        ),
                      ),
                    ),
                    IconButton(
                      tooltip: 'Recarregar',
                      icon: const Icon(Icons.refresh,
                          color: NebulaColors.textPrimary),
                      onPressed: () => _reload(context),
                    ),
                  ],
                ),
                const SizedBox(height: 16),
                Expanded(
                  child: GridView.builder(
                    gridDelegate:
                        const SliverGridDelegateWithFixedCrossAxisCount(
                      crossAxisCount: 2,
                      mainAxisSpacing: 16,
                      crossAxisSpacing: 16,
                      mainAxisExtent: 130,
                    ),
                    itemCount: items.length,
                    itemBuilder: (context, index) {
                      final item = items[index];

                      return _MenuTile(
                        item: item,
                        onTap: () => Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => item.builder(channelsSourceUrl),
                          ),
                        ),
                      );
                    },
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _MenuItem {
  const _MenuItem(this.label, this.icon, this.builder);

  final String label;
  final IconData icon;
  final Widget Function(String? sourceUrl) builder;
}

class _MenuTile extends StatelessWidget {
  const _MenuTile({required this.item, required this.onTap});

  final _MenuItem item;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: NebulaColors.surface,
      shape: RoundedRectangleBorder(
        side: const BorderSide(color: NebulaColors.surfaceBorder),
        borderRadius: BorderRadius.circular(16),
      ),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(16),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(item.icon, size: 38, color: NebulaColors.textPrimary),
              const SizedBox(height: 8),
              Text(
                item.label,
                maxLines: 1,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(
                  color: NebulaColors.textPrimary,
                  fontSize: 16,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
