import 'package:flutter/material.dart';

import '../player/playback_controller.dart';
import 'player_controls.dart';

/// Vídeo do player com os controles sobrepostos e **toque na tela alternando
/// play/pause**.
class PlayerView extends StatelessWidget {
  const PlayerView({super.key, required this.controller});

  final PlaybackController controller;

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: controller.playOrPause,
            child: controller.buildVideo(),
          ),
        ),
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: PlayerControls(controller: controller),
        ),
      ],
    );
  }
}
