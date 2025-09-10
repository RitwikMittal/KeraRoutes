// mobile_app/lib/core/models/food_model.dart
class DishItem {
  final String name;
  final String cuisineType;
  final double price;
  final int quantity;
  final bool vegetarian;
  final String? spiceLevel;
  final bool localSpecialty;

  DishItem({
    required this.name,
    required this.cuisineType,
    required this.price,
    this.quantity = 1,
    this.vegetarian = true,
    this.spiceLevel,
    this.localSpecialty = false,
  });

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'cuisine_type': cuisineType,
      'price': price,
      'quantity': quantity,
      'vegetarian': vegetarian,
      'spice_level': spiceLevel,
      'local_specialty': localSpecialty,
    };
  }

  factory DishItem.fromJson(Map<String, dynamic> json) {
    return DishItem(
      name: json['name'] ?? '',
      cuisineType: json['cuisine_type'] ?? '',
      price: json['price']?.toDouble() ?? 0.0,
      quantity: json['quantity'] ?? 1,
      vegetarian: json['vegetarian'] ?? true,
      spiceLevel: json['spice_level'],
      localSpecialty: json['local_specialty'] ?? false,
    );
  }
}

class FoodLocation {
  final String restaurantName;
  final double lat;
  final double lng;
  final String? address;
  final String cuisineType;
  final String establishmentType;
  final String? accessibilityFromTransport;

  FoodLocation({
    required this.restaurantName,
    required this.lat,
    required this.lng,
    this.address,
    required this.cuisineType,
    required this.establishmentType,
    this.accessibilityFromTransport,
  });

  Map<String, dynamic> toJson() {
    return {
      'restaurant_name': restaurantName,
      'lat': lat,
      'lng': lng,
      'address': address,
      'cuisine_type': cuisineType,
      'establishment_type': establishmentType,
      'accessibility_from_transport': accessibilityFromTransport,
    };
  }

  factory FoodLocation.fromJson(Map<String, dynamic> json) {
    return FoodLocation(
      restaurantName: json['restaurant_name'] ?? '',
      lat: json['lat']?.toDouble() ?? 0.0,
      lng: json['lng']?.toDouble() ?? 0.0,
      address: json['address'],
      cuisineType: json['cuisine_type'] ?? '',
      establishmentType: json['establishment_type'] ?? '',
      accessibilityFromTransport: json['accessibility_from_transport'],
    );
  }
}

class FoodConsumption {
  final String? tripSegmentId;
  final FoodLocation location;
  final String mealType;
  final List<DishItem> dishesOrdered;
  final double totalCost;
  final double costPerPerson;
  final String paymentMethod;
  final int? serviceRating;
  final int? foodQualityRating;
  final int? culturalAuthenticityRating;
  final int diningCompanions;
  final bool localRecommendation;
  final List<String> dietaryRestrictions;
  final bool languageBarrier;
  final String? billPhotoUrl;
  final List<String>? foodPhotoUrls;

  FoodConsumption({
    this.tripSegmentId,
    required this.location,
    required this.mealType,
    required this.dishesOrdered,
    required this.totalCost,
    required this.costPerPerson,
    required this.paymentMethod,
    this.serviceRating,
    this.foodQualityRating,
    this.culturalAuthenticityRating,
    this.diningCompanions = 1,
    this.localRecommendation = false,
    this.dietaryRestrictions = const [],
    this.languageBarrier = false,
    this.billPhotoUrl,
    this.foodPhotoUrls,
  });

  Map<String, dynamic> toJson() {
    return {
      'trip_segment_id': tripSegmentId,
      'location': location.toJson(),
      'meal_type': mealType,
      'dishes_ordered': dishesOrdered.map((dish) => dish.toJson()).toList(),
      'total_cost': totalCost,
      'cost_per_person': costPerPerson,
      'payment_method': paymentMethod,
      'service_rating': serviceRating,
      'food_quality_rating': foodQualityRating,
      'cultural_authenticity_rating': culturalAuthenticityRating,
      'dining_companions': diningCompanions,
      'local_recommendation': localRecommendation,
      'dietary_restrictions': dietaryRestrictions,
      'language_barrier': languageBarrier,
      'bill_photo_url': billPhotoUrl,
      'food_photo_urls': foodPhotoUrls,
    };
  }

  factory FoodConsumption.fromJson(Map<String, dynamic> json) {
    return FoodConsumption(
      tripSegmentId: json['trip_segment_id'],
      location: FoodLocation.fromJson(json['location'] ?? {}),
      mealType: json['meal_type'] ?? '',
      dishesOrdered: json['dishes_ordered'] != null
          ? (json['dishes_ordered'] as List)
              .map((dish) => DishItem.fromJson(dish))
              .toList()
          : [],
      totalCost: json['total_cost']?.toDouble() ?? 0.0,
      costPerPerson: json['cost_per_person']?.toDouble() ?? 0.0,
      paymentMethod: json['payment_method'] ?? '',
      serviceRating: json['service_rating'],
      foodQualityRating: json['food_quality_rating'],
      culturalAuthenticityRating: json['cultural_authenticity_rating'],
      diningCompanions: json['dining_companions'] ?? 1,
      localRecommendation: json['local_recommendation'] ?? false,
      dietaryRestrictions: json['dietary_restrictions'] != null
          ? List<String>.from(json['dietary_restrictions'])
          : [],
      languageBarrier: json['language_barrier'] ?? false,
      billPhotoUrl: json['bill_photo_url'],
      foodPhotoUrls: json['food_photo_urls'] != null
          ? List<String>.from(json['food_photo_urls'])
          : null,
    );
  }
}