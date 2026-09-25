import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:nebula_tv/main.dart';

void main() {
  testWidgets('Nebula TV inicia no boot', (WidgetTester tester) async {
    await tester.pumpWidget(const NebulaTvApp());

    // O boot mostra o progresso enquanto registra o aparelho no Core.
    expect(find.byType(CircularProgressIndicator), findsOneWidget);
    expect(find.textContaining('Inicializando'), findsOneWidget);
  });
}
