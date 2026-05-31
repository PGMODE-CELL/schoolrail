from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from typing import Optional
import json
from app.core.security import decode_token
from app.core.websocket import manager, RealtimeEvents

router = APIRouter(tags=["WebSocket"])


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
    route_id: Optional[int] = Query(None),
    vehicle_id: Optional[int] = Query(None)
):
    user_id = 0
    role = "anonymous"
    
    if token:
        try:
            token_data = decode_token(token)
            user_id = token_data.user_id or 0
            role = token_data.role or "user"
        except Exception:
            pass
    
    conn_id = await manager.connect(websocket, user_id, role)
    
    if route_id:
        manager.subscribe_to_route(websocket, route_id)
    
    if vehicle_id:
        manager.subscribe_to_vehicle(websocket, vehicle_id)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "conn_id": conn_id,
            "message": "WebSocket connection established"
        })
        
        while True:
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                msg_type = message.get("type")
                
                if msg_type == "subscribe_route":
                    route_id = message.get("route_id")
                    if route_id:
                        manager.subscribe_to_route(websocket, route_id)
                        await websocket.send_json({"type": "subscribed", "route_id": route_id})
                
                elif msg_type == "unsubscribe_route":
                    route_id = message.get("route_id")
                    if route_id:
                        manager.unsubscribe_from_route(websocket, route_id)
                        await websocket.send_json({"type": "unsubscribed", "route_id": route_id})
                
                elif msg_type == "subscribe_vehicle":
                    vehicle_id = message.get("vehicle_id")
                    if vehicle_id:
                        manager.subscribe_to_vehicle(websocket, vehicle_id)
                        await websocket.send_json({"type": "subscribed", "vehicle_id": vehicle_id})
                
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong", "timestamp": RealtimeEvents.location_update(0, 0, 0, 0, 0)["data"]["timestamp"]})
                
                else:
                    await websocket.send_json({"type": "error", "message": f"Unknown message type: {msg_type}"})
            
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "message": "Invalid JSON"})
    
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id, conn_id)


@router.websocket("/ws/location/{vehicle_id}")
async def websocket_location(websocket: WebSocket, vehicle_id: int):
    await manager.connect(websocket, 0, "location")
    manager.subscribe_to_vehicle(websocket, vehicle_id)
    
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, 0)


@router.get("/ws/stats")
async def websocket_stats():
    return {
        "total_connections": manager.get_online_count(),
        "active_routes": len(manager.route_subscribers),
        "active_vehicles": len(manager.vehicle_subscribers)
    }
