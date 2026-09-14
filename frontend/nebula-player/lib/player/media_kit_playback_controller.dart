import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';

import '../theme/nebula_theme.dart';
import 'playback_controller.dart';

/// Implementação de [PlaybackController] com `media_kit` (libmpv), robusta
/// para streams IPTV (mpegts/HLS).
class MediaKitPlaybackController implements PlaybackController {
  MediaKitPlaybackController() {
    _player = Player();
    _controller = VideoController(_player);
  }

  late final Player _player;
  late final VideoController _controller;

  /// Tema dos controles (barra de progresso / botões) na cor do Nebula.
  static const MaterialVideoControlsThemeData _controlsTheme =
      MaterialVideoControlsThemeData(
    seekBarPositionColor: NebulaColors.primary,
    seekBarThumbColor: NebulaColors.primary,
    seekBarBufferColor: Color(0x4DFFFFFF),
    buttonBarButtonColor: NebulaColors.textPrimary,
  );

  @override
  Widget buildVideo({Key? key, bool controls = false}) {
    if (!controls) {
      return Video(
        key: key,
        controller: _controller,
        controls: NoVideoControls,
      );
    }

    return MaterialVideoControlsTheme(
      normal: _controlsTheme,
      fullscreen: _controlsTheme,
      child: Video(
        key: key,
        controller: _controller,
        controls: MaterialVideoControls,
      ),
    );
  }

  @override
  Future<void> play(String url) async {
    await _player.open(Media(url));
  }

  @override
  Future<void> pause() async {
    await _player.pause();
  }

  @override
  Future<void> dispose() async {
    await _player.dispose();
  }
}
