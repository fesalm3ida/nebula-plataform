import 'package:flutter/material.dart';

import '../player/playback_controller.dart';
import '../theme/nebula_theme.dart';

/// Controles do player, sobrepostos ao vídeo pelo [PlayerView].
///
/// Linha de cima: **play/pause** (esquerda) e **volume** (direita).
/// Linha de baixo: **barra de progresso** (omitida em transmissões ao vivo).
class PlayerControls extends StatelessWidget {
  const PlayerControls({super.key, required this.controller});

  final PlaybackController controller;

  static String _format(Duration duration) {
    final hours = duration.inHours;
    final minutes =
        duration.inMinutes.remainder(60).toString().padLeft(2, '0');
    final seconds =
        duration.inSeconds.remainder(60).toString().padLeft(2, '0');

    return hours > 0 ? '$hours:$minutes:$seconds' : '$minutes:$seconds';
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.black54,
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Row(
            children: [
              _PlayPauseButton(controller: controller),
              const Spacer(),
              const Icon(
                Icons.volume_up,
                color: NebulaColors.textPrimary,
                size: 20,
              ),
              SizedBox(
                width: 150,
                child: _VolumeSlider(controller: controller),
              ),
            ],
          ),
          _ProgressBar(controller: controller),
        ],
      ),
    );
  }
}

/// Play/pause (lado esquerdo da linha).
class _PlayPauseButton extends StatelessWidget {
  const _PlayPauseButton({required this.controller});

  final PlaybackController controller;

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<bool>(
      stream: controller.playing,
      initialData: false,
      builder: (context, snapshot) {
        final playing = snapshot.data ?? false;

        return IconButton(
          tooltip: playing ? 'Pausar' : 'Reproduzir',
          icon: Icon(
            playing ? Icons.pause : Icons.play_arrow,
            color: NebulaColors.textPrimary,
          ),
          onPressed: controller.playOrPause,
        );
      },
    );
  }
}

/// Volume (lado direito da linha).
class _VolumeSlider extends StatelessWidget {
  const _VolumeSlider({required this.controller});

  final PlaybackController controller;

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<double>(
      stream: controller.volume,
      initialData: 100,
      builder: (context, snapshot) {
        final volume = (snapshot.data ?? 100).clamp(0, 100).toDouble();

        return Slider(
          value: volume,
          max: 100,
          activeColor: NebulaColors.primary,
          inactiveColor: Colors.white24,
          onChanged: controller.setVolume,
        );
      },
    );
  }
}

/// Barra de progresso (posição / duração) — oculta em transmissões ao vivo.
class _ProgressBar extends StatelessWidget {
  const _ProgressBar({required this.controller});

  final PlaybackController controller;

  @override
  Widget build(BuildContext context) {
    return StreamBuilder<Duration>(
      stream: controller.duration,
      initialData: Duration.zero,
      builder: (context, durationSnapshot) {
        final duration = durationSnapshot.data ?? Duration.zero;

        // Streams ao vivo não têm duração: sem barra de progresso.
        if (duration.inSeconds <= 0) {
          return const SizedBox.shrink();
        }

        return StreamBuilder<Duration>(
          stream: controller.position,
          initialData: Duration.zero,
          builder: (context, positionSnapshot) {
            final position = positionSnapshot.data ?? Duration.zero;
            final max = duration.inMilliseconds.toDouble();
            final raw = position.inMilliseconds.toDouble();
            final value = raw > max ? max : (raw < 0 ? 0.0 : raw);

            return Row(
              children: [
                Text(
                  PlayerControls._format(position),
                  style: const TextStyle(
                    color: NebulaColors.textPrimary,
                    fontSize: 12,
                  ),
                ),
                Expanded(
                  child: Slider(
                    value: value,
                    max: max,
                    activeColor: NebulaColors.primary,
                    inactiveColor: Colors.white24,
                    onChanged: (value) => controller.seek(
                      Duration(milliseconds: value.round()),
                    ),
                  ),
                ),
                Text(
                  PlayerControls._format(duration),
                  style: const TextStyle(
                    color: NebulaColors.textPrimary,
                    fontSize: 12,
                  ),
                ),
              ],
            );
          },
        );
      },
    );
  }
}
