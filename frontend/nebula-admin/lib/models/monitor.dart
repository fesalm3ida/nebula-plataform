// Modelos do Nebula Monitor (telemetria e logs).

class MonitorHourlyPoint {
  MonitorHourlyPoint({required this.hour, required this.count});

  final DateTime hour;
  final int count;

  factory MonitorHourlyPoint.fromJson(Map<String, dynamic> json) =>
      MonitorHourlyPoint(
        hour: DateTime.parse(json['hour'] as String).toLocal(),
        count: json['count'] as int,
      );
}

class MonitorSummary {
  MonitorSummary({
    required this.since,
    required this.totalEvents,
    required this.eventsByType,
    required this.eventsPerHour,
    required this.totalLogs,
    required this.logsByLevel,
  });

  final DateTime since;
  final int totalEvents;
  final Map<String, int> eventsByType;
  final List<MonitorHourlyPoint> eventsPerHour;
  final int totalLogs;
  final Map<String, int> logsByLevel;

  int countOfType(String type) => eventsByType[type] ?? 0;

  int countOfLevel(String level) => logsByLevel[level] ?? 0;

  factory MonitorSummary.fromJson(Map<String, dynamic> json) => MonitorSummary(
        since: DateTime.parse(json['since'] as String).toLocal(),
        totalEvents: json['total_events'] as int,
        eventsByType: Map<String, int>.from(
          (json['events_by_type'] as Map<String, dynamic>? ?? {})
              .map((key, value) => MapEntry(key, value as int)),
        ),
        eventsPerHour: (json['events_per_hour'] as List<dynamic>? ?? [])
            .map(
              (item) =>
                  MonitorHourlyPoint.fromJson(item as Map<String, dynamic>),
            )
            .toList(),
        totalLogs: json['total_logs'] as int,
        logsByLevel: Map<String, int>.from(
          (json['logs_by_level'] as Map<String, dynamic>? ?? {})
              .map((key, value) => MapEntry(key, value as int)),
        ),
      );
}

class TelemetryEvent {
  TelemetryEvent({
    required this.id,
    required this.deviceId,
    required this.eventType,
    required this.occurredAt,
  });

  final String id;
  final String deviceId;
  final String eventType;
  final DateTime occurredAt;

  factory TelemetryEvent.fromJson(Map<String, dynamic> json) => TelemetryEvent(
        id: json['event_id'] as String,
        deviceId: json['device_id'] as String,
        eventType: json['event_type'] as String,
        occurredAt: DateTime.parse(json['occurred_at'] as String).toLocal(),
      );
}

class LogEntry {
  LogEntry({
    required this.id,
    required this.deviceId,
    required this.level,
    required this.message,
    required this.occurredAt,
  });

  final String id;
  final String deviceId;
  final String level;
  final String message;
  final DateTime occurredAt;

  factory LogEntry.fromJson(Map<String, dynamic> json) => LogEntry(
        id: json['log_id'] as String,
        deviceId: json['device_id'] as String,
        level: json['level'] as String,
        message: json['message'] as String,
        occurredAt: DateTime.parse(json['occurred_at'] as String).toLocal(),
      );
}
