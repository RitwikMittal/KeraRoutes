import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiServiceSimple {
  static final ApiServiceSimple _instance = ApiServiceSimple._internal();
  
  factory ApiServiceSimple() {
    return _instance;
  }
  
  ApiServiceSimple._internal();

  final String baseUrl = 'http://10.0.2.2:8000'; // Android emulator localhost
  // For iOS simulator, use: 'http://localhost:8000'
  // For real device, use your computer's IP: 'http://192.168.1.X:8000'

  // Headers for API requests
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Generic API call handler
  Future<Map<String, dynamic>> _makeRequest(
    String method,
    String endpoint, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      http.Response response;

      switch (method.toUpperCase()) {
        case 'GET':
          response = await http.get(uri, headers: _headers);
          break;
        case 'POST':
          response = await http.post(
            uri,
            headers: _headers,
            body: data != null ? json.encode(data) : null,
          );
          break;
        case 'PUT':
          response = await http.put(
            uri,
            headers: _headers,
            body: data != null ? json.encode(data) : null,
          );
          break;
        case 'DELETE':
          response = await http.delete(uri, headers: _headers);
          break;
        default:
          throw Exception('Unsupported HTTP method: $method');
      }

      if (response.statusCode >= 200 && response.statusCode < 300) {
        if (response.body.isEmpty) {
          return {'success': true, 'data': null};
        }
        return json.decode(response.body);
      } else {
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      print('API Error: $e');
      return {
        'success': false,
        'error': e.toString(),
        'data': null,
      };
    }
  }

  // Trip APIs
  Future<Map<String, dynamic>> createTrip(Map<String, dynamic> tripData) async {
    return await _makeRequest('POST', '/api/v1/trips', data: tripData);
  }

  Future<Map<String, dynamic>> getTrips() async {
    return await _makeRequest('GET', '/api/v1/trips');
  }

  Future<Map<String, dynamic>> getTripById(String tripId) async {
    return await _makeRequest('GET', '/api/v1/trips/$tripId');
  }

  // Food APIs
  Future<Map<String, dynamic>> createFoodEntry(Map<String, dynamic> foodData) async {
    return await _makeRequest('POST', '/api/v1/food', data: foodData);
  }

  Future<Map<String, dynamic>> getFoodEntries() async {
    return await _makeRequest('GET', '/api/v1/food');
  }

  Future<Map<String, dynamic>> getFoodEntryById(String foodId) async {
    return await _makeRequest('GET', '/api/v1/food/$foodId');
  }

  // Analytics APIs
  Future<Map<String, dynamic>> getDashboardSummary() async {
    return await _makeRequest('GET', '/api/v1/analytics/dashboard-summary');
  }

  Future<Map<String, dynamic>> getTripAnalytics() async {
    return await _makeRequest('GET', '/api/v1/analytics/trips');
  }

  Future<Map<String, dynamic>> getFoodAnalytics() async {
    return await _makeRequest('GET', '/api/v1/analytics/food');
  }

  // User Profile APIs
  Future<Map<String, dynamic>> getUserProfile() async {
    return await _makeRequest('GET', '/api/v1/profile');
  }

  Future<Map<String, dynamic>> updateUserProfile(Map<String, dynamic> profileData) async {
    return await _makeRequest('PUT', '/api/v1/profile', data: profileData);
  }

  // Health check
  Future<bool> checkConnection() async {
    try {
      final response = await _makeRequest('GET', '/health');
      return response['success'] == true;
    } catch (e) {
      return false;
    }
  }
}
