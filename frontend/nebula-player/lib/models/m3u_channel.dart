import 'media_kind.dart';

class M3uChannel {
  const M3uChannel({
    required this.name,
    this.group,
    this.logo,
    this.streamUrl,
    this.originalIndex = 0,
    this.kind = MediaKind.live,
  });

  final String name;
  final String? group;
  final String? logo;
  final String? streamUrl;
  final int originalIndex;
  final MediaKind kind;

  String get displayName => name.isEmpty ? (streamUrl ?? 'Canal') : name;

  /// Nome da série sem o sufixo de temporada/episódio (ex.: "Série S01E02").
  String get seriesName =>
      displayName.replaceAll(RegExp(r'\s+S\d+\s*E\d+.*$'), '').trim();

  /// Temporada/episódio quando presente no nome (ex.: S01E02).
  String get seasonEpisode {
    final match = RegExp(r'(S\d+\s*E\d+)').firstMatch(displayName);
    return match?.group(1) ?? '';
  }
}
