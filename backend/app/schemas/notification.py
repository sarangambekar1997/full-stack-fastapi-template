# Re-export notification models for backwards compatibility
from app.models import (
    Notification,
    NotificationBase,
    NotificationCreate,
    NotificationPublic,
    NotificationsPublic,
    NotificationType,
)

__all__ = [
    "Notification",
    "NotificationBase",
    "NotificationCreate",
    "NotificationPublic",
    "NotificationsPublic",
    "NotificationType",
]
