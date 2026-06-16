"""
Email utility — Gmail SMTP implementation.

Sends real HTML verification and password-reset links via SMTP.
Configured to use a Google App Password for authentication.
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from fastapi import HTTPException, status
from app.config import get_settings

settings = get_settings()


def _send_email(to_email: str, subject: str, html_content: str) -> None:
    """
    Core function to connect to Gmail SMTP server and send an email.
    """
    smtp_email = settings.SMTP_EMAIL
    smtp_password = settings.SMTP_PASSWORD

    if not smtp_email or not smtp_password:
        print("[WARNING] SMTP credentials not set! Check your .env file.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email service is not configured. Please try again later."
        )

    # Create the email message
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"FitPlan <{smtp_email}>"
    msg["To"] = to_email

    # Attach HTML content
    part = MIMEText(html_content, "html")
    msg.attach(part)

    try:
        # Connect to Gmail SMTP server using TLS port 587
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.ehlo()

        # Login and send
        server.login(smtp_email, smtp_password)
        server.sendmail(smtp_email, to_email, msg.as_string())
        server.quit()
        print(f"[SUCCESS] Email successfully sent to {to_email}")

    except smtplib.SMTPAuthenticationError:
        print("[ERROR] SMTP Authentication failed! Ensure you are using a 16-letter App Password.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Email service authentication failed. Administrator has been notified."
        )
    except Exception as e:
        print(f"[ERROR] Failed to send email: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email. Please try again later."
        )


def send_verification_email(email: str, token: str) -> None:
    """
    Send an HTML email containing the verification link.
    """
    link = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    
    subject = "Verify your email - FitPlan"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4F46E5;">Welcome to FitPlan! 🏋️‍♀️🥗</h2>
        <p>Hi there,</p>
        <p>Thank you for signing up for FitPlan! We are excited to help you achieve your fitness goals.</p>
        <p>To get started, please verify your email address by clicking the button below:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Verify Email
            </a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666; font-size: 14px;">{link}</p>
        <p>If you did not create an account, you can safely ignore this email.</p>
        <br/>
        <p>Best regards,</p>
        <p><strong>The FitPlan Team</strong></p>
      </body>
    </html>
    """

    _send_email(email, subject, html_content)


def send_password_reset_email(email: str, token: str) -> None:
    """
    Send an HTML email containing the password reset link.
    """
    link = f"{settings.FRONTEND_URL}/reset-password?token={token}"
    
    subject = "Password Reset Request - FitPlan"
    
    html_content = f"""
    <html>
      <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; max-width: 600px; margin: 0 auto; padding: 20px;">
        <h2 style="color: #4F46E5;">Password Reset Request 🔐</h2>
        <p>Hi there,</p>
        <p>We received a request to reset your password for your FitPlan account.</p>
        <p>Click the button below to set a new password:</p>
        <div style="text-align: center; margin: 30px 0;">
            <a href="{link}" style="background-color: #4F46E5; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                Reset Password
            </a>
        </div>
        <p>Or copy and paste this link into your browser:</p>
        <p style="word-break: break-all; color: #666; font-size: 14px;">{link}</p>
        <p>If you did not request a password reset, you can safely ignore this email.</p>
        <br/>
        <p>Best regards,</p>
        <p><strong>The FitPlan Team</strong></p>
      </body>
    </html>
    """

    _send_email(email, subject, html_content)
