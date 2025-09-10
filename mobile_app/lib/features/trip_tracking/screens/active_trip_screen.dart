
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:geolocator/geolocator.dart';
import 'package:image_picker/image_picker.dart';
import 'dart:async';
import 'dart:io';

import '../providers/trip_provider.dart';
import '../widgets/mode_selector.dart';
import '../../../core/models/trip_model.dart';
import '../../../shared/widgets/kerala_themed_card.dart';

class ActiveTripScreen extends StatefulWidget {
  const ActiveTripScreen({super.key});

  @override
  State<ActiveTripScreen> createState() => _ActiveTripScreenState();
}

class _ActiveTripScreenState extends State<ActiveTripScreen> {
  Timer? _locationTimer;
  Position? _currentPosition;
  DateTime? _tripStartTime;
  bool _isTripActive = false;
  String _selectedMode = 'walk';
  List<Position> _routePoints = [];
  double _totalDistance = 0.0;
  final double _totalCost = 0.0;
  int _groupSize = 1;
  String _tripPurpose = 'other';
  
  final TextEditingController _costController = TextEditingController();
  final TextEditingController _notesController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _getCurrentLocation();
  }

  @override
  void dispose() {
    _locationTimer?.cancel();
    _costController.dispose();
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _getCurrentLocation() async {
    try {
      Position position = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );
      setState(() {
        _currentPosition = position;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error getting location: $e')),
      );
    }
  }

  void _startTrip() {
    if (_currentPosition == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Please wait for location to be detected')),
      );
      return;
    }

    setState(() {
      _isTripActive = true;
      _tripStartTime = DateTime.now();
      _routePoints = [_currentPosition!];
    });

    // Start location tracking
    _locationTimer = Timer.periodic(const Duration(seconds: 10), (timer) {
      _trackLocation();
    });

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Trip started! Tracking your journey...')),
    );
  }

  void _stopTrip() {
    _locationTimer?.cancel();
    setState(() {
      _isTripActive = false;
    });

    _showTripSummaryDialog();
  }

  Future<void> _trackLocation() async {
    try {
      Position newPosition = await Geolocator.getCurrentPosition(
        desiredAccuracy: LocationAccuracy.high,
      );

      if (_routePoints.isNotEmpty) {
        double distance = Geolocator.distanceBetween(
          _routePoints.last.latitude,
          _routePoints.last.longitude,
          newPosition.latitude,
          newPosition.longitude,
        );

        setState(() {
          _totalDistance += distance / 1000; // Convert to kilometers
          _routePoints.add(newPosition);
          _currentPosition = newPosition;
        });
      }
    } catch (e) {
      print('Error tracking location: $e');
    }
  }

  void _showTripSummaryDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('Complete Your Trip'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                // Trip summary
                Text('Distance: ${_totalDistance.toStringAsFixed(2)} km'),
                Text('Duration: ${_tripStartTime != null ? DateTime.now().difference(_tripStartTime!).inMinutes : 0} minutes'),
                const SizedBox(height: 16),

                // Cost input
                TextField(
                  controller: _costController,
                  keyboardType: TextInputType.number,
                  decoration: const InputDecoration(
                    labelText: 'Total Cost (₹)',
                    border: OutlineInputBorder(),
                  ),
                ),
                const SizedBox(height: 12),

                // Group size
                DropdownButtonFormField<int>(
                  initialValue: _groupSize,
                  decoration: const InputDecoration(
                    labelText: 'Group Size',
                    border: OutlineInputBorder(),
                  ),
                  items: List.generate(10, (index) => index + 1)
                      .map((size) => DropdownMenuItem(
                            value: size,
                            child: Text('$size ${size == 1 ? 'person' : 'people'}'),
                          ))
                      .toList(),
                  onChanged: (value) {
                    setState(() {
                      _groupSize = value!;
                    });
                  },
                ),
                const SizedBox(height: 12),

                // Trip purpose
                DropdownButtonFormField<String>(
                  initialValue: _tripPurpose,
                  decoration: const InputDecoration(
                    labelText: 'Trip Purpose',
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'work', child: Text('Work')),
                    DropdownMenuItem(value: 'education', child: Text('Education')),
                    DropdownMenuItem(value: 'shopping', child: Text('Shopping')),
                    DropdownMenuItem(value: 'tourism', child: Text('Tourism')),
                    DropdownMenuItem(value: 'medical', child: Text('Medical')),
                    DropdownMenuItem(value: 'social', child: Text('Social')),
                    DropdownMenuItem(value: 'other', child: Text('Other')),
                  ],
                  onChanged: (value) {
                    setState(() {
                      _tripPurpose = value!;
                    });
                  },
                ),
                const SizedBox(height: 12),

                // Notes
                TextField(
                  controller: _notesController,
                  maxLines: 2,
                  decoration: const InputDecoration(
                    labelText: 'Notes (optional)',
                    border: OutlineInputBorder(),
                  ),
                ),
              ],
            ),
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.of(context).pop(),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: _saveTripData,
              child: const Text('Save Trip'),
            ),
          ],
        );
      },
    );
  }

  Future<void> _saveTripData() async {
    if (_tripStartTime == null || _routePoints.length < 2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Invalid trip data')),
      );
      return;
    }

    // Create trip segment
    final tripSegment = TripSegment(
      segmentId: 1,
      mode: _selectedMode,
      startTime: _tripStartTime!,
      endTime: DateTime.now(),
      origin: LocationPoint(
        lat: _routePoints.first.latitude,
        lng: _routePoints.first.longitude,
        name: 'Start Location',
      ),
      destination: LocationPoint(
        lat: _routePoints.last.latitude,
        lng: _routePoints.last.longitude,
        name: 'End Location',
      ),
      distanceKm: _totalDistance,
      cost: double.tryParse(_costController.text) ?? 0.0,
      comfortRating: 3, // Default rating
      notes: _notesController.text.isNotEmpty ? _notesController.text : null,
    );

    // Create trip data
    final tripData = TripData(
      tripChain: [tripSegment],
      groupDetails: GroupDetails(
        totalMembers: _groupSize,
        groupType: _groupSize == 1 ? 'solo' : 'group',
      ),
      tripPurpose: _tripPurpose,
      userNotes: _notesController.text.isNotEmpty ? _notesController.text : null,
    );

    // Save trip
    try {
      final tripProvider = Provider.of<TripProvider>(context, listen: false);
      await tripProvider.createTrip(tripData);

      Navigator.of(context).pop(); // Close dialog
      Navigator.of(context).pop(); // Go back to dashboard

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Trip saved successfully!')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error saving trip: $e')),
      );
    }
  }

  Future<void> _uploadReceipt() async {
    final ImagePicker picker = ImagePicker();
    final XFile? image = await picker.pickImage(source: ImageSource.camera);

    if (image != null) {
      try {
        final tripProvider = Provider.of<TripProvider>(context, listen: false);
        final result = await tripProvider.uploadReceipt(File(image.path));

        if (result != null) {
          // Pre-fill cost if OCR extracted it
          if (result['extracted_data']?['total_amount'] != null) {
            _costController.text = result['extracted_data']['total_amount'].toString();
          }

          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Receipt uploaded and processed!')),
          );
        }
      } catch (e) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error uploading receipt: $e')),
        );
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Active Trip'),
        backgroundColor: const Color(0xFF2E7D32),
        actions: [
          if (_isTripActive)
            IconButton(
              icon: const Icon(Icons.camera_alt),
              onPressed: _uploadReceipt,
              tooltip: 'Upload Receipt',
            ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Trip status card
            KeralaThemedCard(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  children: [
                    Row(
                      children: [
                        Icon(
                          _isTripActive ? Icons.play_circle : Icons.pause_circle,
                          color: _isTripActive ? Colors.green : Colors.grey,
                          size: 32,
                        ),
                        const SizedBox(width: 12),
                        Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            Text(
                              _isTripActive ? 'Trip Active' : 'Ready to Start',
                              style: const TextStyle(
                                fontSize: 20,
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                            if (_tripStartTime != null)
                              Text(
                                'Started: ${_tripStartTime!.hour}:${_tripStartTime!.minute.toString().padLeft(2, '0')}',
                                style: const TextStyle(color: Colors.grey),
                              ),
                          ],
                        ),
                      ],
                    ),
                    const SizedBox(height: 16),
                    if (_currentPosition != null)
                      Text(
                        'Current Location: ${_currentPosition!.latitude.toStringAsFixed(6)}, ${_currentPosition!.longitude.toStringAsFixed(6)}',
                        style: const TextStyle(fontSize: 12, color: Colors.grey),
                      ),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 16),

            // Transport mode selector
            const Text(
              'Transport Mode',
              style: TextStyle(
                fontSize: 18,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            ModeSelector(
              selectedMode: _selectedMode,
              onModeChanged: (mode) {
                setState(() {
                  _selectedMode = mode;
                });
              },
            ),
            const SizedBox(height: 16),

            // Trip statistics (when active)
            if (_isTripActive) ...[
              const Text(
                'Trip Statistics',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                ),
              ),
              const SizedBox(height: 8),
              KeralaThemedCard(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      _buildStatRow('Distance', '${_totalDistance.toStringAsFixed(2)} km'),
                      _buildStatRow(
                        'Duration',
                        '${_tripStartTime != null ? DateTime.now().difference(_tripStartTime!).inMinutes : 0} min',
                      ),
                      _buildStatRow('Points Collected', '${_routePoints.length}'),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),
            ],

            // Control buttons
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: _isTripActive ? _stopTrip : _startTrip,
                style: ElevatedButton.styleFrom(
                  backgroundColor: _isTripActive ? Colors.red : const Color(0xFF2E7D32),
                  padding: const EdgeInsets.all(16),
                ),
                child: Text(
                  _isTripActive ? 'Stop Trip' : 'Start Trip',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
              ),
            ),
            
            if (_isTripActive) ...[
              const SizedBox(height: 12),
              SizedBox(
                width: double.infinity,
                child: OutlinedButton.icon(
                  onPressed: _uploadReceipt,
                  icon: const Icon(Icons.camera_alt),
                  label: const Text('Upload Receipt'),
                  style: OutlinedButton.styleFrom(
                    padding: const EdgeInsets.all(16),
                    side: const BorderSide(color: Color(0xFF2E7D32)),
                  ),
                ),
              ),
            ],

            const SizedBox(height: 24),

            // Tips card
            const KeralaThemedCard(
              child: Padding(
                padding: EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.lightbulb, color: Color(0xFFFFC107)),
                        SizedBox(width: 8),
                        Text(
                          'Tips',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    SizedBox(height: 8),
                    Text(
                      '• Keep GPS enabled for accurate tracking',
                      style: TextStyle(fontSize: 14),
                    ),
                    Text(
                      '• Upload receipts to get expense insights',
                      style: TextStyle(fontSize: 14),
                    ),
                    Text(
                      '• Complete trips to earn reward points',
                      style: TextStyle(fontSize: 14),
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

  Widget _buildStatRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(color: Colors.grey)),
          Text(
            value,
            style: const TextStyle(
              fontWeight: FontWeight.bold,
              fontSize: 16,
            ),
          ),
        ],
      ),
    );
  }
  }