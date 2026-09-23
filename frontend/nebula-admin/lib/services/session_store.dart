import 'package:shared_preferences/shared_preferences.dart';

import '../models/portal.dart';

/// Guarda a sessão do portal do usuário no dispositivo.
///
/// No web o `shared_preferences` usa o `localStorage`, então a sessão
/// sobrevive a um recarregamento da página — necessário porque o retorno do
/// Mercado Pago (`back_url`) recarrega o portal e, sem isso, o usuário caía
/// na tela de login.
class SessionStore {
  static const _tokenKey = 'nebula.portal.access_token';
  static const _macKey = 'nebula.portal.mac_address';
  static const _deviceIdKey = 'nebula.portal.device_id';

  Future<void> save(PortalSession session) async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.setString(_tokenKey, session.accessToken);
    await prefs.setString(_macKey, session.macAddress);
    await prefs.setString(_deviceIdKey, session.deviceId);
  }

  Future<PortalSession?> load() async {
    final prefs = await SharedPreferences.getInstance();

    final token = prefs.getString(_tokenKey);

    if (token == null || token.isEmpty) {
      return null;
    }

    return PortalSession(
      accessToken: token,
      deviceId: prefs.getString(_deviceIdKey) ?? '',
      deviceStatus: '',
      macAddress: prefs.getString(_macKey) ?? '',
    );
  }

  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();

    await prefs.remove(_tokenKey);
    await prefs.remove(_macKey);
    await prefs.remove(_deviceIdKey);
  }
}
