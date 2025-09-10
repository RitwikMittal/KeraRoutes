// mobile_app/lib/core/models/user_model.dart
class UserRegistration {
  final String email;
  final String password;
  final String fullName;
  final String? phoneNumber;
  final String userType;
  final String preferredLanguage;
  final String? ageGroup;
  final String? location;
  final bool consentDataCollection;
  final bool consentResearchUse;

  UserRegistration({
    required this.email,
    required this.password,
    required this.fullName,
    this.phoneNumber,
    this.userType = 'tourist',
    this.preferredLanguage = 'english',
    this.ageGroup,
    this.location,
    this.consentDataCollection = true,
    this.consentResearchUse = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'email': email,
      'password': password,
      'full_name': fullName,
      'phone_number': phoneNumber,
      'user_type': userType,
      'preferred_language': preferredLanguage,
      'age_group': ageGroup,
      'location': location,
      'consent_data_collection': consentDataCollection,
      'consent_research_use': consentResearchUse,
    };
  }
}

class User {
  final String userId;
  final String email;
  final String fullName;
  final String userType;
  final String preferredLanguage;
  final bool isActive;
  final DateTime createdAt;
  final int gamificationScore;
  final List<String> badgesEarned;

  User({
    required this.userId,
    required this.email,
    required this.fullName,
    required this.userType,
    required this.preferredLanguage,
    required this.isActive,
    required this.createdAt,
    this.gamificationScore = 0,
    this.badgesEarned = const [],
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      userId: json['user_id'] ?? '',
      email: json['email'] ?? '',
      fullName: json['full_name'] ?? '',
      userType: json['user_type'] ?? 'tourist',
      preferredLanguage: json['preferred_language'] ?? 'english',
      isActive: json['is_active'] ?? true,
      createdAt: DateTime.parse(json['created_at'] ?? DateTime.now().toIso8601String()),
      gamificationScore: json['gamification_score'] ?? 0,
      badgesEarned: List<String>.from(json['badges_earned'] ?? []),
    );
  }
}