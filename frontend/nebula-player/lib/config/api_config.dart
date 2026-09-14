class ApiConfig {
  // Emulador Android acessa o host via 10.0.2.2. Em dispositivo físico use o IP da máquina.
  static const String baseUrl = String.fromEnvironment(
    'NEBULA_CORE_API',
    defaultValue: 'http://10.0.2.2:8000',
  );

  /// Portal web exibido na tela de ativação (o usuário entra com o MAC e o
  /// código de ativação).
  static const String portalUrl = String.fromEnvironment(
    'NEBULA_PORTAL_URL',
    defaultValue: 'http://localhost:3000',
  );
}
