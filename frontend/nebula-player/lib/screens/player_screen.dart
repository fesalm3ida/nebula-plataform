import 'package:flutter/material.dart';

import '../player/media_kit_playback_controller.dart';
import '../theme/nebula_theme.dart';
import '../widgets/player_controls.dart';

/// Player em tela cheia (usado em telas estreitas / modo retrato).
class PlayerScreen extends StatefulWidget {
  const PlayerScreen({super.key, required this.url, required this.title});

  final String url;
  final String title;

  @override
  State<PlayerScreen> createState() => _PlayerScreenState();
}

class _PlayerScreenState extends State<PlayerScreen> {
  final MediaKitPlaybackController _controller = MediaKitPlaybackController();

  @override
  void initState() {
    super.initState();
    _controller.play(widget.url);
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.black,
        appBar: AppBar(title: Text(widget.title)),
        body: Stack(
          children: [
            Positioned.fill(child: _controller.buildVideo()),
            Positioned(
              left: 0,
              right: 0,
              bottom: 0,
              child: PlayerControls(controller: _controller),
            ),
          ],
        ),
      ),
    );
  }
}
