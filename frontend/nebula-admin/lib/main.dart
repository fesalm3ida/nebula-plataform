import 'package:flutter/material.dart';

import 'app.dart';

void main() {
  // Captura a URL ANTES do Flutter assumir o roteamento: depois disso o
  // fragmento pode ser normalizado para '#/' e perderiamos a rota secreta
  // do administrador.
  final initialLocation = Uri.base.toString();

  runApp(NebulaAdminApp(initialLocation: initialLocation));
}
