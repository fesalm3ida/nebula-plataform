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

  /// Verifica se a URL informada aponta para a rota secreta do administrador.
  ///
  /// Passe a URL capturada no início do app (`Uri.base.toString()`), antes de
  /// o roteador do Flutter normalizar o fragmento.
  static bool isAdminLocation(String location) =>
      location.contains(adminPath);

  /// Atalho usando a URL corrente do navegador.
  static bool get isAdminUrl => isAdminLocation(Uri.base.toString());

  /// URL que o administrador deve usar (para exibir/documentar).
  static String get adminUrl => '/#/$adminPath';
}
