import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';

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

  @override
  Widget buildVideo({Key? key}) => Video(
        key: key,
        controller: _controller,
        controls: NoVideoControls,
      );

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
