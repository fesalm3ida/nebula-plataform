import 'package:flutter/material.dart';
import 'package:flutter/services.dart';

import '../api/portal_api_client.dart';
import '../services/session_store.dart';
import '../widgets/mac_address_input_formatter.dart';
import 'user_portal_screen.dart';

/// Login do **usuário** com o MAC Address e o código de ativação exibidos
/// pelo Nebula Player.
class UserLoginScreen extends StatefulWidget {
  const UserLoginScreen({super.key});

  @override
  State<UserLoginScreen> createState() => _UserLoginScreenState();
}

class _UserLoginScreenState extends State<UserLoginScreen> {
  final PortalApiClient _api = PortalApiClient();
  final TextEditingController _macAddress = TextEditingController();
  final TextEditingController _activationCode = TextEditingController();

  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _macAddress.dispose();
    _activationCode.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final macAddress = _macAddress.text.trim();

      final session = (await _api.login(
        macAddress,
        _activationCode.text.trim(),
      ))
          .copyWith(macAddress: macAddress);

      // Guarda a sessao: o retorno do Mercado Pago recarrega a pagina.
      await SessionStore().save(session);

      if (!mounted) return;

      await Navigator.of(context).push(
        MaterialPageRoute(
          builder: (_) => UserPortalScreen(api: _api, session: session),
        ),
      );

      if (!mounted) return;
      setState(() {});
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: ConstrainedBox(
            constraints: const BoxConstraints(maxWidth: 420),
            child: Card(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: [
                    const Icon(Icons.play_circle_outline, size: 56),
                    const SizedBox(height: 12),
                    Text(
                      'Nebula Player',
                      textAlign: TextAlign.center,
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'Entre com o MAC Address e o código de ativação '
                      'exibidos na tela do seu aparelho.',
                      textAlign: TextAlign.center,
                    ),
                    const SizedBox(height: 24),
                    TextField(
                      controller: _macAddress,
                      inputFormatters: const [MacAddressInputFormatter()],
                      keyboardType: TextInputType.visiblePassword,
                      decoration: const InputDecoration(
                        labelText: 'MAC Address',
                        hintText: '02:C4:E0:F9:65:30',
                        helperText: '6 duplas separadas por ":"',
                      ),
                    ),
                    const SizedBox(height: 12),
                    TextField(
                      controller: _activationCode,
                      keyboardType: TextInputType.number,
                      inputFormatters: [
                        FilteringTextInputFormatter.digitsOnly,
                        LengthLimitingTextInputFormatter(6),
                      ],
                      decoration: const InputDecoration(
                        labelText: 'Código de ativação',
                        hintText: '000000',
                        helperText: '6 dígitos exibidos no aparelho',
                      ),
                    ),
                    if (_error != null) ...[
                      const SizedBox(height: 12),
                      Text(
                        _error!,
                        style: TextStyle(
                          color: Theme.of(context).colorScheme.error,
                        ),
                      ),
                    ],
                    const SizedBox(height: 24),
                    FilledButton(
                      onPressed: _loading ? null : _submit,
                      child: _loading
                          ? const SizedBox(
                              height: 18,
                              width: 18,
                              child: CircularProgressIndicator(
                                strokeWidth: 2,
                              ),
                            )
                          : const Text('Entrar'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ),
      ),
    );
  }
}
