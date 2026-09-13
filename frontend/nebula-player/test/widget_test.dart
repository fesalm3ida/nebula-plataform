import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:nebula_player/screens/home_menu_screen.dart';

void main() {
  testWidgets('Nebula Player home menu builds', (WidgetTester tester) async {
    await tester.pumpWidget(const MaterialApp(home: HomeMenuScreen()));
    await tester.pump();

    expect(find.text('Nebula Player'), findsOneWidget);
    expect(find.text('Ao vivo'), findsOneWidget);
  });
}
