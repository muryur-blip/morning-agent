import requests
import smtplib
from email.mime.text import MIMEText

# -----------------------------
# 1) API RAW verisini çek
# -----------------------------
def get_raw_api():
    url = "https://api.metals.live/v1/spot"

    try:
        data = requests.get(url, timeout=10).json()
        return data
    except Exception as e:
        return {"error": str(e)}


# -----------------------------
# 2) E‑mail Gönder
# -----------------------------
def send_email(subject, body):
    sender = "muryur@gmail.com"
    receiver = "muryur@gmail.com"
    password = "pglttsrxplrbdczs"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())


# -----------------------------
# 3) Ana Çalışma
# -----------------------------
data = get_raw_api()

body = f"API RAW RESPONSE:\n\n{data}"
send_email("Morning Agent – API RAW", body)

print("Raw API response sent.")
