import 'package:flutter/material.dart';

import '../theme/nebula_theme.dart';

/// Campo de busca por título (usado em Filmes e Séries).
class TitleSearchField extends StatefulWidget {
  const TitleSearchField({
    super.key,
    required this.onChanged,
    this.hintText = 'Buscar por título',
  });

  final ValueChanged<String> onChanged;
  final String hintText;

  @override
  State<TitleSearchField> createState() => _TitleSearchFieldState();
}

class _TitleSearchFieldState extends State<TitleSearchField> {
  final TextEditingController _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  void _clear() {
    _controller.clear();
    widget.onChanged('');
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.fromLTRB(12, 8, 12, 0),
      child: TextField(
        controller: _controller,
        onChanged: (value) {
          widget.onChanged(value);
          setState(() {});
        },
        textInputAction: TextInputAction.search,
        style: const TextStyle(color: NebulaColors.textPrimary),
        decoration: InputDecoration(
          hintText: widget.hintText,
          hintStyle: const TextStyle(color: NebulaColors.textSecondary),
          prefixIcon: const Icon(
            Icons.search,
            color: NebulaColors.textSecondary,
          ),
          suffixIcon: _controller.text.isEmpty
              ? null
              : IconButton(
                  tooltip: 'Limpar',
                  icon: const Icon(
                    Icons.close,
                    color: NebulaColors.textSecondary,
                  ),
                  onPressed: _clear,
                ),
          isDense: true,
          filled: true,
          fillColor: NebulaColors.surface,
          border: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: NebulaColors.surfaceBorder),
          ),
          enabledBorder: OutlineInputBorder(
            borderRadius: BorderRadius.circular(12),
            borderSide: const BorderSide(color: NebulaColors.surfaceBorder),
          ),
        ),
      ),
    );
  }
}
