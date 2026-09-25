import 'dart:convert';

import 'package:flutter/foundation.dart';
import 'package:http/http.dart' as http;

import '../m3u/m3u_parser.dart';
import '../models/m3u_channel.dart';

class PlaylistService {
  PlaylistService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<List<M3uChannel>> loadChannels(String url) async {
    final downloadWatch = Stopwatch()..start();
    final response = await _client.get(Uri.parse(url));
    downloadWatch.stop();

    if (response.statusCode != 200) {
      throw Exception('Falha ao carregar lista (${response.statusCode})');
    }

    // Muitos provedores nao informam charset no Content-Type; o http do Dart
    // assume latin-1 nesse caso, o que quebra acentos e emojis. Decodifica
    // explicitamente como UTF-8 (tolerando bytes invalidos).
    final content = utf8.decode(
      response.bodyBytes,
      allowMalformed: true,
    );

    final parseWatch = Stopwatch()..start();
    final items = M3uParser.parse(content);
    parseWatch.stop();

    final megabytes = response.bodyBytes.length / 1048576;

    debugPrint(
      '[Nebula] lista: download ${downloadWatch.elapsedMilliseconds} ms '
      '(${megabytes.toStringAsFixed(1)} MB) | '
      'parse ${parseWatch.elapsedMilliseconds} ms | '
      '${items.length} entradas',
    );

    return items;
  }
}
