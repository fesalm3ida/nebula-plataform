import 'package:http/http.dart' as http;

import '../m3u/m3u_parser.dart';
import '../models/m3u_channel.dart';

class PlaylistService {
  PlaylistService({http.Client? client}) : _client = client ?? http.Client();

  final http.Client _client;

  Future<List<M3uChannel>> loadChannels(String url) async {
    final response = await _client.get(Uri.parse(url));

    if (response.statusCode != 200) {
      throw Exception('Falha ao carregar lista (${response.statusCode})');
    }

    return M3uParser.parse(response.body);
  }
}
