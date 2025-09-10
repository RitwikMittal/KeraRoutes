// mobile_app/lib/core/constants/api_endpoints.dart
class ApiEndpoints {
  static const String baseUrl = 'http://localhost:8000';
  
  // Auth endpoints
  static const String register = '/api/auth/register';
  static const String login = '/api/auth/login';
  static const String me = '/api/auth/me';
  
  // Trip endpoints
  static const String trips = '/api/trips/';
  static const String uploadReceipt = '/api/trips/upload-receipt';
  static const String tripAnalytics = '/api/trips/analytics/personal';
  
  // Food endpoints
  static const String food = '/api/food/';
  static const String uploadBill = '/api/food/upload-bill';
  static const String uploadFoodPhoto = '/api/food/upload-food-photo';
  static const String foodRecommendations = '/api/food/recommendations/nearby';
  static const String foodAnalytics = '/api/food/analytics/personal';
  
  // Gamification endpoints
  static const String points = '/api/gamification/points';
  static const String badges = '/api/gamification/badges';
}