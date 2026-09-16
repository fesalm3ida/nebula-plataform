class PortalSession {
  PortalSession({
    required this.accessToken,
    required this.deviceId,
    required this.deviceStatus,
    this.macAddress = '',
  });

  final String accessToken;
  final String deviceId;
  final String deviceStatus;

  /// MAC Address informado no login (exibido no cabeçalho do portal).
  final String macAddress;

  PortalSession copyWith({String? macAddress}) => PortalSession(
        accessToken: accessToken,
        deviceId: deviceId,
        deviceStatus: deviceStatus,
        macAddress: macAddress ?? this.macAddress,
      );

  factory PortalSession.fromJson(Map<String, dynamic> json) => PortalSession(
        accessToken: json['access_token'] as String,
        deviceId: json['device_id'] as String,
        deviceStatus: json['device_status'] as String,
      );
}

class PortalLicense {
  PortalLicense({
    required this.status,
    required this.licenseType,
    required this.expiresAt,
    required this.daysRemaining,
    required this.expired,
  });

  final String status;
  final String? licenseType;
  final String? expiresAt;
  final int? daysRemaining;
  final bool expired;

  bool get isPending => status == 'pending';
  bool get isActive => status == 'active';
  bool get isTrial => licenseType == 'trial';
  bool get isLifetime => licenseType == 'lifetime';

  String get label {
    if (isPending) return 'Aguardando ativação';
    if (expired) return 'Licença expirada';
    if (isLifetime) return 'Licença vitalícia';
    if (isTrial) {
      return 'Teste grátis — ${daysRemaining ?? 0} dia(s) restante(s)';
    }
    return 'Licença ativa — ${daysRemaining ?? 0} dia(s) restante(s)';
  }

  factory PortalLicense.fromJson(Map<String, dynamic> json) => PortalLicense(
        status: json['status'] as String,
        licenseType: json['license_type'] as String?,
        expiresAt: json['expires_at'] as String?,
        daysRemaining: json['days_remaining'] as int?,
        expired: json['expired'] as bool,
      );
}

class PortalPlaylist {
  PortalPlaylist({
    required this.assignmentId,
    required this.id,
    required this.name,
    required this.format,
    required this.sourceUrl,
    required this.status,
  });

  /// Identificador da ASSOCIAÇÃO (usado para remover).
  final String assignmentId;

  final String id;
  final String name;
  final String format;
  final String sourceUrl;
  final String status;

  factory PortalPlaylist.fromJson(Map<String, dynamic> json) => PortalPlaylist(
        assignmentId: (json['assignment_id'] ?? json['playlist_id']) as String,
        id: json['playlist_id'] as String,
        name: json['name'] as String,
        format: json['format'] as String,
        sourceUrl: json['source_url'] as String,
        status: json['status'] as String,
      );
}

class PortalPlan {
  PortalPlan({
    required this.product,
    required this.title,
    required this.description,
    required this.priceCents,
    required this.priceLabel,
  });

  final String product;
  final String title;
  final String description;
  final int priceCents;
  final String priceLabel;

  factory PortalPlan.fromJson(Map<String, dynamic> json) => PortalPlan(
        product: json['product'] as String,
        title: json['title'] as String,
        description: json['description'] as String,
        priceCents: json['price_cents'] as int,
        priceLabel: json['price_label'] as String,
      );
}

class PortalDevice {
  PortalDevice({
    required this.deviceId,
    required this.license,
    required this.playlists,
  });

  final String deviceId;
  final PortalLicense license;

  /// Um aparelho pode ter uma ou várias listas.
  final List<PortalPlaylist> playlists;

  factory PortalDevice.fromJson(Map<String, dynamic> json) => PortalDevice(
        deviceId: json['device_id'] as String,
        license: PortalLicense.fromJson(
          json['license'] as Map<String, dynamic>,
        ),
        playlists: ((json['playlists'] as List<dynamic>?) ?? [])
            .map((item) => PortalPlaylist.fromJson(item as Map<String, dynamic>))
            .toList(),
      );
}
