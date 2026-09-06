class ApiConfig {
  static const String baseUrl = String.fromEnvironment(
    'NEBULA_ADMIN_API',
    defaultValue: 'http://localhost:8001',
  );
}
