import 'm3u_channel.dart';

/// Uma serie com seus episodios agrupados (uma capa por serie, como o Ibo).
class SeriesGroup {
  SeriesGroup(this.name);

  final String name;

  String poster = '';
  String category = '';
  final List<M3uChannel> episodes = [];

  /// Agrupa episodios por serie, ordenando por temporada/episodio.
  static List<SeriesGroup> from(List<M3uChannel> items) {
    final map = <String, SeriesGroup>{};

    for (final item in items) {
      final name = item.seriesName.isEmpty ? item.displayName : item.seriesName;
      final group = map.putIfAbsent(name.toLowerCase(), () => SeriesGroup(name));

      group.episodes.add(item);

      final logo = item.logo;

      if (group.poster.isEmpty && logo != null && logo.isNotEmpty) {
        group.poster = logo;
      }

      final category = item.group;

      if (group.category.isEmpty && category != null && category.isNotEmpty) {
        group.category = category;
      }
    }

    final groups = map.values.toList();

    for (final group in groups) {
      group.episodes.sort(
        (a, b) => a.seasonEpisode.compareTo(b.seasonEpisode),
      );
    }

    return groups;
  }
}
