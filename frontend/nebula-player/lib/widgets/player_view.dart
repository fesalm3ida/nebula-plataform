import 'dart:async';

import 'package:flutter/material.dart';

import '../player/playback_controller.dart';
import 'player_controls.dart';

/// Vídeo do player com os controles sobrepostos.
///
/// Os controles **desaparecem após 3 segundos** sem interação e **reaparecem
/// ao toque na tela**. Enquanto o usuário interage (arrastando a barra de
/// progresso ou de volume), eles não somem.
class PlayerView extends StatefulWidget {
  const PlayerView({super.key, required this.controller});

  final PlaybackController controller;

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

  void _toggleControls() {
    setState(() => _visible = !_visible);

    if (_visible) {
      _restartHideTimer();
    } else {
      _timer?.cancel();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Stack(
      children: [
        Positioned.fill(
          child: GestureDetector(
            behavior: HitTestBehavior.opaque,
            onTap: _toggleControls,
            child: widget.controller.buildVideo(),
          ),
        ),
        Positioned(
          left: 0,
          right: 0,
          bottom: 0,
          child: IgnorePointer(
            ignoring: !_visible,
            child: AnimatedOpacity(
              opacity: _visible ? 1 : 0,
              duration: _fadeDuration,
              child: Listener(
                // Enquanto o usuario interage com os controles, nao esconde.
                onPointerDown: (_) => _timer?.cancel(),
                onPointerUp: (_) => _restartHideTimer(),
                onPointerCancel: (_) => _restartHideTimer(),
                child: PlayerControls(controller: widget.controller),
              ),
            ),
          ),
        ),
      ],
    );
  }
}
