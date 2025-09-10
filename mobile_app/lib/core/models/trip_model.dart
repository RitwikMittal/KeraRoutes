// mobile_app/lib/core/models/trip_model.dart
class LocationPoint {
  final double lat;
  final double lng;
  final String? name;
  final String? address;

  LocationPoint({
    required this.lat,
    required this.lng,
    this.name,
    this.address,
  });

  Map<String, dynamic> toJson() {
    return {
      'lat': lat,
      'lng': lng,
      'name': name,
      'address': address,
    };
  }

  factory LocationPoint.fromJson(Map<String, dynamic> json) {
    return LocationPoint(
      lat: json['lat']?.toDouble() ?? 0.0,
      lng: json['lng']?.toDouble() ?? 0.0,
      name: json['name'],
      address: json['address'],
    );
  }
}

class TripSegment {
  final int segmentId;
  final String mode;
  final String? subMode;
  final DateTime startTime;
  final DateTime endTime;
  final LocationPoint origin;
  final LocationPoint destination;
  final double? distanceKm;
  final double? cost;
  final int? waitingTimeMinutes;
  final int? comfortRating;
  final String? occupancyLevel;
  final List<String>? delays;
  final String? receiptPhotoUrl;
  final String? weather;
  final String? notes;

  TripSegment({
    required this.segmentId,
    required this.mode,
    this.subMode,
    required this.startTime,
    required this.endTime,
    required this.origin,
    required this.destination,
    this.distanceKm,
    this.cost,
    this.waitingTimeMinutes,
    this.comfortRating,
    this.occupancyLevel,
    this.delays,
    this.receiptPhotoUrl,
    this.weather,
    this.notes,
  });

  Map<String, dynamic> toJson() {
    return {
      'segment_id': segmentId,
      'mode': mode,
      'sub_mode': subMode,
      'start_time': startTime.toIso8601String(),
      'end_time': endTime.toIso8601String(),
      'origin': origin.toJson(),
      'destination': destination.toJson(),
      'distance_km': distanceKm,
      'cost': cost,
      'waiting_time_minutes': waitingTimeMinutes,
      'comfort_rating': comfortRating,
      'occupancy_level': occupancyLevel,
      'delays': delays,
      'receipt_photo_url': receiptPhotoUrl,
      'weather': weather,
      'notes': notes,
    };
  }

  factory TripSegment.fromJson(Map<String, dynamic> json) {
    return TripSegment(
      segmentId: json['segment_id'] ?? 0,
      mode: json['mode'] ?? 'unknown',
      subMode: json['sub_mode'],
      startTime: DateTime.parse(json['start_time'] ?? DateTime.now().toIso8601String()),
      endTime: DateTime.parse(json['end_time'] ?? DateTime.now().toIso8601String()),
      origin: LocationPoint.fromJson(json['origin'] ?? {}),
      destination: LocationPoint.fromJson(json['destination'] ?? {}),
      distanceKm: json['distance_km']?.toDouble(),
      cost: json['cost']?.toDouble(),
      waitingTimeMinutes: json['waiting_time_minutes'],
      comfortRating: json['comfort_rating'],
      occupancyLevel: json['occupancy_level'],
      delays: json['delays'] != null ? List<String>.from(json['delays']) : null,
      receiptPhotoUrl: json['receipt_photo_url'],
      weather: json['weather'],
      notes: json['notes'],
    );
  }
}

class GroupDetails {
  final int totalMembers;
  final String groupType;
  final Map<String, int>? ageDistribution;
  final List<String>? companions;

  GroupDetails({
    required this.totalMembers,
    required this.groupType,
    this.ageDistribution,
    this.companions,
  });

  Map<String, dynamic> toJson() {
    return {
      'total_members': totalMembers,
      'group_type': groupType,
      'age_distribution': ageDistribution,
      'companions': companions,
    };
  }

  factory GroupDetails.fromJson(Map<String, dynamic> json) {
    return GroupDetails(
      totalMembers: json['total_members'] ?? 1,
      groupType: json['group_type'] ?? 'solo',
      ageDistribution: json['age_distribution'] != null 
          ? Map<String, int>.from(json['age_distribution'])
          : null,
      companions: json['companions'] != null 
          ? List<String>.from(json['companions'])
          : null,
    );
  }
}

class TripData {
  final List<TripSegment> tripChain;
  final GroupDetails groupDetails;
  final String tripPurpose;
  final String? userNotes;

  TripData({
    required this.tripChain,
    required this.groupDetails,
    required this.tripPurpose,
    this.userNotes,
  });

  Map<String, dynamic> toJson() {
    return {
      'trip_chain': tripChain.map((segment) => segment.toJson()).toList(),
      'group_details': groupDetails.toJson(),
      'trip_purpose': tripPurpose,
      'user_notes': userNotes,
    };
  }
}

class Trip {
  final String tripId;
  final String userId;
  final List<TripSegment>? tripChain;
  final GroupDetails? groupDetails;
  final String? tripPurpose;
  final double? totalCost;
  final int? totalDurationMinutes;
  final double? totalDistanceKm;
  final double? dataQualityScore;
  final DateTime? createdAt;
  final DateTime? updatedAt;
  final String? userNotes;

  Trip({
    required this.tripId,
    required this.userId,
    this.tripChain,
    this.groupDetails,
    this.tripPurpose,
    this.totalCost,
    this.totalDurationMinutes,
    this.totalDistanceKm,
    this.dataQualityScore,
    this.createdAt,
    this.updatedAt,
    this.userNotes,
  });

  factory Trip.fromJson(Map<String, dynamic> json) {
    return Trip(
      tripId: json['trip_id'] ?? '',
      userId: json['user_id'] ?? '',
      tripChain: json['trip_chain'] != null
          ? (json['trip_chain'] as List)
              .map((segment) => TripSegment.fromJson(segment))
              .toList()
          : null,
      groupDetails: json['group_details'] != null
          ? GroupDetails.fromJson(json['group_details'])
          : null,
      tripPurpose: json['trip_purpose'],
      totalCost: json['total_cost']?.toDouble(),
      totalDurationMinutes: json['total_duration_minutes'],
      totalDistanceKm: json['total_distance_km']?.toDouble(),
      dataQualityScore: json['data_quality_score']?.toDouble(),
      createdAt: json['created_at'] != null 
          ? DateTime.parse(json['created_at'])
          : null,
      updatedAt: json['updated_at'] != null 
          ? DateTime.parse(json['updated_at'])
          : null,
      userNotes: json['user_notes'],
    );
  }
}