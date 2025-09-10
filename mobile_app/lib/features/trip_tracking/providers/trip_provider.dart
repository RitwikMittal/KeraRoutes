import 'package:flutter/foundation.dart';

class Trip {
  final String? tripPurpose;
  final DateTime? createdAt;
  final double? totalCost;
  final double? totalDistanceKm;
  final int? totalDurationMinutes;
  final List<dynamic>? tripChain;
  final GroupDetails? groupDetails;

  Trip({
    this.tripPurpose,
    this.createdAt,
    this.totalCost,
    this.totalDistanceKm,
    this.totalDurationMinutes,
    this.tripChain,
    this.groupDetails,
  });
}

class GroupDetails {
  final int? totalMembers;
  final String? groupType;

  GroupDetails({
    this.totalMembers,
    this.groupType,
  });
}

class TripProvider with ChangeNotifier {
  bool _isLoading = false;
  final List<Trip> _trips = [];

  bool get isLoading => _isLoading;
  List<Trip> get trips => _trips;

  Future<void> loadUserTrips() async {
    _isLoading = true;
    notifyListeners();

    // Simulate API call
    await Future.delayed(const Duration(milliseconds: 500));

    // Add dummy data
    _trips.clear();
    _trips.addAll([
      Trip(
        tripPurpose: 'Work',
        createdAt: DateTime.now(),
        totalCost: 50.0,
        totalDistanceKm: 5.2,
        totalDurationMinutes: 30,
        tripChain: [1, 2],
        groupDetails: GroupDetails(totalMembers: 1),
      ),
      Trip(
        tripPurpose: 'Shopping',
        createdAt: DateTime.now().subtract(const Duration(days: 1)),
        totalCost: 100.0,
        totalDistanceKm: 8.5,
        totalDurationMinutes: 45,
        tripChain: [1],
        groupDetails: GroupDetails(totalMembers: 2),
      ),
    ]);

    _isLoading = false;
    notifyListeners();
  }
}