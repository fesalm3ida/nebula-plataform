class PortalSession {
  PortalSession({
    required this.accessToken,
    required this.deviceId,
    required this.deviceStatus,
  });

  final String accessToken;
  final String deviceId;
  final String deviceStatus;

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
    required this.id,
    required this.name,
    required this.format,
    required this.sourceUrl,
    required this.status,
  });

  final String id;
  final String name;
  final String format;
  final String sourceUrl;
  final String status;

  factory PortalPlaylist.fromJson(Map<String, dynamic> json) => PortalPlaylist(
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
    required this.playlist,
  });

  final String deviceId;
  final PortalLicense license;
  final PortalPlaylist? playlist;

  factory PortalDevice.fromJson(Map<String, dynamic> json) => PortalDevice(
        deviceId: json['device_id'] as String,
        license: PortalLicense.fromJson(
          json['license'] as Map<String, dynamic>,
        ),
        playlist: json['playlist'] == null
            ? null
            : PortalPlaylist.fromJson(
                json['playlist'] as Map<String, dynamic>,
              ),
      );
}
