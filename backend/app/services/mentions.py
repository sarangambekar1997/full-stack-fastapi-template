import re
import uuid

from sqlmodel import Session, select

from app.models import Notification, NotificationType, User


def parse_mentions(text: str | None) -> list[str]:
    """
    Parse @email mentions from text.
    Returns list of email addresses found in @email format.
    """
    if not text:
        return []
    # Match @email format (e.g., @admin@example.com)
    pattern = r"@([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
    matches = re.findall(pattern, text)
    return list(set(matches))  # Remove duplicates


def get_users_by_emails(session: Session, emails: list[str]) -> list[User]:
    """
    Get users by their email addresses.
    """
    if not emails:
        return []
    statement = select(User).where(User.email.in_(emails))  # type: ignore
    return list(session.exec(statement).all())


def create_mention_notifications(
    session: Session,
    text: str | None,
    mentioner: User,
    reference_id: uuid.UUID,
) -> list[Notification]:
    """
    Parse mentions from text and create notifications for mentioned users.
    Returns list of created notifications.
    """
    emails = parse_mentions(text)
    mentioned_users = get_users_by_emails(session, emails)

    notifications = []
    for user in mentioned_users:
        # Don't notify yourself
        if user.id == mentioner.id:
            continue

        notification = Notification(
            user_id=user.id,
            type=NotificationType.MENTION,
            message=f"{mentioner.full_name or mentioner.email} mentioned you",
            reference_id=reference_id,
        )
        session.add(notification)
        notifications.append(notification)

    if notifications:
        session.commit()
        for notification in notifications:
            session.refresh(notification)

    return notifications
