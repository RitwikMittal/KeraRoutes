import 'package:flutter/material.dart';

// Original implementation with location support
/*
import 'package:geolocator/geolocator.dart';

class TripMap extends StatelessWidget {
  final Position? currentPosition;
  final List<Position>? routePoints;
  final bool isActive;

  const TripMap({
    Key? key,
    this.currentPosition,
    this.routePoints,
    this.isActive = false,
  }) : super(key: key);
*/

// Simplified implementation for initial setup
class TripMap extends StatelessWidget {
  final bool isActive;

  const TripMap({
    Key? key,
    this.isActive = false,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      height: 200,
      decoration: BoxDecoration(
        color: Colors.grey.shade200,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade300),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(12),
        child: Stack(
          children: [
            // Map placeholder
            Container(
              width: double.infinity,
              height: double.infinity,
              color: Colors.blue.shade50,
              child: const Center(
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Icon(
                      Icons.map,
                      size: 48,
                      color: Colors.grey,
                    ),
                    SizedBox(height: 8),
                    Text(
                      'Map View',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 16,
                      ),
                    ),
                    Text(
                      '(Integration with actual map service)',
                      style: TextStyle(
                        color: Colors.grey,
                        fontSize: 12,
                      ),
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