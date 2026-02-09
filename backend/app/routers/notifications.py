import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import CurrentUser, SessionDep
from app.models import Message
from app.schemas.notification import (
    Notification,
    NotificationPublic,
    NotificationsPublic,
)

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("/", response_model=NotificationsPublic)
def read_notifications(
    session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100
) -> Any:
    """
    Retrieve notifications for current user.
    """
    count_statement = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == current_user.id)
    )
    count = session.exec(count_statement).one()

    unread_statement = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)  # noqa: E712
    )
    unread_count = session.exec(unread_statement).one()

    statement = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(col(Notification.created_at).desc())
        .offset(skip)
        .limit(limit)
    )
    notifications = session.exec(statement).all()

    return NotificationsPublic(data=notifications, count=count, unread_count=unread_count)


@router.get("/unread-count")
def get_unread_count(session: SessionDep, current_user: CurrentUser) -> dict[str, int]:
    """
    Get unread notification count for bell icon badge.
    """
    statement = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)  # noqa: E712
    )
    unread_count = session.exec(statement).one()
    return {"unread_count": unread_count}


@router.get("/{id}", response_model=NotificationPublic)
def read_notification(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Get notification by ID.
    """
    notification = session.get(Notification, id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    return notification


@router.put("/{id}/read", response_model=NotificationPublic)
def mark_as_read(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Any:
    """
    Mark notification as read.
    """
    notification = session.get(Notification, id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    notification.is_read = True
    session.add(notification)
    session.commit()
    session.refresh(notification)
    return notification


@router.put("/read-all")
def mark_all_as_read(session: SessionDep, current_user: CurrentUser) -> Message:
    """
    Mark all notifications as read.
    """
    statement = (
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .where(Notification.is_read == False)  # noqa: E712
    )
    notifications = session.exec(statement).all()
    for notification in notifications:
        notification.is_read = True
        session.add(notification)
    session.commit()
    return Message(message="All notifications marked as read")


@router.delete("/{id}")
def delete_notification(
    session: SessionDep, current_user: CurrentUser, id: uuid.UUID
) -> Message:
    """
    Delete a notification.
    """
    notification = session.get(Notification, id)
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
    if notification.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not enough permissions")
    session.delete(notification)
    session.commit()
    return Message(message="Notification deleted successfully")
