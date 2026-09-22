import 'package:flutter/services.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:nebula_admin_ui/widgets/mac_address_input_formatter.dart';

/// Simula a digitacao caractere a caractere, como o usuario faria.
String digitar(String digitos) {
  const formatter = MacAddressInputFormatter();
  var value = const TextEditingValue();

  for (final char in digitos.split('')) {
    value = formatter.formatEditUpdate(
      value,
      TextEditingValue(
        text: value.text + char,
        selection: TextSelection.collapsed(offset: value.text.length + 1),
      ),
    );
  }

  return value.text;
}

void main() {
  const formatter = MacAddressInputFormatter();

  TextEditingValue formatar(String texto) => formatter.formatEditUpdate(
        TextEditingValue.empty,
        TextEditingValue(text: texto),
      );

  test('insere ":" a cada duas duplas digitadas', () {
    expect(digitar('0'), '0');
    expect(digitar('02'), '02');
    expect(digitar('02c'), '02:C');
    expect(digitar('02c4'), '02:C4');
    expect(digitar('02c4e'), '02:C4:E');
    expect(digitar('02c4e0f96530'), '02:C4:E0:F9:65:30');
  });

  test('resultado final tem 6 duplas e 5 dois-pontos', () {
    final mac = digitar('02c4e0f96530');

    expect(mac.split(':').length, 6);
    expect(':'.allMatches(mac).length, 5);
    expect(mac.length, 17);
  });

  test('normaliza para maiusculas', () {
    expect(formatar('02:c4:e0:f9:65:30').text, '02:C4:E0:F9:65:30');
  });

  test('aceita texto colado sem separadores', () {
    expect(formatar('02c4e0f96530').text, '02:C4:E0:F9:65:30');
  });

  test('descarta caracteres invalidos', () {
    expect(formatar('02-C4 E0.F9_65-30').text, '02:C4:E0:F9:65:30');
    expect(formatar('zz02c4').text, '02:C4');
  });

  test('limita a 12 digitos hexadecimal', () {
    expect(formatar('02c4e0f96530abcd').text, '02:C4:E0:F9:65:30');
    expect(formatar('02c4e0f96530abcd').text.length, 17);
  });

  test('o cursor fica no fim do texto formatado', () {
    final value = formatter.formatEditUpdate(
      TextEditingValue.empty,
      const TextEditingValue(text: '02c4'),
    );

    expect(value.selection.baseOffset, value.text.length);
  });
}
