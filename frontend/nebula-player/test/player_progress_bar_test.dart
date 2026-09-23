import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nebula_player/player/playback_controller.dart';
import 'package:nebula_player/widgets/player_view.dart';

/// Controlador de teste com emissão manual dos streams.
class _FakeController implements PlaybackController {
  final _position = StreamController<Duration>.broadcast();
  final _duration = StreamController<Duration>.broadcast();
  final _playing = StreamController<bool>.broadcast();
  final _volume = StreamController<double>.broadcast();

  void emitDuration(Duration value) => _duration.add(value);

  @override
  Widget buildVideo({Key? key}) => const SizedBox(key: Key('video'));

  @override
  Future<void> play(String url) async {}

  @override
  Future<void> pause() async {}

  @override
  Future<void> playOrPause() async {}

  @override
  Future<void> seek(Duration position) async {}

  @override
  Future<void> setVolume(double volume) async {}

  @override
  Stream<Duration> get position => _position.stream;

  @override
  Stream<Duration> get duration => _duration.stream;

  @override
  Stream<bool> get playing => _playing.stream;

  @override
  Stream<double> get volume => _volume.stream;

  @override
  Future<void> dispose() async {}
}

Widget _wrap(Widget child) => MaterialApp(home: Scaffold(body: child));

void main() {
  late _FakeController controller;

  setUp(() => controller = _FakeController());

  tearDown(() => controller.dispose());

  testWidgets('canal ao vivo: sem barra de progresso', (tester) async {
    await tester.pumpWidget(
      _wrap(PlayerView(controller: controller, showProgress: false)),
    );

    // Mesmo com duracao reportada (alguns streams ao vivo informam uma
    // duracao falsa), a barra nao aparece.
    controller.emitDuration(const Duration(seconds: 30));
    await tester.pump();

    expect(find.byType(Slider), findsOneWidget);

    // Descarta o widget para cancelar o timer de auto-ocultar.
    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('filme/serie: mostra a barra de progresso', (tester) async {
    await tester.pumpWidget(
      _wrap(PlayerView(controller: controller, showProgress: true)),
    );

    controller.emitDuration(const Duration(seconds: 30));
    await tester.pump();

    // Volume + progresso.
    expect(find.byType(Slider), findsNWidgets(2));

    await tester.pumpWidget(const SizedBox());
  });

  testWidgets('sem duracao: barra oculta mesmo em VOD', (tester) async {
    await tester.pumpWidget(
      _wrap(PlayerView(controller: controller, showProgress: true)),
    );

    await tester.pump();

    expect(find.byType(Slider), findsOneWidget);

    await tester.pumpWidget(const SizedBox());
  });
}
