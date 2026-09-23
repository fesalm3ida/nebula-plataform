import 'package:flutter/material.dart';

import '../player/media_kit_playback_controller.dart';
import '../services/telemetry_service.dart';
import '../theme/nebula_theme.dart';
import '../widgets/player_view.dart';

/// Player em tela cheia (usado em telas estreitas / modo retrato).
class PlayerScreen extends StatefulWidget {
  const PlayerScreen({
    super.key,
    required this.url,
    required this.title,
    this.isLive = false,
  });

  final String url;
  final String title;

  /// Canal ao vivo: sem barra de progresso (nao ha duracao/seek).
  final bool isLive;

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen> {
  final MediaKitPlaybackController _controller = MediaKitPlaybackController();

  @override
  void initState() {
    super.initState();
    _start();
  }

  Future<void> _start() async {
    final telemetry = TelemetryService.instance;

    try {
      await _controller.play(widget.url);

      telemetry.track('playback_started', {
        'title': widget.title,
        'url': widget.url,
        'live': widget.isLive,
      });
    } catch (error) {
      telemetry.track('playback_error', {
        'title': widget.title,
        'url': widget.url,
        'error': '$error',
      });
    }
  }

  @override
  void dispose() {
    TelemetryService.instance.track('playback_ended', {
      'title': widget.title,
      'live': widget.isLive,
    });
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(title: Text(widget.title)),
        body: PlayerView(
          controller: _controller,
          showProgress: !widget.isLive,
        ),
      ),
    );
  }
}
