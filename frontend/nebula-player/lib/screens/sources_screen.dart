import 'package:flutter/material.dart';

import '../models/content_source.dart';
import '../services/playlist_selection_service.dart';
import '../theme/nebula_theme.dart';

/// "Minhas listas": escolhe qual playlist provisionada o app deve usar.
class SourcesScreen extends StatefulWidget {
  const SourcesScreen({
    super.key,
    required this.sources,
    this.selectedPlaylistId,
  });

  final List<ContentSource> sources;
  final String? selectedPlaylistId;

  @override
  State<SourcesScreen> createState() => _SourcesScreenState();
}

class _SourcesScreenState extends State<SourcesScreen> {
  final PlaylistSelectionService _selection = PlaylistSelectionService();

  String? _selected;

  @override
  void initState() {
    super.initState();
    _selected = widget.selectedPlaylistId;
  }

  Future<void> _select(ContentSource source) async {
    await _selection.select(source.playlistId);

    if (!mounted) return;

    setState(() => _selected = source.playlistId);
    Navigator.of(context).pop(true);
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(title: const Text('Minhas listas')),
        body: widget.sources.isEmpty
            ? const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Text(
                    'Nenhuma lista provisionada.\n'
                    'Ative o aparelho e cadastre uma lista no portal.',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: NebulaColors.textPrimary),
                  ),
                ),
              )
            : ListView.separated(
                itemCount: widget.sources.length,
                separatorBuilder: (_, __) => const Divider(height: 1),
                itemBuilder: (context, index) {
                  final source = widget.sources[index];
                  final isSelected = source.playlistId == _selected;

                  return ListTile(
                    leading: Icon(
                      isSelected
                          ? Icons.radio_button_checked
                          : Icons.radio_button_unchecked,
                      color: isSelected
                          ? NebulaColors.primary
                          : NebulaColors.textSecondary,
                    ),
                    title: Text(
                      source.displayName,
                      style: const TextStyle(
                        color: NebulaColors.textPrimary,
                      ),
                    ),
                    subtitle: Text(
                      source.url,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(
                        color: NebulaColors.textSecondary,
                        fontSize: 12,
                      ),
                    ),
                    onTap: () => _select(source),
                  );
                },
              ),
      ),
    );
  }
}
