from typing import Dict, List, Set
from fastapi import WebSocket
import json
import asyncio
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.services.mode_detection import ModeDetectionService
from app.services.analytics_service import AnalyticsService

class WebSocketService:
    def __init__(self):
        # Active connections
        self.dashboard_connections: List[WebSocket] = []
        self.user_tracking_connections: Dict[str, WebSocket] = {}
        
        # Subscription management
        self.dashboard_subscriptions: Dict[WebSocket, Set[str]] = {}
        
        # Services
        self.mode_detection = ModeDetectionService()
        
        # Background tasks
        self.running_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect_dashboard(self, websocket: WebSocket):
        """Connect research dashboard WebSocket"""
        await websocket.accept()
        self.dashboard_connections.append(websocket)
        self.dashboard_subscriptions[websocket] = set()
        
        # Send initial connection message
        await websocket.send_text(json.dumps({
            "type": "connection_established",
            "message": "Connected to NATPAC live dashboard",
            "timestamp": datetime.utcnow().isoformat()
        }))
        
        # Start periodic updates if this is the first dashboard connection
        if len(self.dashboard_connections) == 1:
            await self._start_dashboard_updates()
    
    async def disconnect_dashboard(self, websocket: WebSocket):
        """Disconnect research dashboard WebSocket"""
        if websocket in self.dashboard_connections:
            self.dashboard_connections.remove(websocket)
        
        if websocket in self.dashboard_subscriptions:
            del self.dashboard_subscriptions[websocket]
        
        # Stop updates if no more dashboard connections
        if len(self.dashboard_connections) == 0:
            await self._stop_dashboard_updates()
    
    async def connect_user_tracking(self, websocket: WebSocket, user_id: str):
        """Connect user trip tracking WebSocket"""
        await websocket.accept()
        self.user_tracking_connections[user_id] = websocket
        
        # Send connection confirmation
        await websocket.send_text(json.dumps({
            "type": "tracking_started",
            "user_id": user_id,
            "message": "Real-time trip tracking activated",
            "timestamp": datetime.utcnow().isoformat()
        }))
    
    async def disconnect_user_tracking(self, websocket: WebSocket, user_id: str):
        """Disconnect user trip tracking WebSocket"""
        if user_id in self.user_tracking_connections:
            del self.user_tracking_connections[user_id]
    
    async def subscribe_to_updates(self, websocket: WebSocket, channels: List[str]):
        """Subscribe dashboard to specific update channels"""
        if websocket in self.dashboard_subscriptions:
            self.dashboard_subscriptions[websocket].update(channels)
            
            await websocket.send_text(json.dumps({
                "type": "subscription_updated",
                "subscribed_channels": list(self.dashboard_subscriptions[websocket]),
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    async def unsubscribe_from_updates(self, websocket: WebSocket, channels: List[str]):
        """Unsubscribe dashboard from update channels"""
        if websocket in self.dashboard_subscriptions:
            self.dashboard_subscriptions[websocket] -= set(channels)
            
            await websocket.send_text(json.dumps({
                "type": "subscription_updated",
                "subscribed_channels": list(self.dashboard_subscriptions[websocket]),
                "timestamp": datetime.utcnow().isoformat()
            }))
    
    async def process_location_update(self, user_id: str, location_data: Dict, db: AsyncIOMotorDatabase):
        """Process real-time location update from mobile app"""
        try:
            # Add timestamp if not present
            if "timestamp" not in location_data:
                location_data["timestamp"] = datetime.utcnow()
            elif isinstance(location_data["timestamp"], str):
                location_data["timestamp"] = datetime.fromisoformat(location_data["timestamp"])
            
            # Store location update in temporary collection for processing
            await db.live_locations.insert_one({
                "user_id": user_id,
                "location": location_data,
                "processed": False,
                "created_at": datetime.utcnow()
            })
            
            # Send acknowledgment to mobile app
            if user_id in self.user_tracking_connections:
                websocket = self.user_tracking_connections[user_id]
                await websocket.send_text(json.dumps({
                    "type": "location_received",
                    "status": "success",
                    "timestamp": datetime.utcnow().isoformat()
                }))
            
            # Process location for mode detection
            await self._process_user_location_for_detection(user_id, location_data, db)
            
            # Broadcast to dashboard if subscribed to live tracking
            await self._broadcast_location_update(user_id, location_data)
            
        except Exception as e:
            print(f"Error processing location update: {e}")
            if user_id in self.user_tracking_connections:
                websocket = self.user_tracking_connections[user_id]
                await websocket.send_text(json.dumps({
                    "type": "location_error",
                    "error": str(e),
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    async def _process_user_location_for_detection(self, user_id: str, location_data: Dict, db: AsyncIOMotorDatabase):
        """Process location data for transport mode detection"""
        # Get recent location points for this user
        recent_locations = await db.live_locations.find({
            "user_id": user_id,
            "created_at": {"$gte": datetime.utcnow() - timedelta(minutes=30)}
        }).sort("created_at", 1).to_list(None)
        
        if len(recent_locations) >= 3:
            # Extract GPS points
            gps_points = []
            for loc in recent_locations:
                gps_points.append({
                    "lat": loc["location"]["lat"],
                    "lng": loc["location"]["lng"],
                    "timestamp": loc["created_at"]
                })
            
            # Detect transport mode
            mode_detection = self.mode_detection.detect_transport_mode(gps_points)
            
            # Send mode detection to user
            if user_id in self.user_tracking_connections:
                websocket = self.user_tracking_connections[user_id]
                await websocket.send_text(json.dumps({
                    "type": "mode_detection",
                    "detected_mode": mode_detection["mode"],
                    "confidence": mode_detection["confidence"],
                    "features": mode_detection["features"],
                    "timestamp": datetime.utcnow().isoformat()
                }))
    
    async def _broadcast_location_update(self, user_id: str, location_data: Dict):
        """Broadcast location update to subscribed dashboards"""
        message = {
            "type": "live_location",
            "user_id": user_id[:8],  # Anonymized user ID
            "location": {
                "lat": location_data["lat"],
                "lng": location_data["lng"]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to dashboards subscribed to live tracking
        disconnected = []
        for websocket in self.dashboard_connections:
            if "live_tracking" in self.dashboard_subscriptions.get(websocket, set()):
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    disconnected.append(websocket)
        
        # Clean up disconnected websockets
        for ws in disconnected:
            await self.disconnect_dashboard(ws)
    
    async def _start_dashboard_updates(self):
        """Start periodic updates for dashboard"""
        # Start background task for periodic analytics updates
        if "dashboard_analytics" not in self.running_tasks:
            self.running_tasks["dashboard_analytics"] = asyncio.create_task(
                self._periodic_analytics_updates()
            )
    
    async def _stop_dashboard_updates(self):
        """Stop periodic updates for dashboard"""
        for task_name, task in self.running_tasks.items():
            if not task.done():
                task.cancel()
        
        self.running_tasks.clear()
    
    async def _periodic_analytics_updates(self):
        """Send periodic analytics updates to dashboard"""
        while True:
            try:
                await asyncio.sleep(30)  # Update every 30 seconds
                
                if not self.dashboard_connections:
                    break
                
                # Generate summary statistics
                current_time = datetime.utcnow()
                update_message = {
                    "type": "periodic_update",
                    "data": {
                        "active_users": len(self.user_tracking_connections),
                        "dashboard_connections": len(self.dashboard_connections),
                        "last_update": current_time.isoformat()
                    },
                    "timestamp": current_time.isoformat()
                }
                
                # Send to all connected dashboards
                disconnected = []
                for websocket in self.dashboard_connections:
                    try:
                        await websocket.send_text(json.dumps(update_message))
                    except:
                        disconnected.append(websocket)
                
                # Clean up disconnected websockets
                for ws in disconnected:
                    await self.disconnect_dashboard(ws)
                    
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Error in periodic updates: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def broadcast_trip_completion(self, user_id: str, trip_data: Dict):
        """Broadcast trip completion to dashboard"""
        message = {
            "type": "trip_completed",
            "user_id": user_id[:8],  # Anonymized
            "trip_summary": {
                "purpose": trip_data.get("trip_purpose"),
                "total_cost": trip_data.get("total_cost"),
                "total_distance": trip_data.get("total_distance_km"),
                "modes_used": [segment["mode"] for segment in trip_data.get("trip_chain", [])],
                "duration_minutes": trip_data.get("total_duration_minutes")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to subscribed dashboards
        for websocket in self.dashboard_connections:
            if "trip_completions" in self.dashboard_subscriptions.get(websocket, set()):
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    pass
    
    async def broadcast_food_entry(self, user_id: str, food_data: Dict):
        """Broadcast food entry to dashboard"""
        message = {
            "type": "food_entry",
            "user_id": user_id[:8],  # Anonymized
            "food_summary": {
                "cuisine_type": food_data.get("location", {}).get("cuisine_type"),
                "meal_type": food_data.get("meal_type"),
                "total_cost": food_data.get("total_cost"),
                "restaurant_type": food_data.get("location", {}).get("establishment_type"),
                "cultural_authenticity": food_data.get("cultural_authenticity_rating")
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Send to subscribed dashboards
        for websocket in self.dashboard_connections:
            if "food_entries" in self.dashboard_subscriptions.get(websocket, set()):
                try:
                    await websocket.send_text(json.dumps(message))
                except:
                    pass