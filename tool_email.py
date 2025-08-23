import os
import smtplib
import ssl
from email.mime.text import MIMEText

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject

    # Configurable sender and SMTP via environment variables
    email_from = os.getenv("EMAIL_FROM", "no-reply@example.com")
    smtp_host = os.getenv("SMTP_HOST", "localhost")
    smtp_port = int(os.getenv("SMTP_PORT", "25"))
    smtp_username = os.getenv("SMTP_USERNAME")
    smtp_password = os.getenv("SMTP_PASSWORD")
    smtp_security = os.getenv("SMTP_SECURITY", "none").lower()  # one of: none, starttls, ssl
    email_enabled = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

    msg["From"] = email_from
    msg["To"] = to

    # In development, default to mocked sending unless explicitly enabled
    if not email_enabled:
        return {"status": "mocked", "to": to, "from": email_from}

    try:
        if smtp_security == "ssl":
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context) as server:
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
        else:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                if smtp_security == "starttls":
                    context = ssl.create_default_context()
                    server.starttls(context=context)
                if smtp_username and smtp_password:
                    server.login(smtp_username, smtp_password)
                server.send_message(msg)
        return {"status": "sent", "to": to, "from": email_from}
    except Exception as exc:
        return {
            "status": "error",
            "to": to,
            "from": email_from,
            "error": str(exc),
            "host": smtp_host,
            "port": smtp_port,
            "security": smtp_security,
        }
