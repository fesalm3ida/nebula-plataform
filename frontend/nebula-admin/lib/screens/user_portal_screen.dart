import 'package:flutter/material.dart';

import '../api/portal_api_client.dart';
import '../models/portal.dart';

/// Portal do **usuário**: status/licença do aparelho e cadastro da lista.
class UserPortalScreen extends StatefulWidget {
  const UserPortalScreen({
    super.key,
    required this.api,
    required this.session,
  });

  final PortalApiClient api;
  final PortalSession session;

  @override
  State<UserPortalScreen> createState() => _UserPortalScreenState();
}

class _UserPortalScreenState extends State<UserPortalScreen> {
  PortalDevice? _device;
  bool _loading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final device = await widget.api.device(widget.session.accessToken);

      if (!mounted) return;

      setState(() {
        _device = device;
        _loading = false;
      });
    } catch (error) {
      if (!mounted) return;
      setState(() {
        _loading = false;
        _error = error.toString();
      });
    }
  }

  void _showMessage(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Theme.of(context).colorScheme.error : null,
      ),
    );
  }

  Future<void> _activate() async {
    try {
      final device = await widget.api.activate(widget.session.accessToken);

      if (!mounted) return;

      setState(() => _device = device);
      _showMessage('Aparelho ativado! Teste grátis de 7 dias liberado.');
    } catch (error) {
      if (!mounted) return;
      _showMessage('$error', isError: true);
    }
  }

  Future<void> _registerPlaylist() async {
    final playlist = await showDialog<PortalPlaylist>(
      context: context,
      builder: (_) => _PlaylistForm(
        api: widget.api,
        token: widget.session.accessToken,
        current: _device?.playlist,
      ),
    );

    if (playlist == null) return;

    await _load();
    if (!mounted) return;
    _showMessage('Lista cadastrada com sucesso.');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Meu aparelho'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      floatingActionButton: _device == null
          ? null
          : FloatingActionButton.extended(
              onPressed: _registerPlaylist,
              icon: const Icon(Icons.playlist_add),
              label: Text(
                _device!.playlist == null ? 'Cadastrar lista' : 'Trocar lista',
              ),
            ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text('Erro: $_error'))
              : ListView(
                  padding: const EdgeInsets.all(16),
                  children: [
                    _DeviceCard(device: _device!),
                    const SizedBox(height: 12),
                    _LicenseCard(
                      license: _device!.license,
                      onActivate: _device!.license.isPending ? _activate : null,
                    ),
                    const SizedBox(height: 12),
                    _PlaylistCard(playlist: _device!.playlist),
                  ],
                ),
    );
  }
}

class _DeviceCard extends StatelessWidget {
  const _DeviceCard({required this.device});

  final PortalDevice device;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: ListTile(
        leading: const Icon(Icons.tv),
        title: const Text('Identificação do aparelho'),
        subtitle: Text(device.deviceId),
      ),
    );
  }
}

class _LicenseCard extends StatelessWidget {
  const _LicenseCard({required this.license, this.onActivate});

  final PortalLicense license;
  final VoidCallback? onActivate;

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Licença',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Icon(
                  license.expired
                      ? Icons.error_outline
                      : Icons.verified_outlined,
                  color: license.expired
                      ? Theme.of(context).colorScheme.error
                      : Colors.green,
                ),
                const SizedBox(width: 8),
                Expanded(child: Text(license.label)),
              ],
            ),
            if (license.expiresAt != null) ...[
              const SizedBox(height: 4),
              Text('Vence em: ${license.expiresAt}'),
            ],
            if (onActivate != null) ...[
              const SizedBox(height: 16),
              FilledButton.icon(
                onPressed: onActivate,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Ativar (teste grátis de 7 dias)'),
              ),
              const SizedBox(height: 8),
              const Text(
                'A primeira ativação é gratuita e libera 7 dias de uso.',
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _PlaylistCard extends StatelessWidget {
  const _PlaylistCard({required this.playlist});

  final PortalPlaylist? playlist;

  @override
  Widget build(BuildContext context) {
    final current = playlist;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Lista de reprodução',
              style: TextStyle(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            if (current == null)
              const Text('Nenhuma lista cadastrada.')
            else ...[
              Text(current.name),
              const SizedBox(height: 4),
              Text(
                current.sourceUrl,
                style: Theme.of(context).textTheme.bodySmall,
              ),
            ],
          ],
        ),
      ),
    );
  }
}

class _PlaylistForm extends StatefulWidget {
  const _PlaylistForm({
    required this.api,
    required this.token,
    this.current,
  });

  final PortalApiClient api;
  final String token;
  final PortalPlaylist? current;

  @override
  State<_PlaylistForm> createState() => _PlaylistFormState();
}

class _PlaylistFormState extends State<_PlaylistForm> {
  late final TextEditingController _name = TextEditingController(
    text: widget.current?.name ?? '',
  );
  late final TextEditingController _sourceUrl = TextEditingController(
    text: widget.current?.sourceUrl ?? '',
  );

  bool _loading = false;
  String? _error;

  @override
  void dispose() {
    _name.dispose();
    _sourceUrl.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final playlist = await widget.api.registerPlaylist(
        widget.token,
        _name.text.trim(),
        _sourceUrl.text.trim(),
      );

      if (!mounted) return;
      Navigator.of(context).pop(playlist);
    } catch (error) {
      if (!mounted) return;
      setState(() => _error = error.toString());
    } finally {
      if (mounted) setState(() => _loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: Text(
        widget.current == null ? 'Cadastrar lista' : 'Trocar lista',
      ),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _name,
            decoration: const InputDecoration(labelText: 'Nome da lista'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _sourceUrl,
            decoration: const InputDecoration(
              labelText: 'URL da lista (M3U / m3u_plus)',
            ),
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(
              _error!,
              style: TextStyle(color: Theme.of(context).colorScheme.error),
            ),
          ],
        ],
      ),
      actions: [
        TextButton(
          onPressed: _loading ? null : () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _loading ? null : _submit,
          child: const Text('Salvar'),
        ),
      ],
    );
  }
}
