class DeviceIdentity {
  const DeviceIdentity({
    required this.fingerprint,
    required this.deviceId,
    required this.deviceKey,
    this.activationCode = '',
    this.macAddress = '',
  });

  final String fingerprint;
  final String deviceId;
  final String deviceKey;

  /// Código curto (6 dígitos) exibido ao usuário para entrar no portal web.
  final String activationCode;

  /// MAC Address (identificador público do aparelho no portal).
  final String macAddress;
}
