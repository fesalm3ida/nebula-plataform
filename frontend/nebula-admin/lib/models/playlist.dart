class Playlist {
  Playlist({
    required this.id,
    required this.name,
    required this.format,
    required this.sourceUrl,
    required this.status,
  });

  final String id;
  final String name;
  final String format;
  final String sourceUrl;
  final String status;

  factory Playlist.fromJson(Map<String, dynamic> json) => Playlist(
        id: json['playlist_id'] as String,
        name: json['name'] as String,
        format: json['format'] as String,
        sourceUrl: json['source_url'] as String,
        status: json['status'] as String,
      );
}
