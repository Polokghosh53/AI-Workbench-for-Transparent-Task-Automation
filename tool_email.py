import smtplib
from email.mime.text import MIMEText

def send_email(to, subject, body):
    # Use a test SMTP server or integrate with Sendgrid/Mailgun for hackathon
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = "noreply@aiworkbench.com"
    msg["To"] = to
    with smtplib.SMTP("localhost") as server:
        server.send_message(msg)
    return {"status": "sent", "to": to}
