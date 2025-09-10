import 'package:flutter/material.dart';
import '../../../core/services/api_service_simple.dart';

class AnalyticsScreen extends StatefulWidget {
  const AnalyticsScreen({super.key});

  @override
  State<AnalyticsScreen> createState() => _AnalyticsScreenState();
}

class _AnalyticsScreenState extends State<AnalyticsScreen> {
  final ApiServiceSimple _apiService = ApiServiceSimple();
  bool _isLoading = true;
  Map<String, dynamic>? _analyticsData;
  List<dynamic> _recentTrips = [];
  List<dynamic> _recentFood = [];

  @override
  void initState() {
    super.initState();
    _loadAnalytics();
  }

  Future<void> _loadAnalytics() async {
    setState(() {
      _isLoading = true;
    });

    try {
      final results = await Future.wait([
        _apiService.getDashboardSummary(),
        _apiService.getTrips(),
        _apiService.getFoodEntries(),
      ]);

      setState(() {
        _analyticsData = results[0]['data'];
        _recentTrips = results[1]['data'] ?? [];
        _recentFood = results[2]['data'] ?? [];
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _isLoading = false;
      });
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error loading analytics: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('📊 Your Analytics'),
        backgroundColor: Colors.blue[700],
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAnalytics,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: _loadAnalytics,
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    _buildOverviewSection(),
                    const SizedBox(height: 20),
                    _buildRecentTripsSection(),
                    const SizedBox(height: 20),
                    _buildRecentFoodSection(),
                  ],
                ),
              ),
            ),
    );
  }

  Widget _buildOverviewSection() {
    final overview = _analyticsData?['overview'] ?? {};
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '📈 Overview',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Total Trips',
                    '${overview['total_trips'] ?? 0}',
                    Icons.directions_bus,
                    Colors.green,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatCard(
                    'Food Entries',
                    '${overview['total_food_entries'] ?? 0}',
                    Icons.restaurant,
                    Colors.orange,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(
                  child: _buildStatCard(
                    'Transport Spending',
                    '₹${overview['total_transport_spending'] ?? 0}',
                    Icons.currency_rupee,
                    Colors.blue,
                  ),
                ),
                const SizedBox(width: 8),
                Expanded(
                  child: _buildStatCard(
                    'Food Spending',
                    '₹${overview['total_food_spending'] ?? 0}',
                    Icons.fastfood,
                    Colors.red,
                  ),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: color.withOpacity(0.3)),
      ),
      child: Column(
        children: [
          Icon(icon, color: color, size: 24),
          const SizedBox(height: 4),
          Text(
            value,
            style: TextStyle(
              fontSize: 18,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
          Text(
            title,
            style: TextStyle(
              fontSize: 12,
              color: color.withOpacity(0.8),
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }

  Widget _buildRecentTripsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🚌 Recent Trips (${_recentTrips.length})',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            if (_recentTrips.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20.0),
                  child: Text('No trips logged yet. Start logging your trips!'),
                ),
              )
            else
              ..._recentTrips.take(5).map((trip) => _buildTripCard(trip)),
          ],
        ),
      ),
    );
  }

  Widget _buildTripCard(Map<String, dynamic> trip) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.green[100],
          child: Icon(
            Icons.directions_bus,
            color: Colors.green[700],
          ),
        ),
        title: Text(
          '${trip['transport_mode']?.toString().toUpperCase() ?? 'Unknown'} - ${trip['purpose'] ?? 'Unknown'}',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          '${trip['start_location']?['city'] ?? 'Unknown'} → ${trip['end_location']?['city'] ?? 'Unknown'}',
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              '₹${trip['cost'] ?? 0}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              '${trip['number_of_people'] ?? 1} people',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRecentFoodSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              '🍽️ Recent Food Entries (${_recentFood.length})',
              style: Theme.of(context).textTheme.headlineSmall,
            ),
            const SizedBox(height: 16),
            if (_recentFood.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(20.0),
                  child: Text('No food entries yet. Start logging your meals!'),
                ),
              )
            else
              ..._recentFood.take(5).map((food) => _buildFoodCard(food)),
          ],
        ),
      ),
    );
  }

  Widget _buildFoodCard(Map<String, dynamic> food) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: Colors.orange[100],
          child: Icon(
            Icons.restaurant,
            color: Colors.orange[700],
          ),
        ),
        title: Text(
          food['restaurant_name'] ?? 'Unknown Restaurant',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(
          '${food['cuisine_type']?.toString().replaceAll('_', ' ').toUpperCase() ?? 'Unknown'} - ${food['meal_type']?.toString().toUpperCase() ?? 'Unknown'}',
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              '₹${food['total_cost'] ?? 0}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
            Text(
              '${food['number_of_people'] ?? 1} people',
              style: const TextStyle(fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }
}
