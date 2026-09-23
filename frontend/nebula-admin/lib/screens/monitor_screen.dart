import 'package:flutter/material.dart';

import '../api/admin_api_client.dart';
import '../models/auth_session.dart';
import '../models/monitor.dart';

/// Nebula Monitor: telemetria e logs dos aparelhos em campo.
class MonitorScreen extends StatefulWidget {
  const MonitorScreen({super.key, required this.session});

  final AuthSession session;

  @override
  State<MonitorScreen> createState() => _MonitorScreenState();
}

class _MonitorScreenState extends State<MonitorScreen> {
  final AdminApiClient _api = AdminApiClient();

  int _hours = 24;
  String? _eventType;
  String? _level;

  late Future<MonitorSummary> _summary;
  late Future<List<TelemetryEvent>> _events;
  late Future<List<LogEntry>> _logs;

  static const _eventLabels = {
    'playback_started': 'Reproduções',
    'playback_error': 'Erros de reprodução',
    'buffer_underrun': 'Travamentos (buffer)',
    'channel_changed': 'Trocas de canal',
    'playback_ended': 'Reproduções encerradas',
    'qos_report': 'Relatórios de QoS',
  };

  @override
  void initState() {
    super.initState();
    _reload();
  }

  void _reload() {
    setState(() {
      _summary = _api.monitorSummary(widget.session.accessToken, _hours);
      _events = _api.listTelemetry(
        widget.session.accessToken,
        hours: _hours,
        eventType: _eventType,
      );
      _logs = _api.listLogs(
        widget.session.accessToken,
        hours: _hours,
        level: _level,
      );
    });
  }

  static String _time(DateTime value) {
    final day = value.day.toString().padLeft(2, '0');
    final month = value.month.toString().padLeft(2, '0');
    final hour = value.hour.toString().padLeft(2, '0');
    final minute = value.minute.toString().padLeft(2, '0');

    return '$day/$month $hour:$minute';
  }

  static String _shortId(String value) =>
      value.length > 8 ? value.substring(0, 8) : value;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Nebula Monitor'),
        actions: [
          IconButton(
            tooltip: 'Atualizar',
            icon: const Icon(Icons.refresh),
            onPressed: _reload,
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => _reload(),
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            Row(
              children: [
                const Text('Período: '),
                const SizedBox(width: 8),
                DropdownButton<int>(
                  value: _hours,
                  items: const [
                    DropdownMenuItem(value: 24, child: Text('Últimas 24 h')),
                    DropdownMenuItem(value: 168, child: Text('Últimos 7 dias')),
                    DropdownMenuItem(value: 720, child: Text('Últimos 30 dias')),
                  ],
                  onChanged: (value) {
                    if (value == null) return;
                    _hours = value;
                    _reload();
                  },
                ),
              ],
            ),
            const SizedBox(height: 16),
            FutureBuilder<MonitorSummary>(
              future: _summary,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (snapshot.hasError) {
                  return _ErrorBox(message: '${snapshot.error}');
                }

                final summary = snapshot.data!;

                return Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Wrap(
                      spacing: 12,
                      runSpacing: 12,
                      children: [
                        _KpiCard(
                          label: 'Eventos',
                          value: '${summary.totalEvents}',
                          icon: Icons.timeline,
                        ),
                        _KpiCard(
                          label: 'Erros de reprodução',
                          value: '${summary.countOfType('playback_error')}',
                          icon: Icons.error_outline,
                          highlight: summary.countOfType('playback_error') > 0,
                        ),
                        _KpiCard(
                          label: 'Travamentos (buffer)',
                          value: '${summary.countOfType('buffer_underrun')}',
                          icon: Icons.hourglass_bottom,
                          highlight: summary.countOfType('buffer_underrun') > 0,
                        ),
                        _KpiCard(
                          label: 'Logs de erro',
                          value: '${summary.countOfLevel('error')}',
                          icon: Icons.article_outlined,
                          highlight: summary.countOfLevel('error') > 0,
                        ),
                      ],
                    ),
                    const SizedBox(height: 24),
                    Text(
                      'Eventos por hora',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    _HourlyChart(points: summary.eventsPerHour),
                    const SizedBox(height: 16),
                    Text(
                      'Por tipo de evento',
                      style: Theme.of(context).textTheme.titleMedium,
                    ),
                    const SizedBox(height: 8),
                    if (summary.eventsByType.isEmpty)
                      const Text('Nenhum evento no período.')
                    else
                      Column(
                        children: [
                          for (final entry in summary.eventsByType.entries)
                            ListTile(
                              dense: true,
                              contentPadding: EdgeInsets.zero,
                              leading: const Icon(Icons.chevron_right),
                              title: Text(
                                _eventLabels[entry.key] ?? entry.key,
                              ),
                              trailing: Text(
                                '${entry.value}',
                                style: const TextStyle(
                                  fontWeight: FontWeight.bold,
                                ),
                              ),
                            ),
                        ],
                      ),
                  ],
                );
              },
            ),
            const Divider(height: 32),
            _SectionHeader(
              title: 'Eventos recentes',
              trailing: DropdownButton<String?>(
                value: _eventType,
                hint: const Text('Todos os tipos'),
                items: [
                  const DropdownMenuItem(value: null, child: Text('Todos')),
                  for (final entry in _eventLabels.entries)
                    DropdownMenuItem(
                      value: entry.key,
                      child: Text(entry.value),
                    ),
                ],
                onChanged: (value) {
                  _eventType = value;
                  _reload();
                },
              ),
            ),
            FutureBuilder<List<TelemetryEvent>>(
              future: _events,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Padding(
                    padding: EdgeInsets.all(16),
                    child: Center(child: CircularProgressIndicator()),
                  );
                }

                if (snapshot.hasError) {
                  return _ErrorBox(message: '${snapshot.error}');
                }

                final events = snapshot.data!;

                if (events.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('Nenhum evento no período.'),
                  );
                }

                return Column(
                  children: [
                    for (final event in events)
                      ListTile(
                        dense: true,
                        leading: const Icon(Icons.play_circle_outline),
                        title: Text(
                          _eventLabels[event.eventType] ?? event.eventType,
                        ),
                        subtitle: Text(
                          'Aparelho ${_shortId(event.deviceId)} · '
                          '${_time(event.occurredAt)}',
                        ),
                      ),
                  ],
                );
              },
            ),
            const Divider(height: 32),
            _SectionHeader(
              title: 'Logs recentes',
              trailing: DropdownButton<String?>(
                value: _level,
                hint: const Text('Todos os níveis'),
                items: const [
                  DropdownMenuItem(value: null, child: Text('Todos')),
                  DropdownMenuItem(value: 'debug', child: Text('Debug')),
                  DropdownMenuItem(value: 'info', child: Text('Info')),
                  DropdownMenuItem(value: 'warning', child: Text('Aviso')),
                  DropdownMenuItem(value: 'error', child: Text('Erro')),
                ],
                onChanged: (value) {
                  _level = value;
                  _reload();
                },
              ),
            ),
            FutureBuilder<List<LogEntry>>(
              future: _logs,
              builder: (context, snapshot) {
                if (snapshot.connectionState != ConnectionState.done) {
                  return const Padding(
                    padding: EdgeInsets.all(16),
                    child: Center(child: CircularProgressIndicator()),
                  );
                }

                if (snapshot.hasError) {
                  return _ErrorBox(message: '${snapshot.error}');
                }

                final logs = snapshot.data!;

                if (logs.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.all(16),
                    child: Text('Nenhum log no período.'),
                  );
                }

                return Column(
                  children: [
                    for (final log in logs)
                      ListTile(
                        dense: true,
                        leading: _LevelBadge(level: log.level),
                        title: Text(log.message),
                        subtitle: Text(
                          'Aparelho ${_shortId(log.deviceId)} · '
                          '${_time(log.occurredAt)}',
                        ),
                      ),
                  ],
                );
              },
            ),
            const SizedBox(height: 32),
          ],
        ),
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  const _SectionHeader({required this.title, this.trailing});

  final String title;
  final Widget? trailing;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        children: [
          Expanded(
            child: Text(
              title,
              style: Theme.of(context).textTheme.titleMedium,
            ),
          ),
          if (trailing != null) trailing!,
        ],
      ),
    );
  }
}

class _KpiCard extends StatelessWidget {
  const _KpiCard({
    required this.label,
    required this.value,
    required this.icon,
    this.highlight = false,
  });

  final String label;
  final String value;
  final IconData icon;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    final color = highlight
        ? Theme.of(context).colorScheme.error
        : Theme.of(context).colorScheme.primary;

    return Card(
      child: SizedBox(
        width: 210,
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon, color: color),
              const SizedBox(height: 8),
              Text(
                value,
                style: Theme.of(context).textTheme.headlineSmall?.copyWith(
                      color: color,
                      fontWeight: FontWeight.bold,
                    ),
              ),
              Text(label, style: Theme.of(context).textTheme.bodySmall),
            ],
          ),
        ),
      ),
    );
  }
}

/// Gráfico de barras simples (sem dependências externas).
class _HourlyChart extends StatelessWidget {
  const _HourlyChart({required this.points});

  final List<MonitorHourlyPoint> points;

  @override
  Widget build(BuildContext context) {
    if (points.isEmpty) {
      return const Text('Sem dados no período.');
    }

    final max = points
        .map((point) => point.count)
        .reduce((a, b) => a > b ? a : b);

    return SizedBox(
      height: 140,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Row(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              for (final point in points)
                Expanded(
                  child: Tooltip(
                    message: '${_MonitorScreenState._time(point.hour)} · '
                        '${point.count}',
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 1),
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.end,
                        children: [
                          Container(
                            height: max == 0
                                ? 2
                                : (100 * point.count / max).clamp(2, 100),
                            decoration: BoxDecoration(
                              color: Theme.of(context).colorScheme.primary,
                              borderRadius: BorderRadius.circular(3),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
            ],
          ),
        ),
      ),
    );
  }
}

class _LevelBadge extends StatelessWidget {
  const _LevelBadge({required this.level});

  final String level;

  @override
  Widget build(BuildContext context) {
    final colors = {
      'error': Colors.red,
      'warning': Colors.orange,
      'info': Colors.blueGrey,
      'debug': Colors.grey,
    };

    return CircleAvatar(
      radius: 14,
      backgroundColor: colors[level] ?? Colors.grey,
      child: Text(
        level.isEmpty ? '?' : level[0].toUpperCase(),
        style: const TextStyle(fontSize: 12, color: Colors.white),
      ),
    );
  }
}

class _ErrorBox extends StatelessWidget {
  const _ErrorBox({required this.message});

  final String message;

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.errorContainer,
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Row(
          children: [
            const Icon(Icons.cloud_off),
            const SizedBox(width: 12),
            Expanded(child: Text(message)),
          ],
        ),
      ),
    );
  }
}
