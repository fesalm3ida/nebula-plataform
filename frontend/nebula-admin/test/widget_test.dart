import 'package:flutter_test/flutter_test.dart';

import 'package:nebula_admin_ui/app.dart';

void main() {
  testWidgets('Nebula portal (user) builds', (WidgetTester tester) async {
    await tester.pumpWidget(const NebulaAdminApp());
    await tester.pump();

    // A raiz e o portal do usuario (o admin entra pela URL secreta).
    expect(find.text('Nebula Player'), findsOneWidget);
    expect(find.text('Entrar'), findsOneWidget);
  });
}
