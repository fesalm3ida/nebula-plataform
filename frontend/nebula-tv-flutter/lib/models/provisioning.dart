class Provisioning {
  Provisioning({
    required this.deviceId,
    required this.deviceStatus,
    required this.contentEndpoints,
  });

  final String deviceId;
  final String deviceStatus;
  final List<ContentEndpoint> contentEndpoints;

  factory Provisioning.fromJson(Map<String, dynamic> json) => Provisioning(
        deviceId: json['device_id'] as String,
        deviceStatus: json['device_status'] as String,
        contentEndpoints: (json['content_endpoints'] as List<dynamic>)
            .map((item) =>
                ContentEndpoint.fromJson(item as Map<String, dynamic>))
            .toList(),
      );
}

class ContentEndpoint {
  ContentEndpoint({
    required this.playlistId,
    required this.name,
    required this.format,
    required this.sourceUrl,
    required this.status,
  });

  final String playlistId;
  final String name;
  final String format;
  final String sourceUrl;
  final String status;

  factory ContentEndpoint.fromJson(Map<String, dynamic> json) =>
      ContentEndpoint(
        playlistId: json['playlist_id'] as String,
        name: json['name'] as String,
        format: json['format'] as String,
        sourceUrl: json['source_url'] as String,
        status: json['status'] as String,
      );
}
