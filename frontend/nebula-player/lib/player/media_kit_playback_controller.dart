import 'package:flutter/material.dart';
import 'package:media_kit/media_kit.dart';
import 'package:media_kit_video/media_kit_video.dart';

import 'playback_controller.dart';

/// Implementação de [PlaybackController] com `media_kit` (libmpv), robusta
/// para streams IPTV (mpegts/HLS).
///
/// A superfície de vídeo é entregue **sem** controles embutidos: as telas
/// desenham os seus próprios controles sobrepostos (ver `PlayerControls`).
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
  Future<void> play(String url) => _player.open(Media(url));

  @override
  Future<void> pause() => _player.pause();

  @override
  Future<void> playOrPause() => _player.playOrPause();

  @override
  Future<void> seek(Duration position) => _player.seek(position);

  @override
  Future<void> setVolume(double volume) => _player.setVolume(volume);

  @override
  Stream<Duration> get position => _player.stream.position;

  @override
  Stream<Duration> get duration => _player.stream.duration;

  @override
  Stream<bool> get playing => _player.stream.playing;

  @override
  Stream<double> get volume => _player.stream.volume;

  @override
  Future<void> dispose() => _player.dispose();
}
