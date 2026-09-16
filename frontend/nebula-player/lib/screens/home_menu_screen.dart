import 'package:flutter/material.dart';

import '../models/content_source.dart';
import '../services/playlist_selection_service.dart';
import '../theme/nebula_theme.dart';
import 'account_screen.dart';
import 'change_playlist_screen.dart';
import 'home_screen.dart';
import 'live_screen.dart';
import 'movies_screen.dart';
import 'series_screen.dart';
import 'settings_screen.dart';
import 'sources_screen.dart';

/// Menu inicial do Nebula Player.
class HomeMenuScreen extends StatefulWidget {
  const HomeMenuScreen({super.key, this.sources = const []});

  /// Listas provisionadas pelo Core (pode haver mais de uma).
  final List<ContentSource> sources;

  @override
  State<HomeMenuScreen> createState() => _HomeMenuScreenState();
}

class _HomeMenuScreenState extends State<HomeMenuScreen> {
  final PlaylistSelectionService _selection = PlaylistSelectionService();

  String? _selectedPlaylistId;

  @override
  void initState() {
    super.initState();
    _loadSelection();
  }

  Future<void> _loadSelection() async {
    final selected = await _selection.getSelectedPlaylistId();

    if (!mounted) return;

    setState(() => _selectedPlaylistId = selected);
  }

  /// Lista ativa: a escolhida pelo usuário (se ainda existir) ou a primeira.
  ContentSource? get _activeSource {
    if (widget.sources.isEmpty) {
      return null;
    }

    for (final source in widget.sources) {
      if (source.playlistId == _selectedPlaylistId) {
        return source;
      }
    }

    return widget.sources.first;
  }

  void _reload() {
    Navigator.of(context).pushAndRemoveUntil(
      MaterialPageRoute(builder: (_) => const HomeScreen()),
      (route) => false,
    );
  }

  Future<void> _openSources() async {
    final changed = await Navigator.of(context).push<bool>(
      MaterialPageRoute(
        builder: (_) => SourcesScreen(
          sources: widget.sources,
          selectedPlaylistId: _activeSource?.playlistId,
        ),
      ),
    );

    if (changed == true) {
      await _loadSelection();
    }
  }

  @override
  Widget build(BuildContext context) {
    final sourceUrl = _activeSource?.url;

    final items = <_MenuItem>[
      _MenuItem('Ao vivo', Icons.live_tv,
          builder: (_) => LiveScreen(sourceUrl: sourceUrl)),
      _MenuItem('Filmes', Icons.movie,
          builder: (_) => MoviesScreen(sourceUrl: sourceUrl)),
      _MenuItem('Séries', Icons.video_library,
          builder: (_) => SeriesScreen(sourceUrl: sourceUrl)),
      _MenuItem('Minhas listas', Icons.playlist_play, action: _openSources),
      _MenuItem('Conta', Icons.person,
          builder: (_) => const AccountScreen()),
      _MenuItem('Mudar lista', Icons.playlist_add,
          builder: (_) => const ChangePlaylistScreen()),
      _MenuItem('Configurações', Icons.settings_suggest,
          builder: (_) => const SettingsScreen()),
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
                      onPressed: _reload,
                    ),
                  ],
                ),
                const SizedBox(height: 4),
                Text(
                  _activeSource == null
                      ? 'Nenhuma lista provisionada'
                      : 'Lista: ${_activeSource!.displayName}',
                  style: const TextStyle(
                    color: NebulaColors.textSecondary,
                  ),
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
                        onTap: () {
                          final action = item.action;

                          if (action != null) {
                            action();
                            return;
                          }

                          Navigator.of(context).push(
                            MaterialPageRoute(
                              builder: (_) => item.builder!(sourceUrl),
                            ),
                          );
                        },
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
  const _MenuItem(
    this.label,
    this.icon, {
    this.builder,
    this.action,
  });

  final String label;
  final IconData icon;
  final Widget Function(String? sourceUrl)? builder;
  final Future<void> Function()? action;
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
