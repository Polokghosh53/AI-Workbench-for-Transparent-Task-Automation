import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "noreply@aiworkbench.com"
    msg["To"] = to
    try:
        with smtplib.SMTP("localhost") as server:
            server.send_message(msg)
        return {"status": "sent", "to": to}
    except Exception as exc:
        # Dev-safe fallback when no local SMTP is available
        return {"status": "mocked", "to": to, "error": str(exc)}
