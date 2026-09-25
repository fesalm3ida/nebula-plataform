import 'package:shared_preferences/shared_preferences.dart';

/// Lista de reprodução local (informada pelo usuário no dispositivo).
///
/// É uma alternativa pessoal usada quando o Core não provisiona uma lista
/// (as playlists gerenciadas pela plataforma continuam sendo cadastradas no
/// Nebula Admin, conforme a ADR-021).
class LocalPlaylistService {
  static const _urlKey = 'nebula.local_playlist_url';
  static const _nameKey = 'nebula.local_playlist_name';

  Future<String?> getUrl() async =>
      (await SharedPreferences.getInstance()).getString(_urlKey);

  Future<String?> getName() async =>
      (await SharedPreferences.getInstance()).getString(_nameKey);

  Future<void> save({required String name, required String url}) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_nameKey, name);
    await prefs.setString(_urlKey, url);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_nameKey);
    await prefs.remove(_urlKey);
  }
}
