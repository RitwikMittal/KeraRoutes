import 'package:flutter/material.dart';
import '../../core/services/api_service_simple.dart';

class ConnectionTestWidget extends StatefulWidget {
  const ConnectionTestWidget({super.key});

  @override
  State<ConnectionTestWidget> createState() => _ConnectionTestWidgetState();
}

class _ConnectionTestWidgetState extends State<ConnectionTestWidget> {
  final ApiServiceSimple _apiService = ApiServiceSimple();
  bool _isLoading = false;
  String? _result;

  Future<void> _testConnection() async {
    setState(() {
      _isLoading = true;
      _result = null;
    });

    try {
      // Test basic connectivity
      final isConnected = await _apiService.testConnection();
      
      if (isConnected) {
        // Test API endpoints
        final results = await Future.wait([
          _apiService.getDashboardSummary(),
          _apiService.getTrips(),
          _apiService.getFoodEntries(),
        ]);

        bool allSuccess = results.every((result) => result['success'] == true);
        
        setState(() {
          _result = allSuccess 
              ? '✅ All API endpoints working correctly!'
              : '⚠️ Some endpoints failed:\n${results.map((r) => r['error'] ?? 'Success').join('\n')}';
        });
      } else {
        setState(() {
          _result = '❌ Cannot connect to backend at ${_apiService.baseUrl}';
        });
      }
    } catch (e) {
      setState(() {
        _result = '❌ Connection failed: $e';
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              '🔗 API Connection Test',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            Text(
              'Backend URL: ${_apiService.baseUrl}',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _testConnection,
              child: _isLoading
                  ? const Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(
                          width: 16,
                          height: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 8),
                        Text('Testing...'),
                      ],
                    )
                  : const Text('Test Connection'),
            ),
            if (_result != null) ...[
              const SizedBox(height: 16),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: _result!.startsWith('✅') 
                      ? Colors.green.withOpacity(0.1)
                      : Colors.red.withOpacity(0.1),
                  borderRadius: BorderRadius.circular(8),
                  border: Border.all(
                    color: _result!.startsWith('✅') 
                        ? Colors.green
                        : Colors.red,
                  ),
                ),
                child: Text(
                  _result!,
                  style: TextStyle(
                    color: _result!.startsWith('✅') 
                        ? Colors.green.shade700
                        : Colors.red.shade700,
                    fontFamily: 'monospace',
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }
}
