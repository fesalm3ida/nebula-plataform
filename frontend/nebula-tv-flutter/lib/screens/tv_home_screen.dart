import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/content_source.dart';
import '../models/m3u_channel.dart';
import '../models/media_kind.dart';
import '../models/series_group.dart';
import '../services/catalog_service.dart';
import '../services/playlist_selection_service.dart';
import '../utils/search.dart';
import 'tv_episodes_screen.dart';
import 'tv_player_screen.dart';

/// Menu da TV no padrao do Ibo Player:
/// categorias a esquerda, grade de capas a direita e filtro ao FOCAR a
/// categoria (sem precisar apertar OK).
class TvHomeScreen extends StatefulWidget {
  const TvHomeScreen({super.key, required this.sources});

  final List<ContentSource> sources;

  @override
  State<TvHomeScreen> createState() => _TvHomeScreenState();
}

class _TvHomeScreenState extends State<TvHomeScreen> {
  static const int gridColumns = 6;

  final CatalogService _catalog = CatalogService.instance;

  MediaKind _kind = MediaKind.movie;
  List<M3uChannel> _items = const [];
  List<SeriesGroup> _groups = const [];
  List<String> _categories = const [];
  String? _category;
  String _query = '';
  bool _loading = true;
  String? _error;

  ContentSource? _source;

  // navegacao: 0 = categorias, 1 = grade
  int _column = 0;
  int _row = 0;

  List<M3uChannel> get _filtered {
    final byCategory = _category == null
        ? _items
        : _items.where((item) => item.group == _category).toList();

    if (_query.trim().isEmpty) return byCategory;

    return byCategory
        .where((item) => matchesSearch(item.displayName, _query))
        .toList();
  }

  /// Series filtradas por categoria e busca (uma entrada por serie).
  List<SeriesGroup> get _filteredGroups {
    final byCategory = _category == null
        ? _groups
        : _groups.where((group) => group.category == _category).toList();

    if (_query.trim().isEmpty) return byCategory;

    return byCategory
        .where((group) => matchesSearch(group.name, _query))
        .toList();
  }

  bool get _isSeries => _kind == MediaKind.series;

  @override
  void initState() {
    super.initState();
    _resolveSource();
  }

  Future<void> _resolveSource() async {
    final selection = PlaylistSelectionService();
    final selected = await selection.getSelectedPlaylistId();

    ContentSource? source;

    for (final candidate in widget.sources) {
      if (candidate.playlistId == selected) source = candidate;
    }

    source ??= widget.sources.isEmpty ? null : widget.sources.first;

    if (!mounted) return;

    setState(() => _source = source);
    await _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
      _category = null;
      _column = 0;
      _row = 0;
    });

    try {
      final items = await _catalog.loadFor(_source?.url, _kind);

      if (!mounted) return;

      final groups = _kind == MediaKind.series
          ? SeriesGroup.from(items)
          : <SeriesGroup>[];

      setState(() {
        _items = items;
        _groups = groups;
        _categories = CatalogService.categoriesOf(items);
        _loading = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = '$error';
      });
    }
  }

  void _open(M3uChannel item) {
    final url = item.streamUrl;

    if (url == null || url.isEmpty) return;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => TvPlayerScreen(url: url, title: item.displayName),
      ),
    );
  }

  /// Move o foco (modelo de colunas: categorias + grade).
  void _move(String direction) {
    final items = _isSeries ? _filteredGroups : _filtered;
    final columns = _categories.length + 1;

    setState(() {
      if (direction == 'left' || direction == 'right') {
        final delta = direction == 'right' ? 1 : -1;

        if (_column == 1 && (direction == 'left' || direction == 'right')) {
          final next = _row + delta;

          if (next >= 0 && next < items.length && next < 240) {
            _row = next;
            return;
          }
        }

        _column = (_column + delta).clamp(0, 1);
        _row = 0;
        return;
      }

      final step = direction == 'down' ? 1 : -1;

      if (_column == 0) {
        final next = _row + step;

        if (next < 0) return;

        if (next >= columns) return;

        _row = next;

        // FILTRO AO FOCAR (padrao Ibo): a grade muda junto com o cursor.
        _category = next == 0 ? null : _categories[next - 1];
        return;
      }

      final next = _row + step * gridColumns;

      if (next >= 0 && next < items.length && next < 240) {
        _row = next;
      }
    });
  }

  void _activate() {
    if (_column == 0) {
      _column = 1;
      _row = 0;
      setState(() {});
      return;
    }

    if (_isSeries) {
      final groups = _filteredGroups;

      if (_row < groups.length) {
        Navigator.of(context).push(
          MaterialPageRoute(
            builder: (_) => TvEpisodesScreen(group: groups[_row]),
          ),
        );
      }

      return;
    }

    final items = _filtered;

    if (_row < items.length) {
      _open(items[_row]);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Focus(
        autofocus: true,
        onKeyEvent: (node, event) {
          if (event is! KeyDownEvent) return KeyEventResult.ignored;

          final key = event.logicalKey;

          if (key == LogicalKeyboardKey.arrowLeft) {
            _move('left');
            return KeyEventResult.handled;
          }
          if (key == LogicalKeyboardKey.arrowRight) {
            _move('right');
            return KeyEventResult.handled;
          }
          if (key == LogicalKeyboardKey.arrowUp) {
            _move('up');
            return KeyEventResult.handled;
          }
          if (key == LogicalKeyboardKey.arrowDown) {
            _move('down');
            return KeyEventResult.handled;
          }
          if (key == LogicalKeyboardKey.enter ||
              key == LogicalKeyboardKey.select) {
            _activate();
            return KeyEventResult.handled;
          }

          return KeyEventResult.ignored;
        },
        child: Column(
          children: [
            _TopBar(
              kind: _kind,
              category: _category,
              count: _isSeries ? _filteredGroups.length : _filtered.length,
              onKind: (kind) {
                _kind = kind;
                _load();
              },
              onSearch: (value) => setState(() => _query = value),
            ),
            Expanded(
              child: _loading
                  ? const Center(child: CircularProgressIndicator())
                  : _error != null
                      ? Center(
                          child: Text(
                            'Erro: $_error',
                            style: const TextStyle(fontSize: 24),
                          ),
                        )
                      : Row(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            SizedBox(
                              width: 380,
                              child: _CategoryColumn(
                                categories: _categories,
                                focusedIndex: _column == 0 ? _row : -1,
                                total: _items.length,
                              ),
                            ),
                            Expanded(
                              child: _isSeries
                                  ? _SeriesGrid(
                                      groups: _filteredGroups,
                                      focusedIndex: _column == 1 ? _row : -1,
                                      columns: gridColumns,
                                    )
                                  : _PosterGrid(
                                      items: _filtered,
                                      focusedIndex: _column == 1 ? _row : -1,
                                      columns: gridColumns,
                                    ),
                            ),
                          ],
                        ),
            ),
          ],
        ),
      ),
    );
  }
}

class _TopBar extends StatelessWidget {
  const _TopBar({
    required this.kind,
    required this.category,
    required this.count,
    required this.onKind,
    required this.onSearch,
  });

  final MediaKind kind;
  final String? category;
  final int count;
  final ValueChanged<MediaKind> onKind;
  final ValueChanged<String> onSearch;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(40, 28, 40, 12),
      child: Row(
        children: [
          const Text(
            'Nebula TV',
            style: TextStyle(fontSize: 34, fontWeight: FontWeight.bold),
          ),
          const SizedBox(width: 40),
          for (final entry in const [
            MapEntry(MediaKind.live, 'Ao vivo'),
            MapEntry(MediaKind.movie, 'Filmes'),
            MapEntry(MediaKind.series, 'Séries'),
          ])
            Padding(
              padding: const EdgeInsets.only(right: 14),
              child: ChoiceChip(
                label: Text(
                  entry.value,
                  style: const TextStyle(fontSize: 20),
                ),
                selected: kind == entry.key,
                onSelected: (_) => onKind(entry.key),
              ),
            ),
          const Spacer(),
          Text(
            '${category ?? 'Todas'} · $count itens',
            style: const TextStyle(fontSize: 20, color: Colors.white70),
          ),
        ],
      ),
    );
  }
}

class _CategoryColumn extends StatelessWidget {
  const _CategoryColumn({
    required this.categories,
    required this.focusedIndex,
    required this.total,
  });

  final List<String> categories;
  final int focusedIndex;
  final int total;

  @override
  Widget build(BuildContext context) {
    final entries = ['Todas ($total)', ...categories];

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 24),
      itemCount: entries.length,
      itemBuilder: (context, index) => Container(
        margin: const EdgeInsets.only(bottom: 6),
        padding: const EdgeInsets.symmetric(horizontal: 18, vertical: 14),
        decoration: BoxDecoration(
          color: index == focusedIndex
              ? const Color(0x668B3FFD)
              : Colors.white10,
          borderRadius: BorderRadius.circular(10),
          border: Border.all(
            color: index == focusedIndex
                ? const Color(0xFFB07BFF)
                : Colors.transparent,
            width: 2,
          ),
        ),
        child: Text(
          entries[index],
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
          style: TextStyle(
            fontSize: 22,
            fontWeight:
                index == focusedIndex ? FontWeight.bold : FontWeight.normal,
          ),
        ),
      ),
    );
  }
}

class _PosterGrid extends StatelessWidget {
  const _PosterGrid({
    required this.items,
    required this.focusedIndex,
    required this.columns,
  });

  final List<M3uChannel> items;
  final int focusedIndex;
  final int columns;

  @override
  Widget build(BuildContext context) {
    final visible = items.take(240).toList();

    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(4, 0, 40, 40),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columns,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 0.62,
      ),
      itemCount: visible.length,
      itemBuilder: (context, index) {
        final item = visible[index];
        final focused = index == focusedIndex;

        return Container(
          decoration: BoxDecoration(
            color: focused ? const Color(0x558B3FFD) : Colors.white10,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: focused ? const Color(0xFFB07BFF) : Colors.white12,
              width: focused ? 3 : 1,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(12),
                  ),
                  child: (item.logo?.isNotEmpty ?? false)
                      ? Image.network(
                          item.logo!,
                          fit: BoxFit.cover,
                          width: double.infinity,
                          errorBuilder: (_, _, _) => _Fallback(
                            label: item.displayName,
                          ),
                        )
                      : _Fallback(label: item.displayName),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(10),
                child: Text(
                  item.displayName,
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                  style: const TextStyle(fontSize: 18),
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

/// Grade de series: uma capa por serie, com a contagem de episodios.
class _SeriesGrid extends StatelessWidget {
  const _SeriesGrid({
    required this.groups,
    required this.focusedIndex,
    required this.columns,
  });

  final List<SeriesGroup> groups;
  final int focusedIndex;
  final int columns;

  @override
  Widget build(BuildContext context) {
    final visible = groups.take(300).toList();

    return GridView.builder(
      padding: const EdgeInsets.fromLTRB(4, 0, 40, 40),
      gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: columns,
        mainAxisSpacing: 16,
        crossAxisSpacing: 16,
        childAspectRatio: 0.60,
      ),
      itemCount: visible.length,
      itemBuilder: (context, index) {
        final group = visible[index];
        final focused = index == focusedIndex;

        return Container(
          decoration: BoxDecoration(
            color: focused ? const Color(0x558B3FFD) : Colors.white10,
            borderRadius: BorderRadius.circular(14),
            border: Border.all(
              color: focused ? const Color(0xFFB07BFF) : Colors.white12,
              width: focused ? 3 : 1,
            ),
          ),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Expanded(
                child: ClipRRect(
                  borderRadius: const BorderRadius.vertical(
                    top: Radius.circular(12),
                  ),
                  child: group.poster.isNotEmpty
                      ? Image.network(
                          group.poster,
                          fit: BoxFit.cover,
                          width: double.infinity,
                          errorBuilder: (_, _, _) =>
                              _Fallback(label: group.name),
                        )
                      : _Fallback(label: group.name),
                ),
              ),
              Padding(
                padding: const EdgeInsets.all(10),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      group.name,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                      style: const TextStyle(fontSize: 18),
                    ),
                    const SizedBox(height: 4),
                    Text(
                      group.episodes.length == 1
                          ? '1 episódio'
                          : '${group.episodes.length} episódios',
                      style: const TextStyle(
                        fontSize: 15,
                        color: Colors.white60,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        );
      },
    );
  }
}

class _Fallback extends StatelessWidget {
  const _Fallback({required this.label});

  final String label;

  @override
  Widget build(BuildContext context) {
    return Container(
      color: const Color(0xFF1B0B3A),
      alignment: Alignment.center,
      child: Text(
        label.isEmpty ? 'N' : label[0].toUpperCase(),
        style: const TextStyle(
          fontSize: 54,
          fontWeight: FontWeight.bold,
          color: Color(0xFFB07BFF),
        ),
      ),
    );
  }
}
