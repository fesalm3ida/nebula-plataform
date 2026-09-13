import 'package:flutter/material.dart';

import '../services/local_playlist_service.dart';
import '../theme/nebula_theme.dart';

/// Permite informar uma lista de reprodução (M3U) localmente no dispositivo.
class ChangePlaylistScreen extends StatefulWidget {
  const ChangePlaylistScreen({super.key});

  @override
  State<ChangePlaylistScreen> createState() => _ChangePlaylistScreenState();
}

class _ChangePlaylistScreenState extends State<ChangePlaylistScreen> {
  final LocalPlaylistService _service = LocalPlaylistService();
  final TextEditingController _name = TextEditingController();
  final TextEditingController _url = TextEditingController();

  bool _loading = true;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _name.dispose();
    _url.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final name = await _service.getName();
    final url = await _service.getUrl();

    if (!mounted) return;

    setState(() {
      _name.text = name ?? '';
      _url.text = url ?? '';
      _loading = false;
    });
  }

  Future<void> _save() async {
    await _service.save(name: _name.text.trim(), url: _url.text.trim());

    if (!mounted) return;

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Lista salva.')),
    );
    Navigator.of(context).pop(true);
  }

  InputDecoration _decoration(String label) => InputDecoration(
        labelText: label,
        labelStyle: const TextStyle(color: NebulaColors.textSecondary),
        enabledBorder: const OutlineInputBorder(
          borderSide: BorderSide(color: NebulaColors.surfaceBorder),
        ),
        focusedBorder: const OutlineInputBorder(
          borderSide: BorderSide(color: NebulaColors.primary),
        ),
      );

  @override
  Widget build(BuildContext context) {
    return NebulaTheme.background(
      child: Scaffold(
        backgroundColor: Colors.transparent,
        appBar: AppBar(title: const Text('Mudar lista de reprodução')),
        body: _loading
            ? const Center(child: CircularProgressIndicator())
            : ListView(
                padding: const EdgeInsets.all(16),
                children: [
                  TextField(
                    controller: _name,
                    style: const TextStyle(color: NebulaColors.textPrimary),
                    decoration: _decoration('Nome da lista'),
                  ),
                  const SizedBox(height: 16),
                  TextField(
                    controller: _url,
                    style: const TextStyle(color: NebulaColors.textPrimary),
                    decoration:
                        _decoration('URL da lista (M3U / m3u_plus)'),
                  ),
                  const SizedBox(height: 24),
                  FilledButton(
                    onPressed: _save,
                    child: const Text('Salvar lista'),
                  ),
                ],
              ),
      ),
    );
  }
}
