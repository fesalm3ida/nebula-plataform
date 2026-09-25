import 'dart:math';

import 'package:shared_preferences/shared_preferences.dart';

class DeviceIdentityService {
  static const _fingerprintKey = 'nebula.device_fingerprint';
  static const _deviceIdKey = 'nebula.device_id';
  static const _deviceKeyKey = 'nebula.device_key';
  static const _macAddressKey = 'nebula.mac_address';
  static const _activationCodeKey = 'nebula.activation_code';

  /// MAC Address estável por instalação.
  ///
  /// O Android oculta o MAC real (Wi-Fi) desde o Android 6, então geramos um
  /// **pseudo-MAC localmente administrado** (`02:...`), único por instalação
  /// e persistido no dispositivo — é o identificador público do Device.
  Future<String> getOrCreateMacAddress() async {
    final prefs = await SharedPreferences.getInstance();
    final existing = prefs.getString(_macAddressKey);

    if (existing != null && existing.isNotEmpty) {
      return existing;
    }

    final macAddress = _generateMacAddress();
    await prefs.setString(_macAddressKey, macAddress);

    return macAddress;
  }

  String _generateMacAddress() {
    final random = Random.secure();

    // Primeiro octeto 0x02: localmente administrado e unicast.
    final octets = <int>[0x02, for (var index = 0; index < 5; index++) random.nextInt(256)];

    return octets
        .map((octet) => octet.toRadixString(16).padLeft(2, '0').toUpperCase())
        .join(':');
  }

  Future<String> getOrCreateFingerprint() async {
    final prefs = await SharedPreferences.getInstance();
    final existing = prefs.getString(_fingerprintKey);

    if (existing != null && existing.isNotEmpty) {
      return existing;
    }

    final fingerprint = _generateFingerprint();
    await prefs.setString(_fingerprintKey, fingerprint);

    return fingerprint;
  }

  Future<String?> getDeviceId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_deviceIdKey);
  }

  Future<String?> getDeviceKey() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_deviceKeyKey);
  }

  Future<void> saveDeviceIdentity({
    required String deviceId,
    required String deviceKey,
    String? activationCode,
    String? macAddress,
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_deviceIdKey, deviceId);
    await prefs.setString(_deviceKeyKey, deviceKey);

    if (activationCode != null && activationCode.isNotEmpty) {
      await prefs.setString(_activationCodeKey, activationCode);
    }

    if (macAddress != null && macAddress.isNotEmpty) {
      await prefs.setString(_macAddressKey, macAddress);
    }
  }

  Future<String?> getActivationCode() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_activationCodeKey);
  }

  /// Descarta a identidade local (device_id/device_key). Usado quando o Core
  /// não reconhece mais o device (ex.: banco recriado) para forçar um novo
  /// registro.
  Future<void> clear() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_deviceIdKey);
    await prefs.remove(_deviceKeyKey);
    await prefs.remove(_activationCodeKey);
  }

  String _generateFingerprint() {
    final random = Random.secure();

    return List.generate(
      64,
      (_) => random.nextInt(16).toRadixString(16),
    ).join();
  }
}
