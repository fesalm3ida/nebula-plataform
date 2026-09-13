import '../models/m3u_channel.dart';

/// Parser de playlists M3U (m3u_plus) do IPTV.
///
/// Lê `#EXTM3U`, `#EXTINF:-1 tvg-id="..." tvg-logo="..." group-title="Grupo",Nome`
/// (e `#EXTGRP:Grupo`) e a linha de URL que segue, produzindo [M3uChannel].
///
/// `#EXTGRP` define um grupo "sticky" aplicado às entradas seguintes; um
/// `group-title` no `#EXTINF` tem precedência sobre ele.
class M3uParser {
  static List<M3uChannel> parse(String content) {
    final channels = <M3uChannel>[];

    if (!content.trimLeft().toUpperCase().startsWith('#EXTM3U')) {
      return channels;
    }

    var index = 0;
    String? stickyGroup;
    String? currentName;
    String? currentGroup;
    String? currentLogo;

    for (final rawLine in content.split('\n')) {
      final line = rawLine.trim();

      if (line.isEmpty) {
        continue;
      }

      if (line.startsWith('#EXTINF')) {
        final attributeGroup = _attribute(line, 'group-title');
        currentGroup =
            (attributeGroup != null && attributeGroup.isNotEmpty)
                ? attributeGroup
                : stickyGroup;
        currentLogo = _attribute(line, 'tvg-logo');

        final comma = line.lastIndexOf(',');
        currentName = comma >= 0
            ? line.substring(comma + 1).trim()
            : (currentName ?? '');
      } else if (line.startsWith('#EXTGRP')) {
        stickyGroup = line.substring('#EXTGRP'.length).trim();
        currentGroup = stickyGroup;
      } else if (line.startsWith('#')) {
        continue;
      } else {
        final url = line;

        if (url.startsWith('http')) {
          channels.add(
            M3uChannel(
              name: (currentName?.isNotEmpty ?? false)
                  ? currentName!
                  : url,
              group: currentGroup,
              logo: currentLogo,
              streamUrl: url,
              originalIndex: index,
            ),
          );
          index++;
        }

        currentName = null;
        currentGroup = null;
        currentLogo = null;
      }
    }

    return channels;
  }

  static String? _attribute(String line, String key) {
    final match = RegExp('$key="([^"]*)"').firstMatch(line);
    return match?.group(1);
  }
}
