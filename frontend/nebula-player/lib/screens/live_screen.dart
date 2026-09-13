import 'package:flutter/material.dart';

import '../models/m3u_channel.dart';
import '../models/media_kind.dart';
import '../player/media_kit_playback_controller.dart';
import '../player/playback_controller.dart';
import '../services/catalog_service.dart';
import '../services/local_playlist_service.dart';
import '../theme/nebula_theme.dart';
import 'change_playlist_screen.dart';
import 'player_screen.dart';

/// Tela "Ao vivo".
///
/// Em telas largas (paisagem): sidebar de grupos + lista de canais + preview.
/// Em telas estreitas (retrato): chips de grupos + lista de canais, e o canal
/// abre em um player de tela cheia.
class LiveScreen extends StatefulWidget {
  const LiveScreen({super.key, this.sourceUrl});

  final String? sourceUrl;

  @override
  State<LiveScreen> createState() => _LiveScreenState();
}

class _LiveScreenState extends State<LiveScreen> {
  static const double _wideBreakpoint = 720;

  final LocalPlaylistService _localPlaylist = LocalPlaylistService();
  final PlaybackController _controller = MediaKitPlaybackController();

  List<M3uChannel> _channels = [];
  List<String> _groups = [];
  String? _selectedGroup;
  M3uChannel? _selected;
  bool _loading = true;
  bool _noPlaylist = false;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  Future<void> _openChangePlaylist() async {
    final changed = await Navigator.of(context).push<bool>(
      MaterialPageRoute(builder: (_) => const ChangePlaylistScreen()),
    );

    if (changed == true) {
      setState(() => _loading = true);
      await _load();
    }
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _noPlaylist = false;
      _error = null;
    });

    var url = widget.sourceUrl;

    if (url == null || url.isEmpty) {
      url = await _localPlaylist.getUrl();
    }

    if (url == null || url.isEmpty) {
      setState(() {
        _loading = false;
        _noPlaylist = true;
      });
      return;
    }

    try {
      final channels = await CatalogService.instance.loadFor(
        url,
        MediaKind.live,
      );
      final groups = <String>[];

      for (final channel in channels) {
        final group = channel.group;
        if (group != null && group.isNotEmpty && !groups.contains(group)) {
          groups.add(group);
        }
      }

      setState(() {
        _channels = channels;
        _groups = groups;
        _loading = false;
      });
    } catch (error) {
      setState(() {
        _loading = false;
        _error = error.toString();
      });
    }
  }

  List<M3uChannel> get _filtered {
    if (_selectedGroup == null || _selectedGroup == 'Todos') {
      return _channels;
    }

    return _channels
        .where((channel) =>
            channel.group != null && channel.group == _selectedGroup)
        .toList();
  }

  void _playInline(M3uChannel channel) {
    setState(() => _selected = channel);

    final url = channel.streamUrl;
    if (url != null && url.isNotEmpty) {
      _controller.play(url);
    }
  }

  void _openFullscreen(M3uChannel channel) {
    final url = channel.streamUrl;
    if (url == null || url.isEmpty) return;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => PlayerScreen(url: url, title: channel.displayName),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          title: const Text('Ao vivo'),
          actions: [
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _load,
            ),
          ],
        ),
        body: _loading
            ? const Center(child: CircularProgressIndicator())
            : _noPlaylist
                ? _NoPlaylistPrompt(onAdd: _openChangePlaylist)
                : _error != null
                    ? Center(
                        child: Padding(
                          padding: const EdgeInsets.all(24),
                          child: Text(
                            _error!,
                            textAlign: TextAlign.center,
                            style: const TextStyle(
                              color: NebulaColors.textPrimary,
                            ),
                          ),
                        ),
                      )
                    : LayoutBuilder(
                        builder: (context, constraints) {
                          final isWide =
                              constraints.maxWidth >= _wideBreakpoint;

                          if (isWide) {
                            return _wideLayout();
                          }

                          return _narrowLayout();
                        },
                      ),
      ),
    );
  }

  Widget _wideLayout() {
    return Row(
      children: [
        SizedBox(
          width: 190,
          child: _GroupsSidebar(
            groups: _groups,
            selected: _selectedGroup ?? 'Todos',
            onSelect: (group) => setState(() => _selectedGroup = group),
          ),
        ),
        SizedBox(
          width: 230,
          child: _ChannelList(
            channels: _filtered,
            selected: _selected,
            onSelect: _playInline,
          ),
        ),
        Expanded(
          flex: 3,
          child: _Preview(controller: _controller, channel: _selected),
        ),
      ],
    );
  }

  Widget _narrowLayout() {
    return Column(
      children: [
        _GroupChips(
          groups: _groups,
          selected: _selectedGroup ?? 'Todos',
          onSelect: (group) => setState(() => _selectedGroup = group),
        ),
        Expanded(
          child: _ChannelList(
            channels: _filtered,
            onSelect: _openFullscreen,
          ),
        ),
      ],
    );
  }
}

class _GroupsSidebar extends StatelessWidget {
  const _GroupsSidebar({
    required this.groups,
    required this.selected,
    required this.onSelect,
  });

  final List<String> groups;
  final String selected;
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: NebulaColors.surface,
      child: ListView(
        children: [
          for (final group in ['Todos', ...groups])
            ListTile(
              selected: group == selected,
              selectedTileColor: NebulaColors.primaryDark,
              title: Text(
                group,
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
                style: const TextStyle(color: NebulaColors.textPrimary),
              ),
              onTap: () => onSelect(group),
            ),
        ],
      ),
    );
  }
}

class _GroupChips extends StatelessWidget {
  const _GroupChips({
    required this.groups,
    required this.selected,
    required this.onSelect,
  });

  final List<String> groups;
  final String selected;
  final ValueChanged<String> onSelect;

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 56,
      color: NebulaColors.surface,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        children: [
          for (final group in ['Todos', ...groups])
            Padding(
              padding: const EdgeInsets.symmetric(
                horizontal: 4,
                vertical: 8,
              ),
              child: ChoiceChip(
                label: Text(group),
                selected: group == selected,
                onSelected: (_) => onSelect(group),
              ),
            ),
        ],
      ),
    );
  }
}

class _ChannelList extends StatelessWidget {
  const _ChannelList({
    required this.channels,
    this.selected,
    required this.onSelect,
  });

  final List<M3uChannel> channels;
  final M3uChannel? selected;
  final ValueChanged<M3uChannel> onSelect;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black54,
      child: ListView.builder(
        itemCount: channels.length,
        itemBuilder: (context, index) {
          final channel = channels[index];
          final isSelected = identical(selected, channel);

          return InkWell(
            onTap: () => onSelect(channel),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
              color: isSelected ? NebulaColors.primaryDark : Colors.transparent,
              child: Row(
                children: [
                  if (channel.logo != null && channel.logo!.isNotEmpty)
                    ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: Image.network(
                        channel.logo!,
                        width: 32,
                        height: 24,
                        errorBuilder: (_, __, ___) =>
                            const SizedBox(width: 32, height: 24),
                      ),
                    )
                  else
                    const SizedBox(width: 32, height: 24),
                  const SizedBox(width: 8),
                  Expanded(
                    child: Text(
                      channel.displayName,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(color: NebulaColors.textPrimary),
                    ),
                  ),
                ],
              ),
            ),
          );
        },
      ),
    );
  }
}

class _Preview extends StatelessWidget {
  const _Preview({required this.controller, this.channel});

  final PlaybackController controller;
  final M3uChannel? channel;

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Expanded(child: controller.buildVideo()),
        if (channel != null)
          Container(
            width: double.infinity,
            color: Colors.black,
            padding: const EdgeInsets.all(16),
            child: Text(
              channel!.displayName,
              style: const TextStyle(
                color: NebulaColors.textPrimary,
                fontSize: 18,
              ),
            ),
          ),
      ],
    );
  }
}

/// Estado amigável quando não há lista disponível (sem mensagem de erro).
class _NoPlaylistPrompt extends StatelessWidget {
  const _NoPlaylistPrompt({required this.onAdd});

  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Icon(Icons.playlist_add,
                size: 56, color: NebulaColors.textSecondary),
            const SizedBox(height: 16),
            const Text(
              'Nenhuma lista de reprodução disponível.',
              textAlign: TextAlign.center,
              style: TextStyle(
                color: NebulaColors.textPrimary,
                fontSize: 18,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Adicione uma lista (M3U) para começar a assistir.',
              textAlign: TextAlign.center,
              style: TextStyle(color: NebulaColors.textSecondary),
            ),
            const SizedBox(height: 24),
            FilledButton.icon(
              onPressed: onAdd,
              icon: const Icon(Icons.add),
              label: const Text('Adicionar lista'),
            ),
          ],
        ),
      ),
    );
  }
}
