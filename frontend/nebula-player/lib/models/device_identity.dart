class DeviceIdentity {
  const DeviceIdentity({
    required this.fingerprint,
    required this.deviceId,
    required this.deviceKey,
  });

  final String fingerprint;
  final String deviceId;
  final String deviceKey;
}
