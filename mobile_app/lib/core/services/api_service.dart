// Original implementation with HTTP client
/*
import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  static final ApiService _instance = ApiService._internal();
  final http.Client _client = http.Client();
  
  factory ApiService() {
    return _instance;
  }
  
  ApiService._internal();

  String? _authToken;
  final String baseUrl = 'http://localhost:8000';
  
  Future<void> initialize() async {
    _authToken = await _loadStoredToken();
  }
  
  Future<void> setAuthToken(String token) async {
    _authToken = token;
    await _storeToken(token);
  }
  
  Future<void> clearAuthToken() async {
    _authToken = null;
    await _clearStoredToken();
  }

  String? get authToken => _authToken;
  bool get isAuthenticated => _authToken != null;
*/

// Simplified implementation for initial setup
class ApiService {
  static final ApiService _instance = ApiService._internal();
  
  factory ApiService() {
    return _instance;
  }
  
  ApiService._internal();

  String? _authToken;
  final String baseUrl = 'http://localhost:8000';
  
  Future<void> initialize() async {
    _authToken = null; // For development
  }
  
  Future<void> setAuthToken(String token) async {
    _authToken = token;
  }
  
  Future<void> clearAuthToken() async {
    _authToken = null;
  }

  String? get authToken => _authToken;
  bool get isAuthenticated => _authToken != null;

  // Original API methods
  /*
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'password': password,
      }),
    );
    return _handleResponse(response);
  }
  */

  // Original API methods with HTTP implementation
  /*
  Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/auth/login'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'email': email,
        'password': password,
      }),
    );
    return _handleResponse(response);
  }

  Future<Map<String, dynamic>> createTrip(TripData tripData) async {
    final response = await _client.post(
      Uri.parse('$baseUrl/trips'),
      headers: _getHeaders(),
      body: json.encode(tripData.toJson()),
    );
    return _handleResponse(response);
  }
  */

  // Simulated API calls for development
  Future<Map<String, dynamic>> login(String email, String password) async {
    await Future.delayed(const Duration(milliseconds: 500));
    _authToken = 'dummy_token';
    return {'token': _authToken};
  }

  Future<List<Map<String, dynamic>>> getUserTrips() async {
    await Future.delayed(const Duration(milliseconds: 500));
    return [
      {
        'id': '1',
        'purpose': 'Work',
        'distance': 5.2,
        'duration': 30,
        'cost': 50.0,
      },
      {
        'id': '2',
        'purpose': 'Shopping',
        'distance': 8.5,
        'duration': 45,
        'cost': 100.0,
      },
    ];
  }
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('auth_token');
  }
  
  // Get headers with auth token
  static Map<String, String> _getHeaders({bool includeAuth = true}) {
    final headers = {
      'Content-Type': 'application/json',
    };
    
    if (includeAuth && _authToken != null) {
      headers['Authorization'] = 'Bearer $_authToken';
    }
    
    return headers;
  }
  
  // Authentication APIs
  static Future<Map<String, dynamic>> register(UserRegistration userData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/register'),
      headers: _getHeaders(includeAuth: false),
      body: json.encode(userData.toJson()),
    );
    
    return _handleResponse(response);
  }
  static Future<Map<String, dynamic>> login(String email, String password) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/auth/login'),
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      body: 'username=$email&password=$password',
    );
   
    final result = _handleResponse(response);
    if (result['success'] && result['data']['access_token'] != null) {
      await setAuthToken(result['data']['access_token']);
    }
    
    return result;
  }
  
  static Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/auth/me'),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  // Trip APIs
  static Future<Map<String, dynamic>> createTrip(TripData tripData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/trips/'),
      headers: _getHeaders(),
      body: json.encode(tripData.toJson()),
    );
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> getUserTrips({int skip = 0, int limit = 10}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/trips/?skip=$skip&limit=$limit'),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> uploadReceipt(File imageFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/trips/upload-receipt'),
    );
    
    request.headers.addAll(_getHeaders());
    request.files.add(await http.MultipartFile.fromPath(
      'file',
      imageFile.path,
    ));
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> getPersonalTripAnalytics({int days = 30}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/trips/analytics/personal?days=$days'),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  // Food APIs
  static Future<Map<String, dynamic>> createFoodEntry(FoodConsumption foodData) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/food/'),
      headers: _getHeaders(),
      body: json.encode(foodData.toJson()),
    );
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> getUserFoodEntries({int skip = 0, int limit = 20, int? days}) async {
    String url = '$baseUrl/api/food/?skip=$skip&limit=$limit';
    if (days != null) {
      url += '&days=$days';
    }
    
    final response = await http.get(
      Uri.parse(url),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> uploadFoodBill(File imageFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/food/upload-bill'),
    );
    
    request.headers.addAll(_getHeaders());
    request.files.add(await http.MultipartFile.fromPath(
      'file',
      imageFile.path,
    ));
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> uploadFoodPhoto(File imageFile) async {
    var request = http.MultipartRequest(
      'POST',
      Uri.parse('$baseUrl/api/food/upload-food-photo'),
    );
    
    request.headers.addAll(_getHeaders());
    request.files.add(await http.MultipartFile.fromPath(
      'file',
      imageFile.path,
    ));
    
    final streamedResponse = await request.send();
    final response = await http.Response.fromStream(streamedResponse);
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> getFoodRecommendations(double lat, double lng, {String? cuisineType, double? budgetMax}) async {
    String url = '$baseUrl/api/food/recommendations/nearby?lat=$lat&lng=$lng';
    if (cuisineType != null) url += '&cuisine_type=$cuisineType';
    if (budgetMax != null) url += '&budget_max=$budgetMax';
    
    final response = await http.get(
      Uri.parse(url),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> getPersonalFoodAnalytics({int days = 30}) async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/food/analytics/personal?days=$days'),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  // Gamification APIs
  static Future<Map<String, dynamic>> getUserPoints() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/gamification/points'),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  static Future<Map<String, dynamic>> getUserBadges() async {
    final response = await http.get(
      Uri.parse('$baseUrl/api/gamification/badges'),
      headers: _getHeaders(),
    );
    
    return _handleResponse(response);
  }
  
  // Helper method to handle HTTP responses
  static Map<String, dynamic> _handleResponse(http.Response response) {
    try {
      final Map<String, dynamic> data = json.decode(response.body);
      
      if (response.statusCode >= 200 && response.statusCode < 300) {
        return {
          'success': true,
          'data': data,
          'statusCode': response.statusCode,
        };
      } else {
        return {
          'success': false,
          'error': data['detail'] ?? 'Unknown error occurred',
          'statusCode': response.statusCode,
        };
      }
    } catch (e) {
      return {
        'success': false,
        'error': 'Failed to parse response: ${e.toString()}',
        'statusCode': response.statusCode,
      };
    }
  }
  }