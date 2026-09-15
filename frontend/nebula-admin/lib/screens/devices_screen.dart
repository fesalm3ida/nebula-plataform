import 'package:flutter/material.dart';

import '../api/admin_api_client.dart';
import '../models/auth_session.dart';
import '../models/device.dart';
import '../models/playlist.dart';

/// Gestão de devices: listar, ativar/bloquear e associar playlists.
class DevicesScreen extends StatefulWidget {
  const DevicesScreen({super.key, required this.session});

  final AuthSession session;

  @override
  State<DevicesScreen> createState() => _DevicesScreenState();
}

class _DevicesScreenState extends State<DevicesScreen> {
  final AdminApiClient _api = AdminApiClient();
  late Future<List<Device>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.listDevices(widget.session.accessToken);
  }

  void _refresh() {
    setState(() {
      _future = _api.listDevices(widget.session.accessToken);
    });
  }

  void _showMessage(String message, {bool isError = false}) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: isError ? Theme.of(context).colorScheme.error : null,
      ),
    );
  }

  Future<void> _runAction(Device device, String action) async {
    try {
      final status = await _api.setDeviceStatus(
        widget.session.accessToken,
        device.id,
        action,
      );

      if (!mounted) return;

      _showMessage('Device: $status.');
      _refresh();
    } catch (error) {
      if (!mounted) return;
      _showMessage('$error', isError: true);
    }
  }

  Future<void> _confirmReset(Device device) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (dialogContext) => AlertDialog(
        title: const Text('Resetar licença'),
        content: const Text(
          'O aparelho voltará para "aguardando ativação" e perderá a '
          'licença atual (trial ou paga). Ele precisará ser ativado '
          'novamente.\n\nContinuar?',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(dialogContext).pop(false),
            child: const Text('Cancelar'),
          ),
          FilledButton(
            onPressed: () => Navigator.of(dialogContext).pop(true),
            child: const Text('Resetar'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await _runAction(device, 'reset-license');
    }
  }

  Future<void> _assign(Device device) async {
    final playlistId = await showDialog<String>(
      context: context,
      builder: (_) => _AssignPlaylistDialog(
        api: _api,
        token: widget.session.accessToken,
      ),
    );

    if (playlistId == null) return;

    try {
      await _api.assignPlaylist(
        widget.session.accessToken,
        device.id,
        playlistId,
      );

      if (!mounted) return;

      _showMessage('Playlist associada ao device.');
    } catch (error) {
      if (!mounted) return;
      _showMessage('$error', isError: true);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Devices'),
        actions: [
          IconButton(icon: const Icon(Icons.refresh), onPressed: _refresh),
        ],
      ),
      body: FutureBuilder<List<Device>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError) {
            return Center(child: Text('Erro: ${snapshot.error}'));
          }

          final devices = snapshot.data ?? [];

          if (devices.isEmpty) {
            return const Center(child: Text('Nenhum device registrado.'));
          }

          return ListView.separated(
            itemCount: devices.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final device = devices[index];

              return ListTile(
                leading: const Icon(Icons.tv),
                title: Text(device.platform),
                subtitle: Text('${device.id}\n${device.createdAt}'),
                isThreeLine: true,
                trailing: Wrap(
                  spacing: 4,
                  crossAxisAlignment: WrapCrossAlignment.center,
                  children: [
                    Chip(label: Text(device.status)),
                    IconButton(
                      tooltip: 'Resetar licença (volta a aguardar ativação)',
                      icon: const Icon(Icons.restart_alt),
                      onPressed: () => _confirmReset(device),
                    ),
                    IconButton(
                      tooltip: 'Ativar',
                      icon: const Icon(Icons.check_circle_outline),
                      onPressed: device.isActive
                          ? null
                          : () => _runAction(device, 'activate'),
                    ),
                    IconButton(
                      tooltip: 'Bloquear',
                      icon: const Icon(Icons.block),
                      onPressed: device.isActive
                          ? () => _runAction(device, 'block')
                          : null,
                    ),
                    IconButton(
                      tooltip: 'Associar playlist',
                      icon: const Icon(Icons.playlist_add),
                      onPressed: () => _assign(device),
                    ),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}

class _AssignPlaylistDialog extends StatefulWidget {
  const _AssignPlaylistDialog({required this.api, required this.token});

  final AdminApiClient api;
  final String token;

  @override
  State<_AssignPlaylistDialog> createState() => _AssignPlaylistDialogState();
}

class _AssignPlaylistDialogState extends State<_AssignPlaylistDialog> {
  late Future<List<Playlist>> _future;
  String? _selected;

  @override
  void initState() {
    super.initState();
    _future = widget.api.listPlaylists(widget.token);
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('Associar playlist'),
      content: FutureBuilder<List<Playlist>>(
        future: _future,
        builder: (context, snapshot) {
          if (snapshot.connectionState != ConnectionState.done) {
            return const SizedBox(
              height: 80,
              child: Center(child: CircularProgressIndicator()),
            );
          }

          if (snapshot.hasError) {
            return Text('Erro: ${snapshot.error}');
          }

          final playlists = snapshot.data ?? [];

          if (playlists.isEmpty) {
            return const Text('Nenhuma playlist cadastrada.');
          }

          return DropdownButtonFormField<String>(
            initialValue: _selected,
            items: [
              for (final playlist in playlists)
                DropdownMenuItem(
                  value: playlist.id,
                  child: Text(playlist.name),
                ),
            ],
            onChanged: (value) => setState(() => _selected = value),
            decoration: const InputDecoration(labelText: 'Playlist'),
          );
        },
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('Cancelar'),
        ),
        FilledButton(
          onPressed: _selected == null
              ? null
              : () => Navigator.of(context).pop(_selected),
          child: const Text('Associar'),
        ),
      ],
    );
  }
}
