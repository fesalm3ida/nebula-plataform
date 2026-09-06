import 'package:flutter_test/flutter_test.dart';

import 'package:nebula_player/app.dart';

void main() {
  testWidgets('Nebula Player app builds', (WidgetTester tester) async {
    await tester.pumpWidget(const NebulaPlayerApp());
    await tester.pump();

    expect(find.text('Nebula Player'), findsOneWidget);
  });
}
