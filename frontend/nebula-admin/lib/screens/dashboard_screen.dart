import 'package:flutter/material.dart';

import '../api/admin_api_client.dart';
import '../models/auth_session.dart';
import '../models/playlist.dart';
import 'devices_screen.dart';

class DashboardScreen extends StatefulWidget {
  const DashboardScreen({super.key, required this.session});

  final AuthSession session;

  @override
  State<DashboardScreen> createState() => _DashboardScreenState();
}

class _DashboardScreenState extends State<DashboardScreen> {
  final AdminApiClient _api = AdminApiClient();
  late Future<List<Playlist>> _future;

  @override
  void initState() {
    super.initState();
    _future = _api.listPlaylists(widget.session.accessToken);
  }

  void _refresh() {
    setState(() {
      _future = _api.listPlaylists(widget.session.accessToken);
    });
  }

  Future<void> _createPlaylist() async {
    final created = await showDialog<Playlist>(
      context: context,
      builder: (_) => _PlaylistForm(
        api: _api,
        token: widget.session.accessToken,
      ),
    );

    if (created != null) _refresh();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Nebula Admin — ${widget.session.email}'),
        actions: [
          IconButton(
            icon: const Icon(Icons.devices),
            tooltip: 'Devices',
            onPressed: () => Navigator.of(context).push(
              MaterialPageRoute(
                builder: (_) => DevicesScreen(session: widget.session),
              ),
            ),
          ),
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _refresh,
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _createPlaylist,
        icon: const Icon(Icons.add),
        label: const Text('Nova playlist'),
      ),
      body: _PlaylistsList(future: _future),
    );
  }
}

class _PlaylistsList extends StatelessWidget {
  const _PlaylistsList({required this.future});

  final Future<List<Playlist>> future;

  @override
  Widget build(BuildContext context) {
    return FutureBuilder<List<Playlist>>(
      future: future,
      builder: (context, snapshot) {
        if (snapshot.connectionState != ConnectionState.done) {
          return const Center(child: CircularProgressIndicator());
        }

        if (snapshot.hasError) {
          return Center(child: Text('Erro: ${snapshot.error}'));
        }

        final playlists = snapshot.data ?? [];

        if (playlists.isEmpty) {
          return const Center(child: Text('Nenhuma playlist cadastrada.'));
        }

        return ListView.separated(
          itemCount: playlists.length,
          separatorBuilder: (_, __) => const Divider(height: 1),
          itemBuilder: (context, index) {
            final playlist = playlists[index];
            return ListTile(
              title: Text(playlist.name),
              subtitle: Text(playlist.sourceUrl),
              trailing: Chip(label: Text(playlist.status)),
            );
          },
        );
      },
    );
  }
}

class _PlaylistForm extends StatefulWidget {
  const _PlaylistForm({required this.api, required this.token});

  final AdminApiClient api;
  final String token;

  @override
  State<_PlaylistForm> createState() => _PlaylistFormState();
}

class _PlaylistFormState extends State<_PlaylistForm> {
  final TextEditingController _name = TextEditingController();
  final TextEditingController _sourceUrl = TextEditingController();
  String _format = 'm3u';
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
      final created = await widget.api.createPlaylist(
        widget.token,
        _name.text,
        _format,
        _sourceUrl.text,
      );

      if (!mounted) return;
      Navigator.of(context).pop(created);
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
      title: const Text('Nova playlist'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          TextField(
            controller: _name,
            decoration: const InputDecoration(labelText: 'Nome'),
          ),
          const SizedBox(height: 12),
          DropdownButtonFormField<String>(
            initialValue: _format,
            items: const [
              DropdownMenuItem(value: 'm3u', child: Text('m3u')),
            ],
            onChanged: (value) {
              if (value != null) setState(() => _format = value);
            },
            decoration: const InputDecoration(labelText: 'Formato'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _sourceUrl,
            decoration: const InputDecoration(labelText: 'URL da playlist'),
          ),
          if (_error != null) ...[
            const SizedBox(height: 12),
            Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error)),
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
          child: _loading
              ? const SizedBox(
                  height: 18,
                  width: 18,
                  child: CircularProgressIndicator(strokeWidth: 2),
                )
              : const Text('Criar'),
        ),
      ],
    );
  }
}
