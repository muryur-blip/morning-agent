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
