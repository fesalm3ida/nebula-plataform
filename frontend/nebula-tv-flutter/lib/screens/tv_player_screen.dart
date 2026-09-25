import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';

import '../services/telemetry_service.dart';

/// Player em tela cheia (media_kit/libmpv: MPEG-TS, HLS, MP4).
class TvPlayerScreen extends StatefulWidget {
  const TvPlayerScreen({super.key, required this.url, required this.title});

  final String url;
  final String title;

  @override
  State<TvPlayerScreen> createState() => _TvPlayerScreenState();
}

class _TvPlayerScreenState extends State<TvPlayerScreen> {
  late final Player _player = Player();
  late final VideoController _controller = VideoController(_player);

  static const bool _showInfo = true;

  @override
  void initState() {
    super.initState();
    _start();
  }

  Future<void> _start() async {
    try {
      await _player.open(Media(widget.url));
      TelemetryService.instance.track('playback_started', {
        'title': widget.title,
        'url': widget.url,
      });
    } catch (_) {
      // erro exibido pelo proprio player
    }
  }

  @override
  void dispose() {
    TelemetryService.instance.track('playback_ended', {'title': widget.title});
    _player.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          Positioned.fill(child: Video(controller: _controller)),
          Positioned(
            left: 40,
            right: 40,
            bottom: 36,
            child: AnimatedOpacity(
              opacity: _showInfo ? 1 : 0,
              duration: const Duration(milliseconds: 250),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    widget.title,
                    style: const TextStyle(
                      fontSize: 34,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                  const SizedBox(height: 6),
                  const Text(
                    'OK: pausar · Voltar: sair',
                    style: TextStyle(fontSize: 20, color: Colors.white70),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
