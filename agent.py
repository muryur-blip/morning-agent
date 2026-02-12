import requests
import smtplib
from email.mime.text import MIMEText

# -----------------------------
# 1) GoldAPI'den Altın & Gümüş Fiyatlarını Çek
# -----------------------------
API_KEY = "YOUR_GOLDAPI_KEY"   # Buraya kendi key'ini yaz

def get_price(metal):
    url = f"https://www.goldapi.io/api/{metal}/USD"
    headers = {
        "x-access-token": API_KEY,
        "Content-Type": "application/json"
    }

    try:
        data = requests.get(url, headers=headers, timeout=10).json()
    except Exception:
        return None

    # Beklenen format:
    # { "price": 1727.75, ... }
    return data.get("price")


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
gold = get_price("XAU")
silver = get_price("XAG")

if gold is None or silver is None:
    body = "API error: GoldAPI fiyatları şu anda alınamadı."
    send_email("Morning Agent – API Error", body)
    print("API error – prices not available")
    exit(0)

body = f"Gold (XAU/USD): {gold}\nSilver (XAG/USD): {silver}"
send_email("Morning Agent – Prices", body)

print("Email sent successfully.")
