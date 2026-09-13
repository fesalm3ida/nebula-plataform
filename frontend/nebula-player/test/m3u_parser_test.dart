import 'package:flutter_test/flutter_test.dart';

import 'package:nebula_player/m3u/m3u_parser.dart';
import 'package:nebula_player/models/media_kind.dart';

void main() {
  test('parses a simple M3U playlist', () {
    final content = [
      '#EXTM3U',
      '#EXTINF:-1 tvg-id="a" tvg-logo="http://logo.png" '
          'group-title="Esportes",Canal 1',
      'http://host/stream1.ts',
      '',
    ].join('\n');

    final channels = M3uParser.parse(content);

    expect(channels, hasLength(1));
    expect(channels.first.name, 'Canal 1');
    expect(channels.first.group, 'Esportes');
    expect(channels.first.logo, 'http://logo.png');
    expect(channels.first.streamUrl, 'http://host/stream1.ts');
  });

  test('handles EXTGRP and ignores empty/comment lines', () {
    final content = [
      '#EXTM3U',
      '#EXTGRP:Filmes',
      '#EXTINF:-1,Nome',
      'http://host/2.ts',
      '',
      '#EXTINF:-1,Outro',
      'http://host/3.ts',
    ].join('\n');

    final channels = M3uParser.parse(content);

    expect(channels, hasLength(2));
    expect(channels[0].group, 'Filmes');
    expect(channels[1].name, 'Outro');
  });

  test('returns empty when not a M3U playlist', () {
    expect(M3uParser.parse('not an m3u playlist'), isEmpty);
  });

  test('classifies live, movie and series entries by URL', () {
    final content = [
      '#EXTM3U',
      '#EXTINF:-1 group-title="Canais",Canal',
      'http://host:80/user/pass/1.ts',
      '#EXTINF:-1 group-title="Filmes",Filme (2026)',
      'http://host:80/movie/user/pass/2.mp4',
      '#EXTINF:-1 group-title="Series",Serie S01E02',
      'http://host:80/series/user/pass/3.mp4',
    ].join('\n');

    final items = M3uParser.parse(content);

    expect(items, hasLength(3));
    expect(items[0].kind, MediaKind.live);
    expect(items[1].kind, MediaKind.movie);
    expect(items[2].kind, MediaKind.series);
    expect(items[2].seriesName, 'Serie');
    expect(items[2].seasonEpisode, 'S01E02');
  });
}
