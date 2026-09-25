/// Uma fonte de conteúdo provisionada pelo Core (Playlist).
class ContentSource {
  const ContentSource({
    required this.playlistId,
    required this.name,
    required this.url,
  });

  final String playlistId;
  final String name;
  final String url;

  String get displayName => name.isEmpty ? url : name;
}
