import 'package:flutter_test/flutter_test.dart';
import 'package:nebula_player/utils/search.dart';

void main() {
  group('normalizeForSearch', () {
    test('remove acentos e coloca em minusculas', () {
      expect(normalizeForSearch('Órfãos da Terra'), 'orfaos da terra');
      expect(normalizeForSearch('Ação'), 'acao');
    });

    test('ignora espacos nas pontas', () {
      expect(normalizeForSearch('  Matrix  '), 'matrix');
    });
  });

  group('matchesSearch', () {
    test('termo vazio combina com tudo', () {
      expect(matchesSearch('Qualquer Filme', ''), isTrue);
      expect(matchesSearch('Qualquer Filme', '   '), isTrue);
    });

    test('encontra ignorando maiusculas/minusculas', () {
      expect(matchesSearch('O Poderoso Chefao', 'poderoso'), isTrue);
      expect(matchesSearch('O Poderoso Chefao', 'PODEROSO'), isTrue);
    });

    test('encontra ignorando acentos', () {
      expect(matchesSearch('Órfãos da Terra', 'orfaos'), isTrue);
      expect(matchesSearch('Ação Explosiva', 'acao'), isTrue);
      expect(matchesSearch('Orfaos da Terra', 'órfãos'), isTrue);
    });

    test('todos os termos precisam aparecer, em qualquer ordem', () {
      expect(matchesSearch('Star Wars: Uma Nova Esperanca', 'wars star'), isTrue);
      expect(matchesSearch('Star Wars: Uma Nova Esperanca', 'star trek'), isFalse);
    });

    test('nao encontra quando o termo nao existe', () {
      expect(matchesSearch('Matrix', 'avatar'), isFalse);
    });

    test('casa com parte do titulo', () {
      expect(matchesSearch('Velozes e Furiosos 10', 'furios'), isTrue);
    });
  });
}
