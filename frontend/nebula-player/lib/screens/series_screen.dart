import 'package:flutter/material.dart';

import '../models/m3u_channel.dart';
import '../models/media_kind.dart';
import '../services/catalog_service.dart';
import '../theme/nebula_theme.dart';
import 'player_screen.dart';
import '../widgets/title_search_field.dart';
import '../utils/search.dart';

/// Tela "Séries" (VOD): agrupa os episódios do M3U por série e mostra uma
/// grade de capas; ao abrir, lista os episódios.
class SeriesScreen extends StatefulWidget {
  const SeriesScreen({super.key, this.sourceUrl});

  final String? sourceUrl;

  @override
  State<SeriesScreen> createState() => _SeriesScreenState();
}

class _SeriesScreenState extends State<SeriesScreen> {
  List<_SeriesGroup> _series = [];
  List<String> _categories = [];
  String? _category;
  String _query = '';
  bool _loading = true;
  bool _empty = false;
  int? _loadMs;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    final watch = Stopwatch()..start();

    try {
      final episodes = await CatalogService.instance.loadFor(
        widget.sourceUrl,
        MediaKind.series,
      );

      final groups = <String, _SeriesGroup>{};

      for (final episode in episodes) {
        final name =
            episode.seriesName.isEmpty ? episode.displayName : episode.seriesName;

        final group = groups.putIfAbsent(name, () => _SeriesGroup(name: name));
        group.episodes.add(episode);
        group.category ??= episode.group;
        group.poster ??=
            (episode.logo?.isNotEmpty ?? false) ? episode.logo : null;
      }

      final list = groups.values.toList()
        ..sort((a, b) => a.name.toLowerCase().compareTo(b.name.toLowerCase()));

      final categories = <String>[];

      for (final group in list) {
        final category = group.category;
        if (category != null &&
            category.isNotEmpty &&
            !categories.contains(category)) {
          categories.add(category);
        }
      }

      categories.sort();
      watch.stop();

      if (!mounted) return;

      setState(() {
        _series = list;
        _categories = categories;
        _loadMs = watch.elapsedMilliseconds;
        _loading = false;
        _empty = list.isEmpty;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error.toString();
      });
    }
  }

  List<_SeriesGroup> get _filtered {
    final byCategory = _category == null
        ? _series
        : _series.where((group) => group.category == _category).toList();

    if (_query.trim().isEmpty) {
      return byCategory;
    }

    return byCategory
        .where((group) => matchesSearch(group.name, _query))
        .toList();
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          title: Text(
            _loadMs == null
                ? 'Séries'
                : 'Séries · ${_series.length} · '
                    '${(_loadMs! / 1000).toStringAsFixed(1)}s',
          ),
        ),
        body: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? _Message(text: _error!)
                : _empty
                    ? const _Message(
                        text: 'Nenhuma série disponível.\n'
                            'Adicione uma lista em "Mudar lista".',
                      )
                    : Column(
                        children: [
                          TitleSearchField(
                            onChanged: (value) =>
                                setState(() => _query = value),
                          ),
                          if (_categories.isNotEmpty)
                            _CategoryChips(
                              categories: _categories,
                              selected: _category,
                              onSelect: (value) =>
                                  setState(() => _category = value),
                            ),
                          if (_filtered.isEmpty)
                            const Expanded(
                              child: _Message(
                                text: 'Nenhum título encontrado.',
                              ),
                            )
                          else
                          Expanded(
                            child: GridView.builder(
                              padding: const EdgeInsets.all(12),
                              gridDelegate:
                                  const SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: 3,
                                mainAxisSpacing: 12,
                                crossAxisSpacing: 12,
                                childAspectRatio: 0.55,
                              ),
                              itemCount: _filtered.length,
                              itemBuilder: (context, index) {
                                final group = _filtered[index];

                                return _PosterTile(
                                  title: group.name,
                                  imageUrl: group.poster,
                                  subtitle: '${group.episodes.length} ep.',
                                  onTap: () => Navigator.of(context).push(
                                    MaterialPageRoute(
                                      builder: (_) =>
                                          _EpisodesScreen(group: group),
                                    ),
                                  ),
                                );
                              },
                            ),
                          ),
                        ],
                      ),
      ),
    );
  }
}

class _SeriesGroup {
  _SeriesGroup({required this.name});

  final String name;
  final List<M3uChannel> episodes = [];
  String? category;
  String? poster;
}

/// Lista de episódios de uma série.
class _EpisodesScreen extends StatelessWidget {
  const _EpisodesScreen({required this.group});

  final _SeriesGroup group;

  @override
  Widget build(BuildContext context) {
    final episodes = [...group.episodes]
      ..sort(
        (a, b) => a.seasonEpisode.compareTo(b.seasonEpisode),
      );

    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(title: Text(group.name)),
        body: ListView.builder(
          itemCount: episodes.length,
          itemBuilder: (context, index) {
            final episode = episodes[index];

            return ListTile(
              leading: (group.poster != null && group.poster!.isNotEmpty)
                  ? ClipRRect(
                      borderRadius: BorderRadius.circular(4),
                      child: Image.network(
                        group.poster!,
                        width: 36,
                        height: 52,
                        fit: BoxFit.cover,
                        errorBuilder: (_, __, ___) =>
                            const SizedBox(width: 36, height: 52),
                      ),
                    )
                  : null,
              title: Text(
                episode.displayName,
                style: const TextStyle(color: NebulaColors.textPrimary),
              ),
              subtitle: Text(
                episode.seasonEpisode,
                style: const TextStyle(color: NebulaColors.textSecondary),
              ),
              onTap: () {
                final url = episode.streamUrl;
                if (url == null || url.isEmpty) return;

                Navigator.of(context).push(
                  MaterialPageRoute(
                    builder: (_) => PlayerScreen(
                      url: url,
                      title: episode.displayName,
                    ),
                  ),
                );
              },
            );
          },
        ),
      ),
    );
  }
}

class _CategoryChips extends StatelessWidget {
  const _CategoryChips({
    required this.categories,
    required this.selected,
    required this.onSelect,
  });

  final List<String> categories;
  final String? selected;
  final ValueChanged<String?> onSelect;

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: 56,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: const EdgeInsets.symmetric(horizontal: 8),
        children: [
          Padding(
            padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
            child: ChoiceChip(
              label: const Text('Todas'),
              selected: selected == null,
              onSelected: (_) => onSelect(null),
            ),
          ),
          for (final category in categories)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 8),
              child: ChoiceChip(
                label: Text(category),
                selected: category == selected,
                onSelected: (_) => onSelect(category),
              ),
            ),
        ],
      ),
    );
  }
}

class _PosterTile extends StatelessWidget {
  const _PosterTile({
    required this.title,
    required this.imageUrl,
    required this.onTap,
    this.subtitle,
  });

  final String title;
  final String? imageUrl;
  final String? subtitle;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final hasImage = imageUrl != null && imageUrl!.isNotEmpty;

    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Expanded(
            child: ClipRRect(
              borderRadius: BorderRadius.circular(10),
              child: hasImage
                  ? Image.network(
                      imageUrl!,
                      fit: BoxFit.cover,
                      errorBuilder: (_, __, ___) => const _PosterFallback(),
                    )
                  : const _PosterFallback(),
            ),
          ),
          const SizedBox(height: 6),
          Text(
            title,
            maxLines: 2,
            overflow: TextOverflow.ellipsis,
            style: const TextStyle(
              color: NebulaColors.textPrimary,
              fontSize: 12,
            ),
          ),
          if (subtitle != null)
            Text(
              subtitle!,
              style: const TextStyle(
                color: NebulaColors.textSecondary,
                fontSize: 11,
              ),
            ),
        ],
      ),
    );
  }
}

class _PosterFallback extends StatelessWidget {
  const _PosterFallback();

  @override
  Widget build(BuildContext context) {
    return Container(
      color: NebulaColors.surface,
      alignment: Alignment.center,
      child: const Icon(Icons.video_library,
          color: NebulaColors.textSecondary),
    );
  }
}

class _Message extends StatelessWidget {
  const _Message({required this.text});

  final String text;

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Text(
          text,
          textAlign: TextAlign.center,
          style: const TextStyle(color: NebulaColors.textPrimary),
        ),
      ),
    );
  }
}
