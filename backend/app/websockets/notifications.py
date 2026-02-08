import uuid
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.notification import NotificationCreate, NotificationType

router = APIRouter()


class ConnectionManager:
    """Manages WebSocket connections per user for real-time notifications."""

    def __init__(self) -> None:
        self.active_connections: dict[uuid.UUID, list[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id: uuid.UUID) -> None:
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    def disconnect(self, websocket: WebSocket, user_id: uuid.UUID) -> None:
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def send_notification(self, user_id: uuid.UUID, data: dict[str, Any]) -> None:
        """Send notification to all connections for a user."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(data)


manager = ConnectionManager()


@router.websocket("/ws/notifications/{user_id}")
async def websocket_notifications(websocket: WebSocket, user_id: uuid.UUID) -> None:
    """
    WebSocket endpoint for real-time notifications.
    Frontend connects here to receive instant notification updates.
    """
    await manager.connect(websocket, user_id)
    try:
        while True:
            # Keep connection alive, listen for any client messages
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket, user_id)


async def notify_user(
    user_id: uuid.UUID,
    notification_type: NotificationType,
    message: str,
    reference_id: uuid.UUID | None = None,
) -> None:
    """
    Helper function to send real-time notification to a user.
    Call this when a mention or like occurs.
    """
    await manager.send_notification(
        user_id,
        {
            "type": notification_type.value,
            "message": message,
            "reference_id": str(reference_id) if reference_id else None,
        },
    )


def create_notification_for_mention(
    mentioned_user_id: uuid.UUID,
    mentioner_name: str,
    item_id: uuid.UUID,
) -> NotificationCreate:
    """Create notification data for @username mention."""
    return NotificationCreate(
        user_id=mentioned_user_id,
        type=NotificationType.MENTION,
        message=f"{mentioner_name} mentioned you",
        reference_id=item_id,
    )


def create_notification_for_like(
    item_owner_id: uuid.UUID,
    liker_name: str,
    item_id: uuid.UUID,
) -> NotificationCreate:
    """Create notification data for likes."""
    return NotificationCreate(
        user_id=item_owner_id,
        type=NotificationType.LIKE,
        message=f"{liker_name} liked your item",
        reference_id=item_id,
    )
