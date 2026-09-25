import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../models/m3u_channel.dart';
import '../models/series_group.dart';
import 'tv_player_screen.dart';

/// Lista de episodios de uma serie (navegacao por controle).
class TvEpisodesScreen extends StatefulWidget {
  const TvEpisodesScreen({super.key, required this.group});

  final SeriesGroup group;

  @override
  State<TvEpisodesScreen> createState() => _TvEpisodesScreenState();
}

class _TvEpisodesScreenState extends State<TvEpisodesScreen> {
  int _row = 0;

  void _play(M3uChannel episode) {
    final url = episode.streamUrl;

    if (url == null || url.isEmpty) return;

    Navigator.of(context).push(
      MaterialPageRoute(
        builder: (_) => TvPlayerScreen(url: url, title: episode.displayName),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final episodes = widget.group.episodes;

    return Scaffold(
      body: Focus(
        autofocus: true,
        onKeyEvent: (node, event) {
          if (event is! KeyDownEvent) return KeyEventResult.ignored;

          final key = event.logicalKey;

          if (key == LogicalKeyboardKey.arrowDown) {
            setState(() => _row = (_row + 1).clamp(0, episodes.length - 1));
            return KeyEventResult.handled;
          }

          if (key == LogicalKeyboardKey.arrowUp) {
            setState(() => _row = (_row - 1).clamp(0, episodes.length - 1));
            return KeyEventResult.handled;
          }

          if (key == LogicalKeyboardKey.enter ||
              key == LogicalKeyboardKey.select) {
            _play(episodes[_row]);
            return KeyEventResult.handled;
          }

          if (key == LogicalKeyboardKey.escape ||
              key == LogicalKeyboardKey.goBack) {
            Navigator.of(context).pop();
            return KeyEventResult.handled;
          }

          return KeyEventResult.ignored;
        },
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.fromLTRB(40, 32, 40, 20),
              child: Row(
                children: [
                  Expanded(
                    child: Text(
                      widget.group.name,
                      style: const TextStyle(
                        fontSize: 36,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                  ),
                  Text(
                    '${episodes.length} episódios',
                    style: const TextStyle(
                      fontSize: 22,
                      color: Colors.white70,
                    ),
                  ),
                ],
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: 40),
                itemCount: episodes.length,
                itemBuilder: (context, index) {
                  final episode = episodes[index];
                  final focused = index == _row;

                  return Container(
                    margin: const EdgeInsets.only(bottom: 8),
                    padding: const EdgeInsets.symmetric(
                      horizontal: 22,
                      vertical: 16,
                    ),
                    decoration: BoxDecoration(
                      color: focused
                          ? const Color(0x668B3FFD)
                          : Colors.white10,
                      borderRadius: BorderRadius.circular(10),
                      border: Border.all(
                        color: focused
                            ? const Color(0xFFB07BFF)
                            : Colors.transparent,
                        width: 2,
                      ),
                    ),
                    child: Row(
                      children: [
                        SizedBox(
                          width: 70,
                          child: Text(
                            '${index + 1}',
                            style: const TextStyle(
                              fontSize: 20,
                              color: Colors.white54,
                            ),
                          ),
                        ),
                        Expanded(
                          child: Text(
                            episode.seriesName.isEmpty
                                ? episode.displayName
                                : episode.seriesName,
                            maxLines: 1,
                            overflow: TextOverflow.ellipsis,
                            style: const TextStyle(fontSize: 24),
                          ),
                        ),
                        Text(
                          episode.seasonEpisode,
                          style: const TextStyle(
                            fontSize: 22,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFFB07BFF),
                          ),
                        ),
                      ],
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}
