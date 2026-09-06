import 'package:flutter_test/flutter_test.dart';

import 'package:nebula_admin_ui/app.dart';

void main() {
  testWidgets('Nebula Admin app builds', (WidgetTester tester) async {
    await tester.pumpWidget(const NebulaAdminApp());
    await tester.pump();

    expect(find.text('Nebula Admin'), findsOneWidget);
  });
}
