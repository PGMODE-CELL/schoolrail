from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List
from app.core.security import get_current_user
from app.services.notification_service import (
    get_user_notifications,
    create_notification,
    mark_notification_read,
    mark_all_read,
    delete_notification,
    send_push_notification,
    send_bulk_notification,
    get_notification_stats,
)
from app.schemas.notification import (
    NotificationCreate,
    NotificationResponse,
    PushNotificationPayload,
)

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get("/", response_model=List[NotificationResponse])
async def list_notifications(
    unread_only: bool = Query(False),
    current_user=Depends(get_current_user)
):
    return get_user_notifications(
        user_id=current_user.id,
        user_type=current_user.role,
        unread_only=unread_only
    )


@router.post("/", response_model=NotificationResponse)
async def create_new_notification(
    notification_data: NotificationCreate,
    current_user=Depends(get_current_user)
):
    return create_notification(notification_data)


@router.post("/mark-read/{notification_id}")
async def mark_read(notification_id: int, current_user=Depends(get_current_user)):
    if not mark_notification_read(notification_id, current_user.id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification marked as read"}


@router.post("/mark-all-read")
async def mark_all_notifications_read(current_user=Depends(get_current_user)):
    result = mark_all_read(user_id=current_user.id, user_type=current_user.role)
    return result


@router.delete("/{notification_id}")
async def delete_notification_by_id(notification_id: int, current_user=Depends(get_current_user)):
    if not delete_notification(notification_id, current_user.id):
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"message": "Notification deleted"}


@router.post("/push")
async def send_push(payload: PushNotificationPayload, current_user=Depends(get_current_user)):
    result = send_push_notification(payload)
    return result


@router.post("/bulk")
async def send_bulk(
    user_ids: List[int],
    user_type: str,
    title: str,
    message: str,
    notification_type: str = "info",
    current_user=Depends(get_current_user)
):
    result = send_bulk_notification(user_ids, user_type, title, message, notification_type)
    return result


@router.get("/stats")
async def notification_statistics(current_user=Depends(get_current_user)):
    return get_notification_stats(user_id=current_user.id, user_type=current_user.role)
