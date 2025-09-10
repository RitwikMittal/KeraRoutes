// mobile_app/lib/core/constants/kerala_data.dart
class KeralaData {
  static const List<String> districts = [
    'Thiruvananthapuram',
    'Kollam',
    'Pathanamthitta',
    'Alappuzha',
    'Kottayam',
    'Idukki',
    'Ernakulam',
    'Thrissur',
    'Palakkad',
    'Malappuram',
    'Kozhikode',
    'Wayanad',
    'Kannur',
    'Kasaragod'
  ];

  static const List<String> transportModes = [
    'walk',
    'bicycle',
    'motorcycle',
    'car',
    'auto_rickshaw',
    'bus',
    'train',
    'metro',
    'ferry',
    'taxi'
  ];

  static const Map<String, String> transportModeNames = {
    'walk': 'Walking',
    'bicycle': 'Bicycle',
    'motorcycle': 'Motorcycle',
    'car': 'Car',
    'auto_rickshaw': 'Auto Rickshaw',
    'bus': 'Bus',
    'train': 'Train',
    'metro': 'Metro',
    'ferry': 'Ferry/Boat',
    'taxi': 'Taxi',
  };

  static const List<String> tripPurposes = [
    'work',
    'education',
    'shopping',
    'medical',
    'social',
    'recreation',
    'tourism',
    'other'
  ];

  static const List<String> cuisineTypes = [
    'kerala_traditional',
    'south_indian',
    'north_indian',
    'chinese',
    'continental',
    'fast_food',
    'street_food',
    'seafood'
  ];

  static const List<String> mealTypes = [
    'breakfast',
    'lunch',
    'dinner',
    'snack',
    'beverage'
  ];
}