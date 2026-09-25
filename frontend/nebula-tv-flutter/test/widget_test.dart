import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:nebula_tv/main.dart';
import 'package:nebula_tv/screens/tv_boot_screen.dart';

void main() {
  testWidgets('Nebula TV monta a tela de boot', (WidgetTester tester) async {
    await tester.pumpWidget(const NebulaTvApp());
    await tester.pump();

    expect(find.byType(MaterialApp), findsOneWidget);
    expect(find.byType(TvBootScreen), findsOneWidget);
  });
}
