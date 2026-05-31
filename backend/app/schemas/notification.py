from datetime import date, datetime, timedelta
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum


class NotificationTypeEnum(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    EMERGENCY = "emergency"


class NotificationCreate(BaseModel):
    user_id: int
    user_type: str
    title: str
    message: str
    type: NotificationTypeEnum = NotificationTypeEnum.INFO
    data: Optional[Dict[str, Any]] = None


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    user_type: str
    title: str
    message: str
    type: str
    is_read: bool = False
    data: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class NotificationPreferences(BaseModel):
    user_id: int
    push_enabled: bool = True
    email_enabled: bool = True
    sms_enabled: bool = False
    notifications_enabled: bool = True
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None


class PushNotificationPayload(BaseModel):
    title: str
    body: str
    data: Optional[Dict[str, Any]] = None
    icon: Optional[str] = None
    badge: Optional[int] = None
    sound: Optional[str] = "default"


class NotificationFilter(BaseModel):
    user_id: int
    user_type: str
    notification_type: Optional[NotificationTypeEnum] = None
    is_read: Optional[bool] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    limit: int = 50
    offset: int = 0


class NotificationSummary(BaseModel):
    total: int
    unread: int
    read: int
    by_type: Dict[str, int]
