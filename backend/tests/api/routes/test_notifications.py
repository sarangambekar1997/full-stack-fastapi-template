import uuid

from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app.core.config import settings
from app.models import Notification, NotificationType, User
from app.services.mentions import parse_mentions
from tests.utils.user import create_random_user


def test_parse_mentions_single() -> None:
    """Test parsing a single @mention from text."""
    text = "Hello @admin@example.com, please check this"
    mentions = parse_mentions(text)
    assert len(mentions) == 1
    assert "admin@example.com" in mentions


def test_parse_mentions_multiple() -> None:
    """Test parsing multiple @mentions from text."""
    text = "Hey @user1@example.com and @user2@test.org, look at this"
    mentions = parse_mentions(text)
    assert len(mentions) == 2
    assert "user1@example.com" in mentions
    assert "user2@test.org" in mentions


def test_parse_mentions_duplicates() -> None:
    """Test that duplicate mentions are removed."""
    text = "@admin@example.com said @admin@example.com should check"
    mentions = parse_mentions(text)
    assert len(mentions) == 1
    assert "admin@example.com" in mentions


def test_parse_mentions_no_mentions() -> None:
    """Test parsing text with no mentions."""
    text = "This is a regular text without any mentions"
    mentions = parse_mentions(text)
    assert len(mentions) == 0


def test_parse_mentions_none() -> None:
    """Test parsing None text."""
    mentions = parse_mentions(None)
    assert len(mentions) == 0


def test_parse_mentions_empty() -> None:
    """Test parsing empty text."""
    mentions = parse_mentions("")
    assert len(mentions) == 0


def test_create_item_with_mention_creates_notification(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test that creating an item with @mention creates a notification."""
    # Create a user to be mentioned
    mentioned_user, _ = create_random_user(db)

    # Create an item mentioning that user
    data = {
        "title": "Test Item",
        "description": f"Check this @{mentioned_user.email}",
    }
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    item = response.json()

    # Verify notification was created
    db.expire_all()
    statement = select(Notification).where(
        Notification.user_id == mentioned_user.id,
        Notification.reference_id == uuid.UUID(item["id"]),
        Notification.type == NotificationType.MENTION,
    )
    notification = db.exec(statement).first()
    assert notification is not None
    assert notification.is_read is False
    assert "mentioned you" in notification.message


def test_create_item_self_mention_no_notification(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test that mentioning yourself does not create a notification."""
    # Get the superuser
    superuser_email = settings.FIRST_SUPERUSER
    statement = select(User).where(User.email == superuser_email)
    superuser = db.exec(statement).first()
    assert superuser is not None

    # Count notifications before
    count_before = len(
        db.exec(select(Notification).where(Notification.user_id == superuser.id)).all()
    )

    # Create an item mentioning yourself
    data = {
        "title": "Self Mention Test",
        "description": f"I mention myself @{superuser_email}",
    }
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200

    # Verify no new notification was created for self
    db.expire_all()
    count_after = len(
        db.exec(select(Notification).where(Notification.user_id == superuser.id)).all()
    )
    assert count_after == count_before


def test_read_notifications(client: TestClient, db: Session) -> None:
    """Test reading notifications for a user."""
    # Create a user and a notification for them
    user, password = create_random_user(db)
    notification = Notification(
        user_id=user.id,
        type=NotificationType.MENTION,
        message="Test notification",
        reference_id=uuid.uuid4(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Login as that user and fetch notifications
    login_data = {
        "username": user.email,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get notifications
    response = client.get(
        f"{settings.API_V1_STR}/notifications/",
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert "data" in content
    assert "count" in content
    assert "unread_count" in content
    assert content["count"] >= 1


def test_get_unread_count(client: TestClient, db: Session) -> None:
    """Test getting unread notification count."""
    # Create a user with unread notifications
    user, password = create_random_user(db)
    for i in range(3):
        notification = Notification(
            user_id=user.id,
            type=NotificationType.MENTION,
            message=f"Notification {i}",
            reference_id=uuid.uuid4(),
        )
        db.add(notification)
    db.commit()

    # Login as that user
    login_data = {
        "username": user.email,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Get unread count
    response = client.get(
        f"{settings.API_V1_STR}/notifications/unread-count",
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["unread_count"] >= 3


def test_mark_notification_as_read(client: TestClient, db: Session) -> None:
    """Test marking a notification as read."""
    # Create a user and notification
    user, password = create_random_user(db)
    notification = Notification(
        user_id=user.id,
        type=NotificationType.LIKE,
        message="Someone liked your item",
        reference_id=uuid.uuid4(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Login as that user
    login_data = {
        "username": user.email,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mark as read
    response = client.put(
        f"{settings.API_V1_STR}/notifications/{notification.id}/read",
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["is_read"] is True


def test_mark_all_notifications_as_read(client: TestClient, db: Session) -> None:
    """Test marking all notifications as read."""
    # Create a user with multiple unread notifications
    user, password = create_random_user(db)
    for i in range(3):
        notification = Notification(
            user_id=user.id,
            type=NotificationType.MENTION,
            message=f"Notification {i}",
            reference_id=uuid.uuid4(),
        )
        db.add(notification)
    db.commit()

    # Login as that user
    login_data = {
        "username": user.email,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Mark all as read
    response = client.put(
        f"{settings.API_V1_STR}/notifications/read-all",
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "All notifications marked as read"

    # Verify unread count is now 0
    response = client.get(
        f"{settings.API_V1_STR}/notifications/unread-count",
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["unread_count"] == 0


def test_delete_notification(client: TestClient, db: Session) -> None:
    """Test deleting a notification."""
    # Create a user and notification
    user, password = create_random_user(db)
    notification = Notification(
        user_id=user.id,
        type=NotificationType.MENTION,
        message="Delete me",
        reference_id=uuid.uuid4(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)
    notification_id = notification.id

    # Login as that user
    login_data = {
        "username": user.email,
        "password": password,
    }
    response = client.post(f"{settings.API_V1_STR}/login/access-token", data=login_data)
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Delete notification
    response = client.delete(
        f"{settings.API_V1_STR}/notifications/{notification_id}",
        headers=headers,
    )
    assert response.status_code == 200
    content = response.json()
    assert content["message"] == "Notification deleted successfully"

    # Verify it's deleted
    db.expire_all()
    deleted = db.get(Notification, notification_id)
    assert deleted is None


def test_read_notification_not_found(
    client: TestClient, superuser_token_headers: dict[str, str]
) -> None:
    """Test reading a non-existent notification."""
    response = client.get(
        f"{settings.API_V1_STR}/notifications/{uuid.uuid4()}",
        headers=superuser_token_headers,
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Notification not found"


def test_read_notification_not_owner(
    client: TestClient, normal_user_token_headers: dict[str, str], db: Session
) -> None:
    """Test that users cannot read other users' notifications."""
    # Create another user and their notification
    other_user, _ = create_random_user(db)
    notification = Notification(
        user_id=other_user.id,
        type=NotificationType.MENTION,
        message="Private notification",
        reference_id=uuid.uuid4(),
    )
    db.add(notification)
    db.commit()
    db.refresh(notification)

    # Try to read it as normal user
    response = client.get(
        f"{settings.API_V1_STR}/notifications/{notification.id}",
        headers=normal_user_token_headers,
    )
    assert response.status_code == 403
    assert response.json()["detail"] == "Not enough permissions"


def test_update_item_with_new_mention_creates_notification(
    client: TestClient, superuser_token_headers: dict[str, str], db: Session
) -> None:
    """Test that updating an item with new @mention creates a notification."""
    # Create a user to be mentioned
    mentioned_user, _ = create_random_user(db)

    # Create an item first without mentions
    data = {
        "title": "Original Item",
        "description": "No mentions here",
    }
    response = client.post(
        f"{settings.API_V1_STR}/items/",
        headers=superuser_token_headers,
        json=data,
    )
    assert response.status_code == 200
    item = response.json()

    # Update with a mention
    update_data = {
        "description": f"Now mentioning @{mentioned_user.email}",
    }
    response = client.put(
        f"{settings.API_V1_STR}/items/{item['id']}",
        headers=superuser_token_headers,
        json=update_data,
    )
    assert response.status_code == 200

    # Verify notification was created
    db.expire_all()
    statement = select(Notification).where(
        Notification.user_id == mentioned_user.id,
        Notification.reference_id == uuid.UUID(item["id"]),
        Notification.type == NotificationType.MENTION,
    )
    notification = db.exec(statement).first()
    assert notification is not None
    assert "mentioned you" in notification.message
