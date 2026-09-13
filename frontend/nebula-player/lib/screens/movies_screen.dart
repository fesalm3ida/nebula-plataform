import 'package:flutter/material.dart';

import '../models/m3u_channel.dart';
import '../models/media_kind.dart';
import '../services/catalog_service.dart';
import '../theme/nebula_theme.dart';
import 'player_screen.dart';

/// Tela "Filmes" (VOD): grade de capas com filtro por categoria.
class MoviesScreen extends StatefulWidget {
  const MoviesScreen({super.key, this.sourceUrl});

  final String? sourceUrl;

  @override
  State<MoviesScreen> createState() => _MoviesScreenState();
}

class _MoviesScreenState extends State<MoviesScreen> {
  List<M3uChannel> _movies = [];
  List<String> _categories = [];
  String? _category;
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
      final movies = await CatalogService.instance.loadFor(
        widget.sourceUrl,
        MediaKind.movie,
      );

      watch.stop();

      if (!mounted) return;

      setState(() {
        _movies = movies;
        _categories = CatalogService.categoriesOf(movies);
        _loadMs = watch.elapsedMilliseconds;
        _loading = false;
        _empty = movies.isEmpty;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error.toString();
      });
    }
  }

  List<M3uChannel> get _filtered {
    if (_category == null) return _movies;
    return _movies.where((item) => item.group == _category).toList();
  }

  void _open(M3uChannel item) {
    final url = item.streamUrl;
    if (url == null || url.isEmpty) return;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => PlayerScreen(url: url, title: item.displayName),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(
          title: Text(
            _loadMs == null
                ? 'Filmes'
                : 'Filmes · ${_movies.length} · '
                    '${(_loadMs! / 1000).toStringAsFixed(1)}s',
          ),
        ),
        body: _loading
            ? const Center(child: CircularProgressIndicator())
            : _error != null
                ? _Message(text: _error!)
                : _empty
                    ? const _Message(
                        text: 'Nenhum filme disponível.\n'
                            'Adicione uma lista em "Mudar lista".',
                      )
                    : Column(
                        children: [
                          if (_categories.isNotEmpty)
                            _CategoryChips(
                              categories: _categories,
                              selected: _category,
                              onSelect: (value) =>
                                  setState(() => _category = value),
                            ),
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
                                final movie = _filtered[index];

                                return _PosterTile(
                                  title: movie.displayName,
                                  imageUrl: movie.logo,
                                  onTap: () => _open(movie),
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
  });

  final String title;
  final String? imageUrl;
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
      child: const Icon(Icons.movie, color: NebulaColors.textSecondary),
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
