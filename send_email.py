import os
import smtplib
from email.message import EmailMessage
from pathlib import Path


def load_env(path: str = ".env"):
    """Minimal .env loader: KEY=VALUE lines, # comments ignored."""
    env_file = Path(__file__).parent / path
    if not env_file.exists():
        return
    for line in env_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            key, value = line.split("=", 1)
            os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


def send_email(subject: str, body: str, html: str | None = None):
    load_env()
    # Real env vars win over .env (setdefault), so GitHub Actions secrets just work
    missing = [k for k in ("SMTP_USER", "SMTP_PASSWORD", "EMAIL_TO") if not os.environ.get(k)]
    if missing:
        raise SystemExit(f"Missing in .env: {', '.join(missing)} (see .env.example)")

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = os.environ.get("EMAIL_FROM", os.environ["SMTP_USER"])
    msg["To"] = os.environ["EMAIL_TO"]
    msg.set_content(body)  # text/plain, utf-8
    if html:
        msg.add_alternative(html, subtype="html")  # clients that can show HTML pick this part

    host = os.environ.get("SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("SMTP_PORT", "587"))
    with smtplib.SMTP(host, port, timeout=30) as smtp:
        smtp.starttls()
        smtp.login(os.environ["SMTP_USER"], os.environ["SMTP_PASSWORD"])
        smtp.send_message(msg)
