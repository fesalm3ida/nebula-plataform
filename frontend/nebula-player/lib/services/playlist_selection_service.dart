import 'package:shared_preferences/shared_preferences.dart';

/// Guarda qual das listas provisionadas o usuário escolheu usar.
///
/// Um aparelho pode ter várias playlists (ex.: uma de canais e outra só de
/// filmes); o app usa a selecionada no Ao vivo, Filmes e Séries.
class PlaylistSelectionService {
  static const _selectedKey = 'nebula.selected_playlist_id';

  Future<String?> getSelectedPlaylistId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_selectedKey);
  }

  Future<void> select(String playlistId) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_selectedKey, playlistId);
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_selectedKey);
  }
}
