import 'dart:async';

import 'package:flutter/material.dart';

import '../player/playback_controller.dart';
import 'player_controls.dart';

/// Vídeo do player com os controles sobrepostos.
///
/// - **Toque na tela**: alterna play/pause **e** traz os controles de volta.
/// - Os controles **desaparecem após 3 segundos** sem interação.
/// - Respeitam a área segura (`SafeArea`), ficando acima dos botões nativos
///   do Android (barra de navegação/gestos).
class PlayerView extends StatefulWidget {
  const PlayerView({
    super.key,
    required this.controller,
    this.showProgress = true,
  });

  final PlaybackController controller;

  /// Mostra a barra de progresso (apenas filmes e series).
  final bool showProgress;

  @override
  State<PlayerView> createState() => _PlayerViewState();
}

class _PlayerViewState extends State<PlayerView> {
  static const Duration _hideAfter = Duration(seconds: 3);
  static const Duration _fadeDuration = Duration(milliseconds: 250);

  Timer? _timer;
  bool _visible = true;

  @override
  void initState() {
    super.initState();
    _restartHideTimer();
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  void _restartHideTimer() {
    _timer?.cancel();
    _timer = Timer(_hideAfter, () {
      if (mounted) {
        setState(() => _visible = false);
      }
    });
  }

  void _showControls() {
    setState(() => _visible = true);
    _restartHideTimer();
  }

  /// Toque no vídeo: play/pause + controles visíveis.
  void _onTapVideo() {
    widget.controller.playOrPause();
    _showControls();
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: _onTapVideo,
            child: widget.controller.buildVideo(),
          ),
        ),
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: SafeArea(
            top: false,
            minimum: const EdgeInsets.only(bottom: 12),
            child: IgnorePointer(
              ignoring: !_visible,
              child: AnimatedOpacity(
                opacity: _visible ? 1 : 0,
                duration: _fadeDuration,
                child: Listener(
                  // Enquanto o usuario interage, nao esconde.
                  onPointerDown: (_) => _timer?.cancel(),
                  onPointerUp: (_) => _restartHideTimer(),
                  onPointerCancel: (_) => _restartHideTimer(),
                  child: PlayerControls(controller: widget.controller),
                ),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
