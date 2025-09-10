import 'package:flutter/material.dart';
import 'package:geolocator/geolocator.dart';
import '../../../core/services/api_service_simple.dart';

class DataCollectionScreen extends StatefulWidget {
  const DataCollectionScreen({super.key});

  @override
  State<DataCollectionScreen> createState() => _DataCollectionScreenState();
}

class _DataCollectionScreenState extends State<DataCollectionScreen>
    with SingleTickerProviderStateMixin {
  late TabController _tabController;
  final ApiServiceSimple _apiService = ApiServiceSimple();
  
  // Common loading state
  bool _isLoading = false;
  Position? _currentPosition;

  // Trip form data
  final _tripFormKey = GlobalKey<FormState>();
  String? _selectedTransportMode;
  String? _selectedTripPurpose;
  final _startLocationController = TextEditingController();
  final _endLocationController = TextEditingController();
  final _tripCostController = TextEditingController();
  final _numberOfPeopleController = TextEditingController(text: '1');

  // Food form data
  final _foodFormKey = GlobalKey<FormState>();
  final _restaurantNameController = TextEditingController();
  String? _selectedCuisineType;
  String? _selectedMealType;
  final _foodCostController = TextEditingController();
  final _foodPeopleController = TextEditingController(text: '1');
  final _notesController = TextEditingController();

  // Options
  final List<String> _transportModes = ['bus', 'train', 'auto', 'taxi', 'bike', 'walk', 'car'];
  final List<String> _tripPurposes = ['work', 'education', 'shopping', 'leisure', 'business', 'medical', 'other'];
  final List<String> _cuisineTypes = ['kerala', 'north_indian', 'south_indian', 'chinese', 'continental', 'fast_food', 'other'];
  final List<String> _mealTypes = ['breakfast', 'lunch', 'dinner', 'snack', 'beverage'];

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _tabController.dispose();
    _startLocationController.dispose();
    _endLocationController.dispose();
    _tripCostController.dispose();
    _numberOfPeopleController.dispose();
    _restaurantNameController.dispose();
    _foodCostController.dispose();
    _foodPeopleController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _getCurrentLocation() async {
    try {
      LocationPermission permission = await Geolocator.checkPermission();
      if (permission == LocationPermission.denied) {
        permission = await Geolocator.requestPermission();
      }

      if (permission == LocationPermission.deniedForever) {
        _showSnackBar('Location permissions are permanently denied');
        return;
      }

      if (permission == LocationPermission.denied) {
        _showSnackBar('Location permissions are denied');
        return;
      }

      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      setState(() {
        _currentPosition = position;
      });
    } catch (e) {
      _showSnackBar('Error getting location: $e');
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  Future<void> _submitTrip() async {
    if (!_tripFormKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final tripData = {
        'transport_mode': _selectedTransportMode,
        'purpose': _selectedTripPurpose,
        'start_location': {
          'city': _startLocationController.text,
          'latitude': _currentPosition?.latitude ?? 0.0,
          'longitude': _currentPosition?.longitude ?? 0.0,
        },
        'end_location': {
          'city': _endLocationController.text,
          'latitude': _currentPosition?.latitude ?? 0.0,
          'longitude': _currentPosition?.longitude ?? 0.0,
        },
        'cost': double.tryParse(_tripCostController.text) ?? 0.0,
        'number_of_people': int.tryParse(_numberOfPeopleController.text) ?? 1,
      };

      final result = await _apiService.createTrip(tripData);

      if (result['success'] == true) {
        _showSnackBar('Trip logged successfully! 🚌');
        _clearTripForm();
      } else {
        _showSnackBar('Failed to log trip: ${result['error'] ?? 'Unknown error'}');
      }
    } catch (e) {
      _showSnackBar('Error submitting trip: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  Future<void> _submitFood() async {
    if (!_foodFormKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
    });

    try {
      final foodData = {
        'restaurant_name': _restaurantNameController.text,
        'cuisine_type': _selectedCuisineType,
        'meal_type': _selectedMealType,
        'total_cost': double.tryParse(_foodCostController.text) ?? 0.0,
        'number_of_people': int.tryParse(_foodPeopleController.text) ?? 1,
        'notes': _notesController.text,
        'location': {
          'city': 'Kerala',
          'latitude': _currentPosition?.latitude ?? 0.0,
          'longitude': _currentPosition?.longitude ?? 0.0,
        },
      };

      final result = await _apiService.createFoodEntry(foodData);

      if (result['success'] == true) {
        _showSnackBar('Food entry logged successfully! 🍽️');
        _clearFoodForm();
      } else {
        _showSnackBar('Failed to log food: ${result['error'] ?? 'Unknown error'}');
      }
    } catch (e) {
      _showSnackBar('Error submitting food: $e');
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  void _clearTripForm() {
    _selectedTransportMode = null;
    _selectedTripPurpose = null;
    _startLocationController.clear();
    _endLocationController.clear();
    _tripCostController.clear();
    _numberOfPeopleController.text = '1';
    setState(() {});
  }

  void _clearFoodForm() {
    _restaurantNameController.clear();
    _selectedCuisineType = null;
    _selectedMealType = null;
    _foodCostController.clear();
    _foodPeopleController.text = '1';
    _notesController.clear();
    setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('🌴 Kerala Travel Logger'),
        backgroundColor: Colors.green[700],
        foregroundColor: Colors.white,
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.green[100],
          tabs: const [
            Tab(icon: Icon(Icons.directions_bus), text: 'Trip'),
            Tab(icon: Icon(Icons.restaurant), text: 'Food'),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _buildTripForm(),
          _buildFoodForm(),
        ],
      ),
    );
  }

  Widget _buildTripForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Form(
        key: _tripFormKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '🚌 Log Your Trip',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    
                    // Transport Mode
                    DropdownButtonFormField<String>(
                      value: _selectedTransportMode,
                      decoration: const InputDecoration(
                        labelText: 'Transport Mode',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.directions_transit),
                      ),
                      items: _transportModes.map((mode) {
                        return DropdownMenuItem(
                          value: mode,
                          child: Text(mode.toUpperCase()),
                        );
                      }).toList(),
                      onChanged: (value) => setState(() => _selectedTransportMode = value),
                      validator: (value) => value == null ? 'Please select transport mode' : null,
                    ),
                    const SizedBox(height: 16),

                    // Trip Purpose
                    DropdownButtonFormField<String>(
                      value: _selectedTripPurpose,
                      decoration: const InputDecoration(
                        labelText: 'Trip Purpose',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.location_on),
                      ),
                      items: _tripPurposes.map((purpose) {
                        return DropdownMenuItem(
                          value: purpose,
                          child: Text(purpose.toUpperCase()),
                        );
                      }).toList(),
                      onChanged: (value) => setState(() => _selectedTripPurpose = value),
                      validator: (value) => value == null ? 'Please select trip purpose' : null,
                    ),
                    const SizedBox(height: 16),

                    // Start Location
                    TextFormField(
                      controller: _startLocationController,
                      decoration: const InputDecoration(
                        labelText: 'From (City/Area)',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.my_location),
                      ),
                      validator: (value) => value?.isEmpty ?? true ? 'Please enter start location' : null,
                    ),
                    const SizedBox(height: 16),

                    // End Location
                    TextFormField(
                      controller: _endLocationController,
                      decoration: const InputDecoration(
                        labelText: 'To (City/Area)',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.place),
                      ),
                      validator: (value) => value?.isEmpty ?? true ? 'Please enter end location' : null,
                    ),
                    const SizedBox(height: 16),

                    // Cost
                    TextFormField(
                      controller: _tripCostController,
                      decoration: const InputDecoration(
                        labelText: 'Cost (₹)',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.currency_rupee),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) => value?.isEmpty ?? true ? 'Please enter cost' : null,
                    ),
                    const SizedBox(height: 16),

                    // Number of People
                    TextFormField(
                      controller: _numberOfPeopleController,
                      decoration: const InputDecoration(
                        labelText: 'Number of People',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.people),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) => value?.isEmpty ?? true ? 'Please enter number of people' : null,
                    ),
                    const SizedBox(height: 24),

                    // Submit Button
                    ElevatedButton(
                      onPressed: _isLoading ? null : _submitTrip,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.green[700],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: _isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('Log Trip 🚌'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFoodForm() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16.0),
      child: Form(
        key: _foodFormKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '🍽️ Log Your Food Experience',
                      style: Theme.of(context).textTheme.headlineSmall,
                    ),
                    const SizedBox(height: 16),
                    
                    // Restaurant Name
                    TextFormField(
                      controller: _restaurantNameController,
                      decoration: const InputDecoration(
                        labelText: 'Restaurant/Place Name',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.store),
                      ),
                      validator: (value) => value?.isEmpty ?? true ? 'Please enter restaurant name' : null,
                    ),
                    const SizedBox(height: 16),

                    // Cuisine Type
                    DropdownButtonFormField<String>(
                      value: _selectedCuisineType,
                      decoration: const InputDecoration(
                        labelText: 'Cuisine Type',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.restaurant_menu),
                      ),
                      items: _cuisineTypes.map((cuisine) {
                        return DropdownMenuItem(
                          value: cuisine,
                          child: Text(cuisine.replaceAll('_', ' ').toUpperCase()),
                        );
                      }).toList(),
                      onChanged: (value) => setState(() => _selectedCuisineType = value),
                      validator: (value) => value == null ? 'Please select cuisine type' : null,
                    ),
                    const SizedBox(height: 16),

                    // Meal Type
                    DropdownButtonFormField<String>(
                      value: _selectedMealType,
                      decoration: const InputDecoration(
                        labelText: 'Meal Type',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.schedule),
                      ),
                      items: _mealTypes.map((meal) {
                        return DropdownMenuItem(
                          value: meal,
                          child: Text(meal.toUpperCase()),
                        );
                      }).toList(),
                      onChanged: (value) => setState(() => _selectedMealType = value),
                      validator: (value) => value == null ? 'Please select meal type' : null,
                    ),
                    const SizedBox(height: 16),

                    // Total Cost
                    TextFormField(
                      controller: _foodCostController,
                      decoration: const InputDecoration(
                        labelText: 'Total Cost (₹)',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.currency_rupee),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) => value?.isEmpty ?? true ? 'Please enter total cost' : null,
                    ),
                    const SizedBox(height: 16),

                    // Number of People
                    TextFormField(
                      controller: _foodPeopleController,
                      decoration: const InputDecoration(
                        labelText: 'Number of People',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.people),
                      ),
                      keyboardType: TextInputType.number,
                      validator: (value) => value?.isEmpty ?? true ? 'Please enter number of people' : null,
                    ),
                    const SizedBox(height: 16),

                    // Notes
                    TextFormField(
                      controller: _notesController,
                      decoration: const InputDecoration(
                        labelText: 'Notes (optional)',
                        border: OutlineInputBorder(),
                        prefixIcon: Icon(Icons.notes),
                      ),
                      maxLines: 3,
                    ),
                    const SizedBox(height: 24),

                    // Submit Button
                    ElevatedButton(
                      onPressed: _isLoading ? null : _submitFood,
                      style: ElevatedButton.styleFrom(
                        backgroundColor: Colors.orange[700],
                        foregroundColor: Colors.white,
                        padding: const EdgeInsets.symmetric(vertical: 16),
                      ),
                      child: _isLoading
                          ? const CircularProgressIndicator(color: Colors.white)
                          : const Text('Log Food Experience 🍽️'),
                    ),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
