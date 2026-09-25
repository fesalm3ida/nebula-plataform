import 'package:flutter/material.dart';

import 'tv_boot_screen.dart';

/// Tela de ativacao exibida na TV: MAC Address + codigo de 6 digitos.
class TvActivationScreen extends StatelessWidget {
  const TvActivationScreen({
    super.key,
    required this.macAddress,
    required this.activationCode,
    this.message = '',
  });

  final String macAddress;
  final String activationCode;
  final String message;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            const Text(
              'Nebula TV',
              style: TextStyle(fontSize: 54, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              message.isEmpty
                  ? 'Ative este aparelho no portal Nebula e informe os dados abaixo:'
                  : message,
              textAlign: TextAlign.center,
              style: const TextStyle(fontSize: 24, color: Colors.white70),
            ),
            const SizedBox(height: 40),
            Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                _DataCard(label: 'MAC Address', value: macAddress),
                const SizedBox(width: 32),
                _DataCard(
                  label: 'Código de ativação',
                  value: activationCode.isEmpty ? '—' : activationCode,
                  highlight: true,
                ),
              ],
            ),
            const SizedBox(height: 40),
            FilledButton(
              autofocus: true,
              onPressed: () => Navigator.of(context).pushReplacement(
                MaterialPageRoute(builder: (_) => const TvBootScreen()),
              ),
              child: const Text(
                'Verificar agora',
                style: TextStyle(fontSize: 24),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _DataCard extends StatelessWidget {
  const _DataCard({
    required this.label,
    required this.value,
    this.highlight = false,
  });

  final String label;
  final String value;
  final bool highlight;

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 44, vertical: 28),
      decoration: BoxDecoration(
        color: Colors.white10,
        borderRadius: BorderRadius.circular(20),
        border: Border.all(
          color: highlight ? const Color(0xFF8B3FFD) : Colors.white24,
          width: 2,
        ),
      ),
      child: Column(
        children: [
          Text(label, style: const TextStyle(fontSize: 22, color: Colors.white70)),
          const SizedBox(height: 10),
          Text(
            value,
            style: const TextStyle(
              fontSize: 46,
              fontWeight: FontWeight.bold,
              letterSpacing: 2,
            ),
          ),
        ],
      ),
    );
  }
}
