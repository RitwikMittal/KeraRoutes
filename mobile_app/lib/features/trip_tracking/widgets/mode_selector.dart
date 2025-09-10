// mobile_app/lib/features/trip_tracking/widgets/mode_selector.dart
import 'package:flutter/material.dart';
import '../../../core/constants/kerala_data.dart';

class ModeSelector extends StatelessWidget {
  final String selectedMode;
  final Function(String) onModeChanged;

  const ModeSelector({
    Key? key,
    required this.selectedMode,
    required this.onModeChanged,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.grey.shade50,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: Colors.grey.shade200),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          const Text(
            'Select Transport Mode',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
            ),
          ),
          const SizedBox(height: 12),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: KeralaData.transportModes.map((mode) {
              final isSelected = selectedMode == mode;
              final displayName = KeralaData.transportModeNames[mode] ?? mode;
              
              return GestureDetector(
                onTap: () => onModeChanged(mode),
                child: Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 12,
                    vertical: 8,
                  ),
                  decoration: BoxDecoration(
                    color: isSelected 
                        ? const Color(0xFF2E7D32)
                        : Colors.white,
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(
                      color: isSelected 
                          ? const Color(0xFF2E7D32)
                          : Colors.grey.shade300,
                    ),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        _getTransportIcon(mode),
                        size: 16,
                        color: isSelected ? Colors.white : Colors.grey.shade600,
                      ),
                      const SizedBox(width: 4),
                      Text(
                        displayName,
                        style: TextStyle(
                          color: isSelected ? Colors.white : Colors.grey.shade700,
                          fontSize: 12,
                          fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                        ),
                      ),
                    ],
                  ),
                ),
              );
            }).toList(),
          ),
        ],
      ),
    );
  }

  IconData _getTransportIcon(String mode) {
    switch (mode.toLowerCase()) {
      case 'walk':
        return Icons.directions_walk;
      case 'bicycle':
        return Icons.directions_bike;
      case 'motorcycle':
        return Icons.two_wheeler;
      case 'car':
        return Icons.directions_car;
      case 'auto_rickshaw':
        return Icons.two_wheeler;
      case 'bus':
        return Icons.directions_bus;
      case 'train':
        return Icons.train;
      case 'metro':
        return Icons.subway;
      case 'ferry':
        return Icons.directions_boat;
      case 'taxi':
        return Icons.local_taxi;
      default:
        return Icons.directions;
    }
  }
}