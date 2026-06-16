import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger
from core.config import settings

def send_sms_alert(to_phone: str, message: str) -> bool:
    """Send SMS alert via Twilio."""
    try:
        from twilio.rest import Client
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_PHONE_NUMBER,
            to=to_phone
        )
        logger.info(f"SMS sent to {to_phone}")
        return True
    except Exception as e:
        logger.error(f"SMS failed: {e}")
        return False

def send_email_alert(to_email: str, subject: str, body: str) -> bool:
    """Send email alert via SMTP."""
    try:
        msg = MIMEMultipart()
        msg["From"] = settings.SMTP_USER
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASSWORD)
            server.send_message(msg)

        logger.info(f"Email sent to {to_email}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False

def build_bin_full_email(bin_code: str, location: str, fill_level: float) -> str:
    return f"""
    <html><body>
    <h2 style="color:red;">⚠️ Dustbin Alert</h2>
    <p>Bin <strong>{bin_code}</strong> at <strong>{location}</strong> 
    is <strong>{fill_level}% full</strong> and requires immediate collection.</p>
    <p>Please schedule a collection as soon as possible.</p>
    <br/><p>— Smart Dustbin System</p>
    </body></html>
    """
