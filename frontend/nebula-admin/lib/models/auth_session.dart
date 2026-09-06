class AuthSession {
  AuthSession({
    required this.accessToken,
    required this.adminId,
    required this.email,
    required this.role,
  });

  final String accessToken;
  final String adminId;
  final String email;
  final String role;

  factory AuthSession.fromJson(Map<String, dynamic> json) => AuthSession(
        accessToken: json['access_token'] as String,
        adminId: json['admin_id'] as String,
        email: json['email'] as String,
        role: json['role'] as String,
      );
}
