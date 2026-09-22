import 'package:flutter/services.dart';

/// Máscara de MAC Address: insere `:` a cada dois caracteres enquanto o
/// usuário digita.
///
/// São **6 duplas** de caracteres hexadecimais separadas por **5** dois-pontos:
/// `02:C4:E0:F9:65:30`.
///
/// Aceita também o texto colado sem separadores (`02c4e0f96530`) e normaliza
/// para maiúsculas.
class MacAddressInputFormatter extends TextInputFormatter {
  const MacAddressInputFormatter();

  /// 6 duplas de 2 caracteres.
  static const int hexDigits = 12;

  static final RegExp _nonHex = RegExp(r'[^0-9a-fA-F]');

  @override
  TextEditingValue formatEditUpdate(
    TextEditingValue oldValue,
    TextEditingValue newValue,
  ) {
    var digits = newValue.text.replaceAll(_nonHex, '');

    if (digits.length > hexDigits) {
      digits = digits.substring(0, hexDigits);
    }

    final buffer = StringBuffer();

    for (var index = 0; index < digits.length; index++) {
      if (index > 0 && index.isEven) {
        buffer.write(':');
      }

      buffer.write(digits[index].toUpperCase());
    }

    final text = buffer.toString();

    return TextEditingValue(
      text: text,
      selection: TextSelection.collapsed(offset: text.length),
    );
  }
}
