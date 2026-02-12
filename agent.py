import requests
import smtplib
from email.mime.text import MIMEText

# -----------------------------
# 1) Altın & Gümüş Fiyatlarını Çek
# -----------------------------
def get_gold_silver():
    url = "https://metals-api.com/api/latest?access_key=DEMO"
    try:
        data = requests.get(url, timeout=10).json()
    except Exception:
        return None, None

    # Eğer API bozuk veri döndürürse çökmeyi engelle
    if "rates" not in data:
        return None, None

    gold = data["rates"].get("XAU")
    silver = data["rates"].get("XAG")

    return gold, silver


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
gold, silver = get_gold_silver()

# API bozuksa bile workflow fail olmasın
if gold is None or silver is None:
    body = "API error: Altın/Gümüş fiyatları şu anda alınamadı."
    send_email("Morning Agent – API Error", body)
    print("API error – rates not available")
    exit(0)

# Normal durumda fiyatları gönder
body = f"Gold (XAU): {gold}\nSilver (XAG): {silver}"
send_email("Morning Agent – Prices", body)

print("Email sent successfully.")
