import os
import csv
import yfinance as yf
from datetime import datetime, timedelta
from email.mime.text import MIMEText
import smtplib

LOG_FILE = "log.csv"

# --------------------------------------------------
# E-MAIL GÖNDERME
# --------------------------------------------------

def send_email(subject, body):
    sender = os.getenv("EMAIL")
    password = os.getenv("EMAIL_PASSWORD")
    receiver = os.getenv("EMAIL")

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())


# --------------------------------------------------
# LOG OKUMA
# --------------------------------------------------

def read_last_signals(n):
    # log.csv yoksa hata verme → boş liste döndür
    if not os.path.exists(LOG_FILE):
        return []

    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        return rows[-n:]


# --------------------------------------------------
# FİYAT ALMA
# --------------------------------------------------

def get_price(symbol, date):
    data = yf.download(symbol, start=date, end=date + timedelta(days=3))
    if data.empty:
        return None
    return float(data["Close"].iloc[-1])


# --------------------------------------------------
# SİNYAL DEĞERLENDİRME
# --------------------------------------------------

def evaluate_signals(signals):
    results = []

    for s in signals:
        symbol = s["symbol"]
        signal = s["signal"]
        entry = float(s["price"])
        date = datetime.strptime(s["timestamp"], "%Y-%m-%d")

        price_after = get_price(symbol, date)
        if price_after is None:
            continue

        success = (price_after > entry) if signal == "AL" else (price_after < entry)

        results.append({
            "symbol": symbol,
            "signal": signal,
            "entry": entry,
            "after": price_after,
            "success": success
        })

    return results


# --------------------------------------------------
# İSTATİSTİK HESAPLAMA
# --------------------------------------------------

def compute_stats(results):
    al_signals = [r for r in results if r["signal"] == "AL"]
    sat_signals = [r for r in results if r["signal"] == "SAT"]

    al_rate = (sum(r["success"] for r in al_signals) / len(al_signals) * 100) if al_signals else 0
    sat_rate = (sum(r["success"] for r in sat_signals) / len(sat_signals) * 100) if sat_signals else 0

    return al_rate, sat_rate


# --------------------------------------------------
# ANA ÇALIŞMA
# --------------------------------------------------

signals = read_last_signals(30)
results = evaluate_signals(signals)
al_rate, sat_rate = compute_stats(results)

report = []
report.append("PERFORMANS RAPORU - Son 30 Sinyal\n")
report.append(f"AL sinyali başarı oranı: %{al_rate:.2f}")
report.append(f"SAT sinyali başarı oranı: %{sat_rate:.2f}\n")

report.append("Detaylı sonuçlar:\n")
for r in results:
    report.append(
        f"{r['symbol']} | {r['signal']} | Entry: {r['entry']} | "
        f"After: {r['after']} | Başarılı: {r['success']}"
    )

send_email("Performans Raporu", "\n".join(report))

