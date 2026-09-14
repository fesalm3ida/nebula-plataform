import 'package:flutter/material.dart';

import '../player/playback_controller.dart';
import '../theme/nebula_theme.dart';

/// Controles do player: barra de progresso (seek), play/pause e volume.
///
/// É sobreposto ao vídeo pelo chamador (via `Stack`), garantindo o mesmo
/// posicionamento em retrato e paisagem.
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
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 2),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          StreamBuilder<Duration>(
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
                  final value = raw > max ? max : (raw < 0 ? 0 : raw);

                  return Row(
                    children: [
                      Text(
                        _format(position),
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
                        _format(duration),
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
          ),
          Row(
            children: [
              StreamBuilder<bool>(
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
              ),
              const Spacer(),
              const Icon(
                Icons.volume_up,
                color: NebulaColors.textPrimary,
                size: 20,
              ),
              SizedBox(
                width: 140,
                child: StreamBuilder<double>(
                  stream: controller.volume,
                  initialData: 100,
                  builder: (context, snapshot) {
                    final volume =
                        (snapshot.data ?? 100).clamp(0, 100).toDouble();

                    return Slider(
                      value: volume,
                      max: 100,
                      activeColor: NebulaColors.primary,
                      inactiveColor: Colors.white24,
                      onChanged: controller.setVolume,
                    );
                  },
                ),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
