/// Configuração do portal web.
///
/// O **usuário** acessa a raiz (`http://host:3000`); o **administrador** entra
/// por uma URL secreta (`http://host:3000/#/<ADMIN_PATH>`), desconhecida do
/// usuário.
class PortalConfig {
  static const String adminPath = String.fromEnvironment(
    'ADMIN_PATH',
    defaultValue: 'gestao-nebula-3f9c',
  );

  static const String apiBaseUrl = String.fromEnvironment(
    'NEBULA_ADMIN_API',
    defaultValue: 'http://localhost:8001',
  );

  /// Detecta se a URL atual é a rota secreta do administrador.
  static bool get isAdminUrl {
    final target = '${Uri.base.fragment} ${Uri.base.path}';

    return target.contains(adminPath);
  }

  /// URL que o administrador deve usar (para exibir/logar).
  static String get adminUrl => '/#/$adminPath';
}
