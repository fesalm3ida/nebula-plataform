// Utilidades de busca por título (Filmes e Séries).

const Map<String, String> _accents = {
  'á': 'a', 'à': 'a', 'ã': 'a', 'â': 'a', 'ä': 'a',
  'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
  'í': 'i', 'ì': 'i', 'î': 'i', 'ï': 'i',
  'ó': 'o', 'ò': 'o', 'õ': 'o', 'ô': 'o', 'ö': 'o',
  'ú': 'u', 'ù': 'u', 'û': 'u', 'ü': 'u',
  'ç': 'c', 'ñ': 'n',
  'Á': 'a', 'À': 'a', 'Ã': 'a', 'Â': 'a', 'Ä': 'a',
  'É': 'e', 'È': 'e', 'Ê': 'e', 'Ë': 'e',
  'Í': 'i', 'Ì': 'i', 'Î': 'i', 'Ï': 'i',
  'Ó': 'o', 'Ò': 'o', 'Õ': 'o', 'Ô': 'o', 'Ö': 'o',
  'Ú': 'u', 'Ù': 'u', 'Û': 'u', 'Ü': 'u',
  'Ç': 'c', 'Ñ': 'n',
};

/// Normaliza o texto para comparação: sem acentos, minúsculo e sem espaços
/// nas pontas.
String normalizeForSearch(String value) {
  final buffer = StringBuffer();

  for (final char in value.trim().toLowerCase().split('')) {
    buffer.write(_accents[char] ?? char);
  }

  return buffer.toString();
}

/// Verifica se o [title] corresponde ao [query].
///
/// Um termo vazio combina com tudo. Termos separados por espaço precisam
/// aparecer todos, em qualquer ordem (ex.: "guerra estrelas" encontra
/// "Star Wars: Uma Nova Guerra nas Estrelas").
bool matchesSearch(String title, String query) {
  final term = normalizeForSearch(query);

  if (term.isEmpty) {
    return true;
  }

  final normalizedTitle = normalizeForSearch(title);

  return term
      .split(RegExp(r'\s+'))
      .where((word) => word.isNotEmpty)
      .every(normalizedTitle.contains);
}
