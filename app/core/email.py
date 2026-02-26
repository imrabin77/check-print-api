import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.core.config import get_settings


def _send_email(to_email: str, subject: str, html_body: str):
    """Send an email via Gmail SMTP."""
    settings = get_settings()
    if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
        raise RuntimeError("SMTP not configured. Set SMTP_USER and SMTP_PASSWORD in .env")

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_USER}>"
    msg["To"] = to_email
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
        server.starttls()
        server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
        server.sendmail(settings.SMTP_USER, to_email, msg.as_string())


def send_verification_email(to_email: str, code: str):
    """Send a 6-digit verification code."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 30px;">
        <h2 style="color: #1e293b;">Verify your email</h2>
        <p style="color: #475569; font-size: 15px;">Enter this code on the verification screen to complete your signup:</p>
        <div style="background: #f1f5f9; border-radius: 8px; padding: 20px; text-align: center; margin: 24px 0;">
            <span style="font-size: 32px; font-weight: 700; letter-spacing: 8px; color: #0f172a;">{code}</span>
        </div>
        <p style="color: #94a3b8; font-size: 13px;">This code expires in 10 minutes. If you didn't request this, ignore this email.</p>
    </div>
    """
    _send_email(to_email, f"CheckPrint – Your verification code is {code}", html)


def send_admin_new_user_notification(admin_emails: list[str], new_user_name: str, new_user_email: str):
    """Notify all admins that a new user signed up and needs approval."""
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 480px; margin: 0 auto; padding: 30px;">
        <h2 style="color: #1e293b;">New User Awaiting Approval</h2>
        <p style="color: #475569; font-size: 15px;">A new user has registered and verified their email. They need your approval to access CheckPrint.</p>
        <div style="background: #f1f5f9; border-radius: 8px; padding: 16px; margin: 20px 0;">
            <p style="margin: 4px 0; color: #1e293b;"><strong>Name:</strong> {new_user_name}</p>
            <p style="margin: 4px 0; color: #1e293b;"><strong>Email:</strong> {new_user_email}</p>
        </div>
        <p style="color: #475569; font-size: 15px;">Log in to the <strong>Users</strong> panel to activate their account.</p>
    </div>
    """
    for email in admin_emails:
        try:
            _send_email(email, f"CheckPrint – New user {new_user_name} needs approval", html)
        except Exception as e:
            print(f"Failed to notify admin {email}: {e}")
