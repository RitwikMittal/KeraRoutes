import numpy as np
from typing import List, Dict, Tuple
from datetime import datetime
import math

class ModeDetectionService:
    def __init__(self):
        # Speed thresholds (km/h) for different modes
        self.speed_thresholds = {
            "walk": (0, 8),
            "bicycle": (8, 25),
            "auto_rickshaw": (10, 50),
            "car": (15, 120),
            "bus": (15, 80),
            "train": (40, 160),
            "metro": (30, 100)
        }
        
        # Acceleration patterns
        self.acceleration_patterns = {
            "walk": {"max_accel": 2, "smoothness": 0.8},
            "bicycle": {"max_accel": 3, "smoothness": 0.7},
            "auto_rickshaw": {"max_accel": 8, "smoothness": 0.4},
            "car": {"max_accel": 10, "smoothness": 0.6},
            "bus": {"max_accel": 6, "smoothness": 0.5},
            "train": {"max_accel": 4, "smoothness": 0.9},
            "metro": {"max_accel": 5, "smoothness": 0.9}
        }
    
    def detect_transport_mode(self, gps_points: List[Dict]) -> Dict:
        """
        Detect transport mode from GPS trajectory data
        
        Args:
            gps_points: List of GPS points with lat, lng, timestamp
            
        Returns:
            Dict with detected mode and confidence
        """
        if len(gps_points) < 3:
            return {"mode": "unknown", "confidence": 0.0}
        
        # Calculate features
        speeds = self._calculate_speeds(gps_points)
        accelerations = self._calculate_accelerations(speeds)
        
        # Analyze patterns
        avg_speed = np.mean(speeds) if speeds else 0
        max_speed = max(speeds) if speeds else 0
        speed_variance = np.var(speeds) if speeds else 0
        avg_acceleration = np.mean([abs(a) for a in accelerations]) if accelerations else 0
        
        # Rule-based classification
        mode_scores = {}
        
        for mode, (min_speed, max_speed_limit) in self.speed_thresholds.items():
            score = 0
            
            # Speed-based scoring
            if min_speed <= avg_speed <= max_speed_limit:
                score += 0.4
            
            if max_speed <= max_speed_limit * 1.2:  # Allow some buffer
                score += 0.3
            
            # Acceleration-based scoring
            expected_accel = self.acceleration_patterns[mode]["max_accel"]
            if avg_acceleration <= expected_accel:
                score += 0.3
            
            mode_scores[mode] = score
        
        # Get best match
        best_mode = max(mode_scores.keys(), key=lambda x: mode_scores[x])
        confidence = mode_scores[best_mode]
        
        return {
            "mode": best_mode,
            "confidence": confidence,
            "avg_speed_kmh": avg_speed,
            "max_speed_kmh": max_speed,
            "features": {
                "avg_speed": avg_speed,
                "max_speed": max_speed,
                "speed_variance": speed_variance,
                "avg_acceleration": avg_acceleration
            }
        }
    
    def _calculate_speeds(self, gps_points: List[Dict]) -> List[float]:
        """Calculate speeds between consecutive GPS points"""
        speeds = []
        
        for i in range(1, len(gps_points)):
            prev_point = gps_points[i-1]
            curr_point = gps_points[i]
            
            # Calculate distance using Haversine formula
            distance_km = self._haversine_distance(
                prev_point["lat"], prev_point["lng"],
                curr_point["lat"], curr_point["lng"]
            )
            
            # Calculate time difference in hours
            time_diff = (curr_point["timestamp"] - prev_point["timestamp"]).total_seconds() / 3600
            
            if time_diff > 0:
                speed_kmh = distance_km / time_diff
                speeds.append(speed_kmh)
        
        return speeds
    
    def _calculate_accelerations(self, speeds: List[float]) -> List[float]:
        """Calculate accelerations from speed data"""
        accelerations = []
        
        for i in range(1, len(speeds)):
            accel = speeds[i] - speeds[i-1]  # Simplified acceleration
            accelerations.append(accel)
        
        return accelerations
    
    def _haversine_distance(self, lat1: float, lng1: float, lat2: float, lng2: float) -> float:
        """Calculate distance between two points using Haversine formula"""
        R = 6371  # Earth's radius in kilometers
        
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        
        a = (math.sin(dlat/2) * math.sin(dlat/2) + 
             math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * 
             math.sin(dlng/2) * math.sin(dlng/2))
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def detect_stops_and_segments(self, gps_points: List[Dict], stop_threshold_minutes: int = 3) -> List[Dict]:
        """Detect trip segments separated by stops"""
        if len(gps_points) < 2:
            return []
        
        segments = []
        current_segment = [gps_points[0]]
        
        for i in range(1, len(gps_points)):
            prev_point = gps_points[i-1]
            curr_point = gps_points[i]
            
            # Check if this is a stop (low movement for extended time)
            distance = self._haversine_distance(
                prev_point["lat"], prev_point["lng"],
                curr_point["lat"], curr_point["lng"]
            )
            
            time_diff_minutes = (curr_point["timestamp"] - prev_point["timestamp"]).total_seconds() / 60
            
            # If stationary for more than threshold, it's a stop
            if distance < 0.1 and time_diff_minutes > stop_threshold_minutes:  # Less than 100m movement
                # End current segment
                if len(current_segment) > 1:
                    mode_detection = self.detect_transport_mode(current_segment)
                    segments.append({
                        "start_time": current_segment[0]["timestamp"],
                        "end_time": current_segment[-1]["timestamp"],
                        "points": current_segment,
                        "detected_mode": mode_detection["mode"],
                        "confidence": mode_detection["confidence"]
                    })
                
                # Start new segment
                current_segment = [curr_point]
            else:
                current_segment.append(curr_point)
        
        # Add final segment
        if len(current_segment) > 1:
            mode_detection = self.detect_transport_mode(current_segment)
            segments.append({
                "start_time": current_segment[0]["timestamp"],
                "end_time": current_segment[-1]["timestamp"],
                "points": current_segment,
                "detected_mode": mode_detection["mode"],
                "confidence": mode_detection["confidence"]
            })
        
        return segments