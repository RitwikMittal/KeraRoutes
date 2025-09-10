import 'package:flutter/foundation.dart';

class AuthProvider with ChangeNotifier {
  bool _isAuthenticated = true; // Set to true for development

  bool get isAuthenticated => _isAuthenticated;

  Future<void> login(String email, String password) async {
    _isAuthenticated = true;
    notifyListeners();
  }

  void logout() {
    _isAuthenticated = false;
    notifyListeners();
  }
}
