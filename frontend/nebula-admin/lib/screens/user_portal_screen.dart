import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

import '../api/portal_api_client.dart';
import '../models/portal.dart';

enum _PortalSection { playlist, activate }

/// Portal do **usuário** (layout inspirado no painel do Ibo Player):
/// cabeçalho com os dados do aparelho, menu lateral e área de listas.
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
  _PortalSection _section = _PortalSection.playlist;

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
      var device = await widget.api.device(widget.session.accessToken);

      // Se ha licenca pendente/expirada, confirma pagamentos no provedor.
      if (device.license.isPending || device.license.expired) {
        try {
          device = await widget.api.syncPayments(
            widget.session.accessToken,
          );
        } catch (_) {
          // Apenas nao confirmou agora.
        }
      }

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
        title: const Text('Nebula Player'),
        actions: [
          IconButton(
            tooltip: 'Verificar pagamento',
            icon: const Icon(Icons.receipt_long),
            onPressed: _load,
          ),
          IconButton(icon: const Icon(Icons.refresh), onPressed: _load),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(child: Text('Erro: $_error'))
              : Column(
                  children: [
                    _DeviceHeader(
                      license: _device!.license,
                      macAddress: widget.session.macAddress,
                    ),
                    const Divider(height: 1),
                    Expanded(
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _Sidebar(
                            section: _section,
                            onSelect: (section) =>
                                setState(() => _section = section),
                            onLogout: () => Navigator.of(context).pop(),
                          ),
                          Expanded(
                            child: _section == _PortalSection.playlist
                                ? _PlaylistPanel(
                                    playlist: _device!.playlist,
                                    onAdd: _registerPlaylist,
                                  )
                                : _ActivatePanel(
                                    api: widget.api,
                                    token: widget.session.accessToken,
                                    license: _device!.license,
                                    onActivate: _activate,
                                  ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
    );
  }
}

/// Cabeçalho com a identificação do aparelho (MAC, status e expiração).
class _DeviceHeader extends StatelessWidget {
  const _DeviceHeader({required this.license, required this.macAddress});

  final PortalLicense license;
  final String macAddress;

  static String formatDate(String? iso) {
    if (iso == null || iso.isEmpty) {
      return '—';
    }

    final parsed = DateTime.tryParse(iso);

    if (parsed == null) {
      return iso;
    }

    final local = parsed.toLocal();
    final day = local.day.toString().padLeft(2, '0');
    final month = local.month.toString().padLeft(2, '0');

    return '$day/$month/${local.year}';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Container(
      width: double.infinity,
      color: theme.colorScheme.surfaceContainerLow,
      padding: const EdgeInsets.fromLTRB(24, 20, 24, 16),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Sua lista de reprodução',
                  style: theme.textTheme.headlineSmall,
                ),
                const SizedBox(height: 4),
                Text(
                  'Gerencie o aparelho e o conteúdo dele.',
                  style: theme.textTheme.bodyMedium,
                ),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              _InfoLine(
                label: 'Mac Address',
                value: macAddress.isEmpty ? '—' : macAddress,
              ),
              _InfoLine(
                label: 'Status',
                value: license.label.split('—').first.trim(),
              ),
              _InfoLine(
                label: 'Expiração',
                value: license.isLifetime
                    ? 'Sem expiração'
                    : formatDate(license.expiresAt),
              ),
            ],
          ),
        ],
      ),
    );
  }
}

class _InfoLine extends StatelessWidget {
  const _InfoLine({required this.label, required this.value});

  final String label;
  final String value;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 2),
      child: RichText(
        text: TextSpan(
          style: Theme.of(context).textTheme.bodyMedium,
          children: [
            TextSpan(
              text: '$label: ',
              style: const TextStyle(fontWeight: FontWeight.w600),
            ),
            TextSpan(text: value),
          ],
        ),
      ),
    );
  }
}

/// Menu lateral: Playlist · Ativar · Sair.
class _Sidebar extends StatelessWidget {
  const _Sidebar({
    required this.section,
    required this.onSelect,
    required this.onLogout,
  });

  final _PortalSection section;
  final ValueChanged<_PortalSection> onSelect;
  final VoidCallback onLogout;

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 200,
      color: Theme.of(context).colorScheme.surfaceContainerHighest,
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          _SidebarButton(
            label: 'Playlist',
            icon: Icons.playlist_play,
            selected: section == _PortalSection.playlist,
            onPressed: () => onSelect(_PortalSection.playlist),
          ),
          const SizedBox(height: 8),
          _SidebarButton(
            label: 'Ativar',
            icon: Icons.verified_user_outlined,
            selected: section == _PortalSection.activate,
            onPressed: () => onSelect(_PortalSection.activate),
          ),
          const SizedBox(height: 8),
          _SidebarButton(
            label: 'Sair',
            icon: Icons.logout,
            onPressed: onLogout,
          ),
        ],
      ),
    );
  }
}

class _SidebarButton extends StatelessWidget {
  const _SidebarButton({
    required this.label,
    required this.icon,
    required this.onPressed,
    this.selected = false,
  });

  final String label;
  final IconData icon;
  final VoidCallback onPressed;
  final bool selected;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;

    return Material(
      color: selected ? scheme.primary : scheme.surfaceContainerHigh,
      borderRadius: BorderRadius.circular(8),
      child: InkWell(
        onTap: onPressed,
        borderRadius: BorderRadius.circular(8),
        child: Padding(
          padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 14),
          child: Row(
            children: [
              Icon(
                icon,
                size: 20,
                color: selected ? scheme.onPrimary : scheme.onSurface,
              ),
              const SizedBox(width: 10),
              Text(
                label,
                style: TextStyle(
                  fontWeight: FontWeight.w600,
                  color: selected ? scheme.onPrimary : scheme.onSurface,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

/// Painel de listas: botão de adicionar + tabela (Nome | URL).
class _PlaylistPanel extends StatelessWidget {
  const _PlaylistPanel({required this.playlist, required this.onAdd});

  final PortalPlaylist? playlist;
  final VoidCallback onAdd;

  @override
  Widget build(BuildContext context) {
    final current = playlist;

    return Padding(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              FilledButton.icon(
                onPressed: onAdd,
                icon: const Icon(Icons.add),
                label: Text(
                  current == null ? 'Add Playlist' : 'Trocar Playlist',
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          Card(
            clipBehavior: Clip.antiAlias,
            child: Column(
              children: [
                Container(
                  color: Theme.of(context).colorScheme.primaryContainer,
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 12,
                  ),
                  child: const Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: Text(
                          'Nome',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                      Expanded(
                        flex: 5,
                        child: Text(
                          'URL',
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                      ),
                    ],
                  ),
                ),
                if (current == null)
                  const Padding(
                    padding: EdgeInsets.all(24),
                    child: Text('Nenhuma lista cadastrada.'),
                  )
                else
                  Padding(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 16,
                      vertical: 14,
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          flex: 2,
                          child: Text(current.name),
                        ),
                        Expanded(
                          flex: 5,
                          child: Text(
                            current.sourceUrl,
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

/// Painel de ativação/licença: status, trial e planos de compra.
class _ActivatePanel extends StatefulWidget {
  const _ActivatePanel({
    required this.api,
    required this.token,
    required this.license,
    required this.onActivate,
  });

  final PortalApiClient api;
  final String token;
  final PortalLicense license;
  final Future<void> Function() onActivate;

  @override
  State<_ActivatePanel> createState() => _ActivatePanelState();
}

class _ActivatePanelState extends State<_ActivatePanel> {
  late Future<List<PortalPlan>> _plans;

  @override
  void initState() {
    super.initState();
    _plans = widget.api.listPlans(widget.token);
  }

  Future<void> _buy(PortalPlan plan) async {
    try {
      final checkoutUrl = await widget.api.purchase(
        widget.token,
        plan.product,
      );

      final uri = Uri.parse(checkoutUrl);

      if (!await launchUrl(uri, mode: LaunchMode.externalApplication)) {
        throw PortalApiException('Não foi possível abrir o checkout.');
      }
    } catch (error) {
      if (!mounted) return;

      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text('$error'),
          backgroundColor: Theme.of(context).colorScheme.error,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final license = widget.license;

    return Padding(
      padding: const EdgeInsets.all(20),
      child: ListView(
        children: [
          Card(
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
                  if (license.isPending) ...[
                    const SizedBox(height: 16),
                    FilledButton.icon(
                      onPressed: widget.onActivate,
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
          ),
          const SizedBox(height: 16),
          const Text(
            'Comprar licença',
            style: TextStyle(fontWeight: FontWeight.bold, fontSize: 16),
          ),
          const SizedBox(height: 8),
          FutureBuilder<List<PortalPlan>>(
            future: _plans,
            builder: (context, snapshot) {
              if (snapshot.connectionState != ConnectionState.done) {
                return const Center(child: CircularProgressIndicator());
              }

              if (snapshot.hasError) {
                return Text(
                  'Não foi possível carregar os planos: ${snapshot.error}',
                );
              }

              final plans = snapshot.data ?? [];

              return Column(
                children: [
                  for (final plan in plans)
                    Card(
                      child: ListTile(
                        title: Text(plan.title),
                        subtitle: Text(plan.description),
                        trailing: FilledButton(
                          onPressed: () => _buy(plan),
                          child: Text(plan.priceLabel),
                        ),
                      ),
                    ),
                ],
              );
            },
          ),
        ],
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
        widget.current == null ? 'Add Playlist' : 'Trocar Playlist',
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
