import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/trip_provider.dart';
import '../../data_collection/screens/data_collection_screen.dart';
import '../../analytics/screens/personal_analytics_screen.dart';
import '../../gamification/screens/achievements_screen.dart';
import '../../../shared/widgets/kerala_themed_card.dart';

class TripDashboard extends StatefulWidget {
  const TripDashboard({super.key});

  @override
  State<TripDashboard> createState() => _TripDashboardState();
}

class _TripDashboardState extends State<TripDashboard> {
  // Original state variables
  // Position? _currentPosition;
  int _selectedIndex = 0;

  @override
  void initState() {
    super.initState();
    // Using addPostFrameCallback to ensure the context is ready
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _loadUserTrips();
    });
  }

  Future<void> _loadUserTrips() async {
    final tripProvider = Provider.of<TripProvider>(context, listen: false);
    await tripProvider.loadUserTrips();
  }

  // Original initState and location methods
  // @override
  // void initState() {
  //   super.initState();
  //   _getCurrentLocation();
  //   _loadUserTrips();
  // }
  // 
  // Future<void> _getCurrentLocation() async {
  //   try {
  //     Position position = await Geolocator.getCurrentPosition(
  //       desiredAccuracy: LocationAccuracy.high,
  //     );
  //     setState(() {
  //       _currentPosition = position;
  //     });
  //   } catch (e) {
  //     print('Error getting location: $e');
  //   }
  // }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('NATPAC Smart Transport'),
        backgroundColor: const Color(0xFF2E7D32), // Kerala green
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.notifications),
            onPressed: () {
              // TODO: Show notifications
            },
          ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () {
              // TODO: Show settings
            },
          ),
        ],
      ),
      body: _buildBody(),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: _selectedIndex,
        onTap: (index) {
          setState(() {
            _selectedIndex = index;
          });
        },
        type: BottomNavigationBarType.fixed,
        selectedItemColor: const Color(0xFF2E7D32),
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.home),
            label: 'Home',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.directions),
            label: 'Trips',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.restaurant),
            label: 'Food',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.analytics),
            label: 'Analytics',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.stars),
            label: 'Rewards',
          ),
        ],
      ),
      floatingActionButton: _selectedIndex == 1 ? FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (context) => const DataCollectionScreen(),
            ),
          );
        },
        backgroundColor: const Color(0xFF2E7D32),
        child: const Icon(Icons.add_location),
      ) : null,
    );
  }

  Widget _buildBody() {
    switch (_selectedIndex) {
      case 0:
        return _buildHomeTab();
      case 1:
        return _buildTripsTab();
      case 2:
        return const DataCollectionScreen();
      case 3:
        return const PersonalAnalyticsScreen();
      case 4:
        return const AchievementsScreen();
      default:
        return _buildHomeTab();
    }
  }

  Widget _buildHomeTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Welcome card
          KeralaThemedCard(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Welcome to Kerala!',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF2E7D32),
                    ),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'Track your trips and discover Kerala!',
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            ),
          ),
          const SizedBox(height: 16),

          // Quick actions
          const Text(
            'Quick Actions',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildQuickActionCard(
                  'Start Trip',
                  Icons.play_arrow,
                  () => Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => Scaffold(
                        appBar: AppBar(title: const Text('Start Trip')),
                        body: const Center(child: Text('Trip tracking coming soon')),
                      ),
                    ),
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickActionCard(
                  'Log Food',
                  Icons.restaurant,
                  () => setState(() => _selectedIndex = 2),
                ),
              ),
            ],
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              Expanded(
                child: _buildQuickActionCard(
                  'View Stats',
                  Icons.analytics,
                  () => setState(() => _selectedIndex = 3),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: _buildQuickActionCard(
                  'Rewards',
                  Icons.stars,
                  () => setState(() => _selectedIndex = 4),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Recent activity
          const Text(
            'Recent Activity',
            style: TextStyle(
              fontSize: 20,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Consumer<TripProvider>(
            builder: (context, tripProvider, child) {
              if (tripProvider.isLoading) {
                return const Center(child: CircularProgressIndicator());
              }

              if (tripProvider.trips.isEmpty) {
                return const KeralaThemedCard(
                  child: Padding(
                    padding: EdgeInsets.all(16),
                    child: Text(
                      'No trips yet. Start your first journey!',
                      textAlign: TextAlign.center,
                    ),
                  ),
                );
              }

              return Column(
                children: tripProvider.trips.take(3).map((trip) {
                  return KeralaThemedCard(
                    child: ListTile(
                      leading: const Icon(
                        Icons.trip_origin,
                        color: Color(0xFF2E7D32),
                      ),
                      title: Text(trip.tripPurpose ?? 'Unknown purpose'),
                      subtitle: Text(
                        'Cost: ₹${trip.totalCost?.toStringAsFixed(0) ?? '0'} • ${trip.tripChain?.length ?? 0} segments',
                      ),
                      trailing: Text(
                        '${trip.createdAt?.day}/${trip.createdAt?.month}',
                        style: const TextStyle(
                          color: Colors.grey,
                          fontSize: 12,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              );
            },
          ),
        ],
      ),
    );
  }

  Widget _buildQuickActionCard(String title, IconData icon, VoidCallback onTap) {
    return GestureDetector(
      onTap: onTap,
      child: KeralaThemedCard(
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Column(
            children: [
              Icon(
                icon,
                size: 32,
                color: const Color(0xFF2E7D32),
              ),
              const SizedBox(height: 8),
              Text(
                title,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildTripsTab() {
    return Consumer<TripProvider>(
      builder: (context, tripProvider, child) {
        if (tripProvider.isLoading) {
          return const Center(child: CircularProgressIndicator());
        }

        return RefreshIndicator(
          onRefresh: _loadUserTrips,
          child: ListView.builder(
            padding: const EdgeInsets.all(16),
            itemCount: tripProvider.trips.length + 1, // +1 for header
            itemBuilder: (context, index) {
              if (index == 0) {
                return Padding(
                  padding: const EdgeInsets.only(bottom: 16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      const Text(
                        'Your Trips',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      TextButton.icon(
                        onPressed: () {
                          // TODO: Show filters
                        },
                        icon: const Icon(Icons.filter_list),
                        label: const Text('Filter'),
                      ),
                    ],
                  ),
                );
              }

              final trip = tripProvider.trips[index - 1];
              return KeralaThemedCard(
                child: ExpansionTile(
                  leading: Icon(
                    _getTripIcon(trip.tripPurpose),
                    color: const Color(0xFF2E7D32),
                  ),
                  title: Text(trip.tripPurpose ?? 'Unknown Purpose'),
                  subtitle: Text(
                    '${trip.createdAt?.day}/${trip.createdAt?.month}/${trip.createdAt?.year} • ₹${trip.totalCost?.toStringAsFixed(0) ?? '0'}',
                  ),
                  children: [
                    Padding(
                      padding: const EdgeInsets.all(16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildTripDetailRow('Distance', '${trip.totalDistanceKm?.toStringAsFixed(1) ?? '0'} km'),
                          _buildTripDetailRow('Duration', '${trip.totalDurationMinutes ?? 0} minutes'),
                          _buildTripDetailRow('Segments', '${trip.tripChain?.length ?? 0}'),
                          _buildTripDetailRow('Group Size', '${trip.groupDetails?.totalMembers ?? 1}'),
                          const SizedBox(height: 12),
                          if (trip.tripChain != null && trip.tripChain!.isNotEmpty)
                            Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                const Text(
                                  'Trip Segments:',
                                  style: TextStyle(fontWeight: FontWeight.bold),
                                ),
                                const SizedBox(height: 8),
                                ...trip.tripChain!.map((segment) => Padding(
                                  padding: const EdgeInsets.only(bottom: 4),
                                  child: Row(
                                    children: [
                                      Icon(
                                        _getTransportIcon(segment.mode),
                                        size: 16,
                                        color: Colors.grey,
                                      ),
                                      const SizedBox(width: 8),
                                      Text(
                                        '${segment.mode} • ₹${segment.cost?.toStringAsFixed(0) ?? '0'}',
                                        style: const TextStyle(fontSize: 14),
                                      ),
                                    ],
                                  ),
                                )),
                              ],
                            ),
                        ],
                      ),
                    ),
                  ],
                ),
              );
            },
          ),
        );
      },
    );
  }

  Widget _buildTripDetailRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(value, style: const TextStyle(fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  IconData _getTripIcon(String? purpose) {
    switch (purpose?.toLowerCase()) {
      case 'work':
        return Icons.work;
      case 'education':
        return Icons.school;
      case 'shopping':
        return Icons.shopping_bag;
      case 'tourism':
        return Icons.camera_alt;
      case 'medical':
        return Icons.local_hospital;
      case 'social':
        return Icons.people;
      default:
        return Icons.trip_origin;
    }
  }

  IconData _getTransportIcon(String? mode) {
    switch (mode?.toLowerCase()) {
      case 'walk':
        return Icons.directions_walk;
      case 'bicycle':
        return Icons.directions_bike;
      case 'car':
        return Icons.directions_car;
      case 'bus':
        return Icons.directions_bus;
      case 'train':
        return Icons.train;
      case 'auto_rickshaw':
        return Icons.two_wheeler;
      default:
        return Icons.directions;
    }
  }
}