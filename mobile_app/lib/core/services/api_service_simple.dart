import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiServiceSimple {
  static final ApiServiceSimple _instance = ApiServiceSimple._internal();
  
  factory ApiServiceSimple() {
    return _instance;
  }
  
  ApiServiceSimple._internal();

  // Dynamic base URL based on platform and environment
  String get baseUrl {
    // For development, try multiple possible URLs
    // You can change this based on your testing environment
    
    // Option 1: Android emulator
    // return 'http://10.0.2.2:8000';
    
    // Option 2: iOS simulator or real device on same network
    // Replace with your computer's actual IP address
    return 'http://192.168.29.117:8000'; // Your computer's IP address
    
    // Option 3: If testing on same machine
    // return 'http://localhost:8000';
  }

  // Headers for API requests
  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  };

  // Test connectivity to backend
  Future<bool> testConnection() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
        headers: _headers,
      ).timeout(const Duration(seconds: 5));
      return response.statusCode == 200;
    } catch (e) {
      print('Connection test failed: $e');
      return false;
    }
  }

  // Generic API call handler
  Future<Map<String, dynamic>> _makeRequest(
    String method,
    String endpoint, {
    Map<String, dynamic>? data,
  }) async {
    try {
      final uri = Uri.parse('$baseUrl$endpoint');
      print('🌐 Making $method request to: $uri'); // Debug log
      
      http.Response response;

      switch (method.toUpperCase()) {
        case 'GET':
          response = await http.get(uri, headers: _headers)
              .timeout(const Duration(seconds: 10));
          break;
        case 'POST':
          print('📤 POST data: ${data != null ? json.encode(data) : 'null'}'); // Debug log
          response = await http.post(
            uri,
            headers: _headers,
            body: data != null ? json.encode(data) : null,
          ).timeout(const Duration(seconds: 10));
          break;
        case 'PUT':
          print('📤 PUT data: ${data != null ? json.encode(data) : 'null'}'); // Debug log
          response = await http.put(
            uri,
            headers: _headers,
            body: data != null ? json.encode(data) : null,
          ).timeout(const Duration(seconds: 10));
          break;
        case 'DELETE':
          response = await http.delete(uri, headers: _headers)
              .timeout(const Duration(seconds: 10));
          break;
        default:
          throw Exception('Unsupported HTTP method: $method');
      }

      print('📥 Response status: ${response.statusCode}'); // Debug log
      print('📥 Response body: ${response.body.length > 500 ? '${response.body.substring(0, 500)}...' : response.body}'); // Debug log

      if (response.statusCode >= 200 && response.statusCode < 300) {
        if (response.body.isEmpty) {
          return {'success': true, 'data': null};
        }
        try {
          final jsonResponse = json.decode(response.body);
          return {'success': true, 'data': jsonResponse};
        } catch (e) {
          print('❌ JSON decode error: $e');
          return {'success': true, 'data': response.body};
        }
      } else {
        print('❌ HTTP Error ${response.statusCode}: ${response.body}');
        throw Exception('HTTP ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      print('❌ API Error: $e');
      if (e.toString().contains('Failed to fetch') || e.toString().contains('SocketException')) {
        return {
          'success': false,
          'error': 'Network connection failed. Please check if the backend is running at $baseUrl',
          'data': null,
        };
      }
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
