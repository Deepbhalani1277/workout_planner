"""
Email utility — sends transactional emails via SendGrid.

Used for welcome emails, password resets, plan delivery, etc.
"""

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

from app.config import get_settings

settings = get_settings()


def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send a single transactional email.

    Returns True on success, False on failure.
    """
    message = Mail(
        from_email="noreply@workoutplanner.app",
        to_emails=to_email,
        subject=subject,
        html_content=html_content,
    )
    try:
        sg = SendGridAPIClient(settings.SENDGRID_API_KEY)
        sg.send(message)
        return True
    except Exception:
        return False
