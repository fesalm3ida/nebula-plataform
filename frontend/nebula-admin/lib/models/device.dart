class Device {
  Device({
    required this.id,
    required this.platform,
    required this.status,
    required this.appVersion,
    required this.createdAt,
    this.macAddress = '',
    this.activationCode = '',
  });

  final String id;
  final String platform;
  final String status;
  final String appVersion;
  final String createdAt;

  /// Identificação exibida no Player (o usuário informa no portal).
  final String macAddress;
  final String activationCode;

  bool get isActive => status == 'active';
  bool get isPending => status == 'pending';

  factory Device.fromJson(Map<String, dynamic> json) => Device(
        id: json['device_id'] as String,
        platform: json['platform'] as String,
        status: json['status'] as String,
        appVersion: json['app_version'] as String,
        createdAt: json['created_at'] as String,
        macAddress: (json['mac_address'] as String?) ?? '',
        activationCode: (json['activation_code'] as String?) ?? '',
      );
}
