from typing import Optional, Dict, Any, List, Set
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
import asyncio
import json
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.user_connections: Dict[int, Set[WebSocket]] = {}
        self.route_subscribers: Dict[int, Set[WebSocket]] = {}
        self.vehicle_subscribers: Dict[int, Set[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, user_id: int, role: str):
        await websocket.accept()
        
        conn_id = f"{role}_{user_id}_{id(websocket)}"
        
        if conn_id not in self.active_connections:
            self.active_connections[conn_id] = []
        self.active_connections[conn_id].append(websocket)
        
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)
        
        logger.info(f"WebSocket connected: {conn_id}")
        return conn_id
    
    def disconnect(self, websocket: WebSocket, user_id: int, conn_id: str = None):
        if conn_id and conn_id in self.active_connections:
            if websocket in self.active_connections[conn_id]:
                self.active_connections[conn_id].remove(websocket)
            if not self.active_connections[conn_id]:
                del self.active_connections[conn_id]
        
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]
        
        for route_id, subscribers in self.route_subscribers.items():
            subscribers.discard(websocket)
        
        for vehicle_id, subscribers in self.vehicle_subscribers.items():
            subscribers.discard(websocket)
        
        logger.info(f"WebSocket disconnected: {conn_id}")
    
    def subscribe_to_route(self, websocket: WebSocket, route_id: int):
        if route_id not in self.route_subscribers:
            self.route_subscribers[route_id] = set()
        self.route_subscribers[route_id].add(websocket)
        logger.info(f"WebSocket subscribed to route {route_id}")
    
    def unsubscribe_from_route(self, websocket: WebSocket, route_id: int):
        if route_id in self.route_subscribers:
            self.route_subscribers[route_id].discard(websocket)
    
    def subscribe_to_vehicle(self, websocket: WebSocket, vehicle_id: int):
        if vehicle_id not in self.vehicle_subscribers:
            self.vehicle_subscribers[vehicle_id] = set()
        self.vehicle_subscribers[vehicle_id].add(websocket)
        logger.info(f"WebSocket subscribed to vehicle {vehicle_id}")
    
    def unsubscribe_from_vehicle(self, websocket: WebSocket, vehicle_id: int):
        if vehicle_id in self.vehicle_subscribers:
            self.vehicle_subscribers[vehicle_id].discard(websocket)
    
    async def send_personal_message(self, message: Dict, user_id: int):
        if user_id in self.user_connections:
            disconnected = []
            for websocket in self.user_connections[user_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending personal message: {str(e)}")
                    disconnected.append(websocket)
            
            for ws in disconnected:
                self.user_connections[user_id].discard(ws)
    
    async def broadcast_to_route(self, message: Dict, route_id: int):
        if route_id in self.route_subscribers:
            disconnected = []
            for websocket in self.route_subscribers[route_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to route: {str(e)}")
                    disconnected.append(websocket)
            
            for ws in disconnected:
                self.route_subscribers[route_id].discard(ws)
    
    async def broadcast_to_vehicle(self, message: Dict, vehicle_id: int):
        if vehicle_id in self.vehicle_subscribers:
            disconnected = []
            for websocket in self.vehicle_subscribers[vehicle_id]:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to vehicle: {str(e)}")
                    disconnected.append(websocket)
            
            for ws in disconnected:
                self.vehicle_subscribers[vehicle_id].discard(ws)
    
    async def broadcast_to_all(self, message: Dict):
        for conn_id, websockets in list(self.active_connections.items()):
            disconnected = []
            for websocket in websockets:
                try:
                    await websocket.send_json(message)
                except Exception as e:
                    logger.error(f"Error broadcasting: {str(e)}")
                    disconnected.append(websocket)
            
            for ws in disconnected:
                websockets.discard(ws)
    
    def get_online_count(self) -> int:
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_route_subscriber_count(self, route_id: int) -> int:
        return len(self.route_subscribers.get(route_id, set()))
    
    def get_vehicle_subscriber_count(self, vehicle_id: int) -> int:
        return len(self.vehicle_subscribers.get(vehicle_id, set()))


manager = ConnectionManager()


class RealtimeEvents:
    @staticmethod
    def location_update(vehicle_id: int, latitude: float, longitude: float, speed: float, heading: float):
        return {
            "type": "location_update",
            "vehicle_id": vehicle_id,
            "data": {
                "latitude": latitude,
                "longitude": longitude,
                "speed": speed,
                "heading": heading,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def student_boarded(student_id: int, student_name: str, vehicle_id: int, stop_id: int):
        return {
            "type": "student_boarded",
            "data": {
                "student_id": student_id,
                "student_name": student_name,
                "vehicle_id": vehicle_id,
                "stop_id": stop_id,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def student_dropped(student_id: int, student_name: str, vehicle_id: int, stop_id: int):
        return {
            "type": "student_dropped",
            "data": {
                "student_id": student_id,
                "student_name": student_name,
                "vehicle_id": vehicle_id,
                "stop_id": stop_id,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def bus_arrival(route_id: int, stop_id: int, eta_minutes: int):
        return {
            "type": "bus_arrival",
            "data": {
                "route_id": route_id,
                "stop_id": stop_id,
                "eta_minutes": eta_minutes,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def alert(vehicle_id: int, alert_type: str, severity: str, message: str):
        return {
            "type": "alert",
            "data": {
                "vehicle_id": vehicle_id,
                "alert_type": alert_type,
                "severity": severity,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def route_update(route_id: int, status: str, message: str):
        return {
            "type": "route_update",
            "data": {
                "route_id": route_id,
                "status": status,
                "message": message,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def attendance_marked(route_id: int, student_id: int, status: str, marked_by: int):
        return {
            "type": "attendance_marked",
            "data": {
                "route_id": route_id,
                "student_id": student_id,
                "status": status,
                "marked_by": marked_by,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    @staticmethod
    def payment_received(student_id: int, amount: float, transaction_id: str):
        return {
            "type": "payment_received",
            "data": {
                "student_id": student_id,
                "amount": amount,
                "transaction_id": transaction_id,
                "timestamp": datetime.now().isoformat()
            }
        }


async def notify_location_update(vehicle_id: int, latitude: float, longitude: float, speed: float, heading: float):
    message = RealtimeEvents.location_update(vehicle_id, latitude, longitude, speed, heading)
    await manager.broadcast_to_vehicle(message, vehicle_id)


async def notify_student_boarded(student_id: int, student_name: str, vehicle_id: int, stop_id: int):
    message = RealtimeEvents.student_boarded(student_id, student_name, vehicle_id, stop_id)
    await manager.broadcast_to_vehicle(message, vehicle_id)


async def notify_student_dropped(student_id: int, student_name: str, vehicle_id: int, stop_id: int):
    message = RealtimeEvents.student_dropped(student_id, student_name, vehicle_id, stop_id)
    await manager.broadcast_to_vehicle(message, vehicle_id)


async def notify_bus_arrival(route_id: int, stop_id: int, eta_minutes: int):
    message = RealtimeEvents.bus_arrival(route_id, stop_id, eta_minutes)
    await manager.broadcast_to_route(message, route_id)


async def notify_alert(vehicle_id: int, alert_type: str, severity: str, message: str):
    message = RealtimeEvents.alert(vehicle_id, alert_type, severity, message)
    await manager.broadcast_to_vehicle(message, vehicle_id)
    await manager.broadcast_to_all(message)


async def notify_attendance_update(route_id: int, student_id: int, status: str, marked_by: int):
    message = RealtimeEvents.attendance_marked(route_id, student_id, status, marked_by)
    await manager.broadcast_to_route(message, route_id)


async def notify_payment(student_id: int, amount: float, transaction_id: str):
    message = RealtimeEvents.payment_received(student_id, amount, transaction_id)
    await manager.send_personal_message(message, user_id=student_id)
