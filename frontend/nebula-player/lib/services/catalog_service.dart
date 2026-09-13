import 'package:flutter/foundation.dart';

import '../models/m3u_channel.dart';
import '../models/media_kind.dart';
import 'local_playlist_service.dart';
import 'playlist_service.dart';

/// Carrega o catálogo (M3U) uma única vez e o mantém em cache, para que as
/// telas Ao vivo, Filmes e Séries compartilhem o mesmo download/parse.
class CatalogService {
  CatalogService._();

  static final CatalogService instance = CatalogService._();

  final PlaylistService _playlistService = PlaylistService();
  final LocalPlaylistService _localPlaylist = LocalPlaylistService();

  String? _cachedUrl;
  List<M3uChannel> _cached = [];

  /// Resolve a URL da lista (provisionada pelo Core ou local no dispositivo)
  /// e retorna as entradas do tipo informado.
  Future<List<M3uChannel>> loadFor(
    String? provisionedUrl,
    MediaKind kind,
  ) async {
    var url = provisionedUrl;

    if (url == null || url.isEmpty) {
      url = await _localPlaylist.getUrl();
    }

    if (url == null || url.isEmpty) {
      return [];
    }

    return _loadByKind(url, kind);
  }

  Future<List<M3uChannel>> _loadByKind(
    String url,
    MediaKind kind,
  ) async {
    if (_cachedUrl != url) {
      _cached = await _playlistService.loadChannels(url);
      _cachedUrl = url;
    } else {
      debugPrint(
        '[Nebula] catalogo: cache reutilizado (${_cached.length} entradas)',
      );
    }

    final filterWatch = Stopwatch()..start();
    final items = _cached.where((item) => item.kind == kind).toList();
    filterWatch.stop();

    debugPrint(
      '[Nebula] ${kind.name}: ${items.length} itens '
      '(filtro ${filterWatch.elapsedMilliseconds} ms)',
    );

    return items;
  }

  /// Categorias distintas (group-title) presentes em uma lista de itens.
  static List<String> categoriesOf(List<M3uChannel> items) {
    final categories = <String>[];

    for (final item in items) {
      final group = item.group;
      if (group != null && group.isNotEmpty && !categories.contains(group)) {
        categories.add(group);
      }
    }

    return categories..sort();
  }
}
