"""
SchoolRail Notifications Service
Handles all types of notifications: Push, SMS, Email, In-App
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
import json


class NotificationService:
    """Comprehensive notification service"""
    
    def __init__(self):
        self.templates = self._load_templates()
        self.history = []
    
    def _load_templates(self) -> Dict[str, Dict]:
        """Load notification templates"""
        return {
            "student_pickup": {
                "title": "Student Picked Up",
                "body": "{student_name} has been picked up from {stop_name} by {vehicle}",
                "data": {"type": "pickup", "student_id": "", "stop_id": ""}
            },
            "student_drop": {
                "title": "Student Dropped",
                "body": "{student_name} has been dropped at {location}",
                "data": {"type": "dropoff", "student_id": "", "location_id": ""}
            },
            "bus_delayed": {
                "title": "Bus Delay Alert",
                "body": "Route {route} is delayed by {delay} minutes. New ETA: {eta}",
                "data": {"type": "delay", "route_id": "", "delay": ""}
            },
            "attendance_alert": {
                "title": "Attendance Update",
                "body": "{student_name} marked as {status} on Route {route}",
                "data": {"type": "attendance", "student_id": ""}
            },
            "fee_reminder": {
                "title": "Fee Payment Reminder",
                "body": "Fee of ₹{amount} is due on {due_date}. Please make payment to avoid late charges.",
                "data": {"type": "fee", "fee_id": ""}
            },
            "emergency_alert": {
                "title": "Emergency Alert",
                "body": "{message}",
                "data": {"type": "emergency"}
            },
            "trip_started": {
                "title": "Trip Started",
                "body": "Bus {vehicle} has started {route}. Estimated arrival: {eta}",
                "data": {"type": "trip_start", "trip_id": ""}
            },
            "trip_completed": {
                "title": "Trip Completed",
                "body": "{route} trip completed successfully. {students_count} students delivered.",
                "data": {"type": "trip_end", "trip_id": ""}
            }
        }
    
    def send_notification(
        self,
        user_id: str,
        notification_type: str,
        channel: str = "push",
        data: Optional[Dict] = None
    ) -> Dict:
        """Send notification to a user"""
        notification = {
            "id": f"notif_{datetime.now().timestamp()}",
            "user_id": user_id,
            "type": notification_type,
            "channel": channel,
            "data": data or {},
            "timestamp": datetime.now().isoformat(),
            "status": "sent"
        }
        
        # Simulate sending based on channel
        if channel == "push":
            notification["sent_via"] = "FCM"
        elif channel == "sms":
            notification["sent_via"] = "Twilio"
        elif channel == "email":
            notification["sent_via"] = "SendGrid"
        else:
            notification["sent_via"] = "In-App"
        
        self.history.append(notification)
        return notification
    
    def send_bulk_notification(
        self,
        user_ids: List[str],
        notification_type: str,
        channel: str = "push",
        data: Optional[Dict] = None
    ) -> Dict:
        """Send notification to multiple users"""
        results = []
        for user_id in user_ids:
            result = self.send_notification(user_id, notification_type, channel, data)
            results.append(result)
        
        return {
            "total": len(user_ids),
            "sent": len(results),
            "failed": 0,
            "notifications": results
        }
    
    def send_template_notification(
        self,
        user_id: str,
        template_name: str,
        variables: Dict[str, str],
        channels: List[str] = ["push"]
    ) -> Dict:
        """Send notification using template"""
        template = self.templates.get(template_name)
        if not template:
            return {"error": "Template not found"}
        
        title = template["title"]
        body = template["body"].format(**variables)
        data = {**template["data"], **variables}
        
        results = []
        for channel in channels:
            result = self.send_notification(user_id, template_name, channel, {
                "title": title,
                "body": body,
                "data": data
            })
            results.append(result)
        
        return {
            "template": template_name,
            "channels": channels,
            "results": results
        }
    
    def get_user_notifications(
        self,
        user_id: str,
        limit: int = 20,
        unread_only: bool = False
    ) -> List[Dict]:
        """Get notifications for a user"""
        user_notifications = [
            n for n in self.history 
            if n["user_id"] == user_id
        ]
        
        if unread_only:
            user_notifications = [
                n for n in user_notifications 
                if n.get("read", False) == False
            ]
        
        return user_notifications[:limit]
    
    def mark_as_read(self, notification_id: str) -> bool:
        """Mark notification as read"""
        for notif in self.history:
            if notif["id"] == notification_id:
                notif["read"] = True
                notif["read_at"] = datetime.now().isoformat()
                return True
        return False
    
    def get_notification_preferences(self, user_id: str) -> Dict:
        """Get user notification preferences"""
        return {
            "push_enabled": True,
            "email_enabled": True,
            "sms_enabled": False,
            "categories": {
                "attendance": True,
                "fees": True,
                "alerts": True,
                "updates": True,
                "marketing": False
            },
            "quiet_hours": {
                "enabled": True,
                "start": "22:00",
                "end": "07:00"
            }
        }
    
    def update_preferences(
        self,
        user_id: str,
        preferences: Dict
    ) -> Dict:
        """Update user notification preferences"""
        return {
            "user_id": user_id,
            "preferences": preferences,
            "updated_at": datetime.now().isoformat()
        }
    
    def create_scheduled_notification(
        self,
        user_id: str,
        notification_type: str,
        scheduled_time: datetime,
        data: Dict
    ) -> Dict:
        """Schedule a notification for later"""
        return {
            "id": f"scheduled_{datetime.now().timestamp()}",
            "user_id": user_id,
            "type": notification_type,
            "scheduled_at": scheduled_time.isoformat(),
            "data": data,
            "status": "scheduled"
        }
    
    def get_notification_stats(self, user_id: str) -> Dict:
        """Get notification statistics for user"""
        user_notifications = self.get_user_notifications(user_id, limit=100)
        
        return {
            "total": len(user_notifications),
            "unread": len([n for n in user_notifications if not n.get("read", False)]),
            "by_type": self._group_by_type(user_notifications),
            "by_channel": self._group_by_channel(user_notifications)
        }
    
    def _group_by_type(self, notifications: List[Dict]) -> Dict:
        """Group notifications by type"""
        grouped = {}
        for notif in notifications:
            notif_type = notif.get("type", "unknown")
            grouped[notif_type] = grouped.get(notif_type, 0) + 1
        return grouped
    
    def _group_by_channel(self, notifications: List[Dict]) -> Dict:
        """Group notifications by channel"""
        grouped = {}
        for notif in notifications:
            channel = notif.get("channel", "unknown")
            grouped[channel] = grouped.get(channel, 0) + 1
        return grouped


# Singleton instance
notification_service = NotificationService()


def get_user_notifications(user_id: str, limit: int = 20, unread_only: bool = False, user_type: Optional[str] = None) -> List[Dict]:
    """Standalone function to get user notifications"""
    return notification_service.get_user_notifications(user_id, limit, unread_only)


def create_notification(notification_data: Any) -> Dict:
    """Standalone function to create a notification"""
    if hasattr(notification_data, 'model_dump'):
        data = notification_data.model_dump()
    elif hasattr(notification_data, 'dict'):
        data = notification_data.dict()
    else:
        data = notification_data
    
    return notification_service.send_notification(
        user_id=str(data.get("user_id", "")),
        notification_type=data.get("type", "info"),
        channel="in_app",
        data={
            "title": data.get("title", ""),
            "body": data.get("message", ""),
        }
    )


def mark_notification_read(notification_id: str) -> bool:
    """Standalone function to mark notification as read"""
    return notification_service.mark_as_read(notification_id)


def mark_all_read(user_id: str, user_type: Optional[str] = None) -> bool:
    """Standalone function to mark all notifications as read for a user"""
    count = 0
    for notif in notification_service.history:
        if notif.get("user_id") == user_id and not notif.get("read", False):
            notif["read"] = True
            notif["read_at"] = datetime.now().isoformat()
            count += 1
    return count > 0


def delete_notification(notification_id: str, user_id: Optional[str] = None) -> bool:
    """Standalone function to delete a notification"""
    for i, notif in enumerate(notification_service.history):
        if notif.get("id") == notification_id:
            if user_id and notif.get("user_id") != user_id:
                continue
            notification_service.history.pop(i)
            return True
    return False


def send_push_notification(user_id: str, title: str, body: str, data: Dict = None) -> Dict:
    """Standalone function to send push notification"""
    return notification_service.send_notification(
        user_id=user_id,
        notification_type="push",
        channel="push",
        data={
            "title": title,
            "body": body,
            "extra": data or {}
        }
    )


def send_bulk_notification(user_ids: List[str], title: str, message: str, notification_type: str = "info") -> Dict:
    """Standalone function to send bulk notifications"""
    data = {"title": title, "body": message}
    return notification_service.send_bulk_notification(
        user_ids=[str(uid) for uid in user_ids],
        notification_type=notification_type,
        channel="push",
        data=data
    )


def get_notification_stats(user_id: str, user_type: Optional[str] = None) -> Dict:
    """Standalone function to get notification stats"""
    return notification_service.get_notification_stats(user_id)