import 'package:flutter/material.dart';

/// Abstração sobre o player de vídeo. A implementação concreta usa `media_kit`
/// (libmpv). As telas constroem seus próprios controles a partir dos streams
/// expostos aqui.
abstract class PlaybackController {
  /// Superfície de vídeo (sem controles embutidos).
  Widget buildVideo({Key? key});

  Future<void> play(String url);
  Future<void> pause();
  Future<void> playOrPause();
  Future<void> seek(Duration position);
  Future<void> setVolume(double volume);

  Stream<Duration> get position;
  Stream<Duration> get duration;
  Stream<bool> get playing;
  Stream<double> get volume;

  Future<void> dispose();
}

/// Implementação provisória (sem vídeo real), útil para testes.
class StubPlaybackController implements PlaybackController {
  String? currentUrl;

  @override
  Widget buildVideo({Key? key}) {
    return Container(
      key: key,
      alignment: Alignment.center,
      color: Colors.black,
      child: const Text(
        'Reprodução em breve',
        style: TextStyle(color: Colors.white70, fontSize: 18),
      ),
    );
  }

  @override
  Future<void> play(String url) async {
    currentUrl = url;
  }

  @override
  Future<void> pause() async {}

  @override
  Future<void> playOrPause() async {}

  @override
  Future<void> seek(Duration position) async {}

  @override
  Future<void> setVolume(double volume) async {}

  @override
  Stream<Duration> get position => const Stream<Duration>.empty();

  @override
  Stream<Duration> get duration => const Stream<Duration>.empty();

  @override
  Stream<bool> get playing => const Stream<bool>.empty();

  @override
  Stream<double> get volume => const Stream<double>.empty();

  @override
  Future<void> dispose() async {}
}
