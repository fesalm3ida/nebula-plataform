import 'dart:math';

import 'package:shared_preferences/shared_preferences.dart';

class DeviceIdentityService {
  static const _fingerprintKey = 'nebula.device_fingerprint';
  static const _deviceIdKey = 'nebula.device_id';
  static const _deviceKeyKey = 'nebula.device_key';

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
  }) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_deviceIdKey, deviceId);
    await prefs.setString(_deviceKeyKey, deviceKey);
  }

  String _generateFingerprint() {
    final random = Random.secure();

    return List.generate(
      64,
      (_) => random.nextInt(16).toRadixString(16),
    ).join();
  }
}
