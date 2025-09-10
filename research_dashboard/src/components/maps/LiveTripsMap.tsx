import React, { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Box, Typography, Chip } from '@mui/material';

import { useWebSocket } from '../../hooks/useWebSocket';
import { useApi } from '../../hooks/useApi';

// Fix for default markers in react-leaflet
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

interface LiveTrip {
  trip_id: string;
  user_type: string;
  location: {
    lat: number;
    lng: number;
    name: string;
  };
  transport_mode: string;
  trip_purpose: string;
  group_size: number;
  started_at: string;
}

const LiveTripsMap: React.FC = () => {
  const [activeTrips, setActiveTrips] = useState<LiveTrip[]>([]);
  const [center, setCenter] = useState<[number, number]>([8.5241, 76.9366]); // Kochi, Kerala
  const { get } = useApi();

  // WebSocket connection for real-time updates
  const { messages, sendMessage, isConnected } = useWebSocket('/ws/live-dashboard');

  useEffect(() => {
    loadActiveTrips();
    
    // Subscribe to live updates
    if (isConnected) {
      sendMessage({
        type: 'subscribe',
        channels: ['live_tracking', 'trip_completions']
      });
    }
  }, [isConnected]);

  useEffect(() => {
    // Handle WebSocket messages
    if (messages.length > 0) {
      const latestMessage = messages[messages.length - 1];
      
      if (latestMessage.type === 'live_location') {
        // Update trip location
        setActiveTrips(prev => {
          const updated = prev.map(trip => 
            trip.trip_id === latestMessage.user_id ? {
              ...trip,
              location: latestMessage.location
            } : trip
          );
          return updated;
        });
      } else if (latestMessage.type === 'trip_completed') {
        // Remove completed trip
        setActiveTrips(prev => 
          prev.filter(trip => trip.trip_id !== latestMessage.user_id)
        );
      }
    }
  }, [messages]);

  const loadActiveTrips = async () => {
    try {
      const response = await get('/analytics/live/active-trips');
      setActiveTrips(response.data || []);
    } catch (error) {
      console.error('Error loading active trips:', error);
    }
  };

  const getMarkerColor = (transportMode: string): string => {
    switch (transportMode.toLowerCase()) {
      case 'walk':
        return '#4CAF50';
      case 'bicycle':
        return '#2196F3';
      case 'car':
        return '#FF9800';
      case 'bus':
        return '#9C27B0';
      case 'train':
        return '#F44336';
      case 'auto_rickshaw':
        return '#FFEB3B';
      default:
        return '#757575';
    }
  };

  const createCustomIcon = (color: string, transportMode: string) => {
    return L.divIcon({
      html: `
        <div style="
          background-color: ${color};
          width: 20px;
          height: 20px;
          border-radius: 50%;
          border: 2px solid white;
          box-shadow: 0 2px 4px rgba(0,0,0,0.3);
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 10px;
          color: white;
          font-weight: bold;
        ">
          ${transportMode.charAt(0).toUpperCase()}
        </div>
      `,
      className: 'custom-marker',
      iconSize: [24, 24],
      iconAnchor: [12, 12]
    });
  };

  return (
    <Box sx={{ height: '100%', position: 'relative' }}>
      {/* Connection Status */}
      <Box sx={{ position: 'absolute', top: 10, right: 10, zIndex: 1000 }}>
        <Chip 
          label={isConnected ? 'Live' : 'Disconnected'} 
          color={isConnected ? 'success' : 'error'}
          size="small"
        />
      </Box>

      {/* Active Trip Count */}
      <Box sx={{ position: 'absolute', top: 10, left: 10, zIndex: 1000 }}>
        <Chip 
          label={`${activeTrips.length} Active Trips`} 
          color="primary"
          size="small"
        />
      </Box>

      <MapContainer 
        center={center} 
        zoom={10} 
        style={{ height: '100%', width: '100%' }}
      >
        <TileLayer
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        />
        
        {activeTrips.map((trip) => (
          <Marker
            key={trip.trip_id}
            position={[trip.location.lat, trip.location.lng]}
            icon={createCustomIcon(
              getMarkerColor(trip.transport_mode),
              trip.transport_mode
            )}
          >
            <Popup>
              <Box sx={{ minWidth: 200 }}>
                <Typography variant="subtitle2" fontWeight="bold">
                  {trip.user_type.charAt(0).toUpperCase() + trip.user_type.slice(1)} Trip
                </Typography>
                
                <Box sx={{ mt: 1, display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Mode:
                    </Typography>
                    <Typography variant="body2">
                      {trip.transport_mode.replace('_', ' ')}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Purpose:
                    </Typography>
                    <Typography variant="body2">
                      {trip.trip_purpose}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Group Size:
                    </Typography>
                    <Typography variant="body2">
                      {trip.group_size} {trip.group_size === 1 ? 'person' : 'people'}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                    <Typography variant="body2" color="text.secondary">
                      Started:
                    </Typography>
                    <Typography variant="body2">
                      {new Date(trip.started_at).toLocaleTimeString()}
                    </Typography>
                  </Box>
                </Box>

                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Location: {trip.location.name || 'Unknown'}
                  </Typography>
                </Box>
              </Box>
            </Popup>
          </Marker>
        ))}
      </MapContainer>
    </Box>
  );
};

export default LiveTripsMap;