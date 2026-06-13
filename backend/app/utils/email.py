"""
Email utility — mock implementation for local development.

Prints verification and password-reset links to the console
instead of sending real emails.  This lets you test the full
auth flow without needing a SendGrid account or SMTP server.

# TODO: Replace with real email sending (SendGrid or SMTP)
#       before deploying to production.  The function signatures
#       are intentionally kept stable so the swap is a drop-in
#       replacement — only the body of each function changes.
"""

from app.config import get_settings

settings = get_settings()


def send_verification_email(email: str, token: str) -> None:
    """
    Print an email-verification link to the console.

    In production this would send an HTML email via SendGrid
    containing a clickable button / link.
    """
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    print("\n" + "=" * 60)
    print("📧  VERIFICATION EMAIL (mock)")
    print(f"   To:   {email}")
    print(f"   Link: {link}")
    print("=" * 60 + "\n")


def send_password_reset_email(email: str, token: str) -> None:
    """
    Print a password-reset link to the console.

    In production this would send an HTML email via SendGrid
    containing a clickable button / link.
    """
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    print("\n" + "=" * 60)
    print("🔑  PASSWORD RESET EMAIL (mock)")
    print(f"   To:   {email}")
    print(f"   Link: {link}")
    print("=" * 60 + "\n")
