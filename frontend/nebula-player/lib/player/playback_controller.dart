import 'package:flutter/material.dart';

/// Abstração sobre o player de vídeo. A implementação concreta
/// (ex.: media_kit / video_player) será plugada quando decidirmos o pacote,
/// sem reescrever as telas.
abstract class PlaybackController {
  /// Constrói a superfície de vídeo. Com [controls] = true, inclui os
  /// controles (barra de progresso, play/pause, volume, tela cheia).
  Widget buildVideo({Key? key, bool controls = false});
  Future<void> play(String url);
  Future<void> pause();
  Future<void> dispose();
}

/// Implementação provisória: exibe um placeholder com o canal selecionado.
class StubPlaybackController implements PlaybackController {
  String? currentUrl;

  @override
  Widget buildVideo({Key? key, bool controls = false}) {
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
  Future<void> dispose() async {}
}
