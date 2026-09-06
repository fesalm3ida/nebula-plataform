class M3uChannel {
  const M3uChannel({
    required this.name,
    this.group,
    this.logo,
    this.streamUrl,
    this.originalIndex = 0,
  });

  final String name;
  final String? group;
  final String? logo;
  final String? streamUrl;
  final int originalIndex;

  String get displayName => name.isEmpty ? (streamUrl ?? 'Canal') : name;
}
