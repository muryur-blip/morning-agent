import requests
import smtplib
from email.mime.text import MIMEText

# -----------------------------
# 1) Altın & Gümüş Fiyatlarını Çek (Metals.live – format otomatik algılama)
# -----------------------------
def get_gold_silver():
    url = "https://api.metals.live/v1/spot"

    try:
        data = requests.get(url, timeout=10).json()
    except Exception:
        return None, None

    # API bazen şöyle döner:
    # [{"gold": 2025.34}, {"silver": 23.45}]
    if isinstance(data, list):
        gold = None
        silver = None

        for item in data:
            if isinstance(item, dict):
                if "gold" in item:
                    gold = item["gold"]
                if "silver" in item:
                    silver = item["silver"]

        return gold, silver

    return None, None


# -----------------------------
# 2) E‑mail Gönder
# -----------------------------
def send_email(subject, body):
    sender = "YOUR_GMAIL@gmail.com"
    receiver = "YOUR_GMAIL@gmail.com"
    password = "YOUR_APP_PASSWORD"

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
gold, silver = get_gold_silver()

if gold is None or silver is None:
    body = "API error: Altın/Gümüş fiyatları şu anda alınamadı."
    send_email("Morning Agent – API Error", body)
    print("API error – rates not available")
    exit(0)

body = f"Gold (XAU): {gold}\nSilver (XAG): {silver}"
send_email("Morning Agent – Prices", body)

print("Email sent successfully.")
