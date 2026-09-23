import 'package:flutter_test/flutter_test.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'package:nebula_admin_ui/app.dart';

void main() {
  setUp(() {
    // O portal usa shared_preferences (localStorage) para guardar a sessao.
    SharedPreferences.setMockInitialValues({});
  });

  testWidgets('Nebula portal (user) builds', (WidgetTester tester) async {
    await tester.pumpWidget(const NebulaAdminApp());
    await tester.pumpAndSettle();

    // A raiz e o portal do usuario (o admin entra pela URL secreta).
    expect(find.text('Nebula Player'), findsOneWidget);
    expect(find.text('Entrar'), findsOneWidget);
  });

  testWidgets('admin URL opens the admin login', (WidgetTester tester) async {
    await tester.pumpWidget(
      const NebulaAdminApp(
        initialLocation: 'https://portal/#/gestao-nebula-3f9c',
      ),
    );
    await tester.pumpAndSettle();

    expect(find.text('Nebula Admin'), findsOneWidget);
  });
}
