from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
from typing import Dict, List
import json
import asyncio
from datetime import datetime

from app.core.database import get_database
from app.services.websocket_service import WebSocketService

router = APIRouter()
websocket_service = WebSocketService()

@router.websocket("/live-dashboard")
async def websocket_live_dashboard(websocket: WebSocket, db=Depends(get_database)):
    """WebSocket endpoint for live dashboard updates"""
    await websocket_service.connect_dashboard(websocket)
    
    try:
        while True:
            # Wait for messages from client
            data = await websocket.receive_text()
            message = json.loads(data)
            
            # Handle different message types
            if message["type"] == "subscribe":
                await websocket_service.subscribe_to_updates(websocket, message["channels"])
            elif message["type"] == "unsubscribe":
                await websocket_service.unsubscribe_from_updates(websocket, message["channels"])
            
    except WebSocketDisconnect:
        await websocket_service.disconnect_dashboard(websocket)

@router.websocket("/trip-tracking/{user_id}")
async def websocket_trip_tracking(websocket: WebSocket, user_id: str, db=Depends(get_database)):
    """WebSocket endpoint for real-time trip tracking"""
    await websocket_service.connect_user_tracking(websocket, user_id)
    
    try:
        while True:
            # Receive location updates from mobile app
            data = await websocket.receive_text()
            location_data = json.loads(data)
            
            # Process location update
            await websocket_service.process_location_update(user_id, location_data, db)
            
    except WebSocketDisconnect:
        await websocket_service.disconnect_user_tracking(websocket, user_id)