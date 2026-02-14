import csv
import yfinance as yf
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText

LOG_FILE = "log.csv"

# -----------------------------
# E‑MAIL GÖNDERME
# -----------------------------
def send_email(subject, body):
    sender = "muryur@gmail.com"
    password = "pglttsrxplrbdczs"
    receiver = "muryur@gmail.com"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

# -----------------------------
# LOG DOSYASINI OKU
# -----------------------------
def read_last_signals(n=30):
    rows = []
    with open(LOG_FILE, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)
    return rows[-n:] if len(rows) >= n else rows

# -----------------------------
# FİYAT GETİR
# -----------------------------
def get_price(symbol, date):
    ticker = yf.Ticker(symbol)
    df = ticker.history(start=date, end=date + timedelta(days=7))
    if len(df) == 0:
        return None
    return df["Close"].iloc[0]

# -----------------------------
# PERFORMANS HESAPLA
# -----------------------------
def evaluate_signals(signals):
    results = []
    for s in signals:
        symbol = s["varlik"]
        signal_type = s["sinyal"]
        entry_date = datetime.strptime(s["tarih"], "%Y-%m-%d")
        entry_price = float(s["fiyat"])

        # 1, 3, 5 gün sonrası fiyatlar
        p1 = get_price(symbol, entry_date + timedelta(days=1))
        p3 = get_price(symbol, entry_date + timedelta(days=3))
        p5 = get_price(symbol, entry_date + timedelta(days=5))

        results.append({
            "symbol": symbol,
            "signal": signal_type,
            "entry": entry_price,
            "p1": p1,
            "p3": p3,
            "p5": p5
        })

    return results

# -----------------------------
# BAŞARI ORANI HESAPLA
# -----------------------------
def compute_stats(results):
    al_hits = 0
    al_total = 0
    sat_hits = 0
    sat_total = 0

    for r in results:
        if r["signal"] == "AL":
            al_total += 1
            if r["p3"] and r["p3"] > r["entry"]:
                al_hits += 1

        if r["signal"] == "SAT":
            sat_total += 1
            if r["p3"] and r["p3"] < r["entry"]:
                sat_hits += 1

    al_rate = (al_hits / al_total * 100) if al_total > 0 else 0
    sat_rate = (sat_hits / sat_total * 100) if sat_total > 0 else 0

    return al_rate, sat_rate

# -----------------------------
# ANA ÇALIŞMA
# -----------------------------
signals = read_last_signals(30)
results = evaluate_signals(signals)
al_rate, sat_rate = compute_stats(results)

report = []
report.append("PERFORMANS RAPORU – Son 30 Sinyal\n")
report.append(f"AL sinyali başarı oranı: %{al_rate:.2f}")
report.append(f"SAT sinyali başarı oranı: %{sat_rate:.2f}\n")

report.append("Detaylı sonuçlar:\n")
for r in results:
    report.append(
        f"{r['symbol']} | {r['signal']} | Entry: {r['entry']} | "
        f"P1: {r['p1']} | P3: {r['p3']} | P5: {r['p5']}"
    )

final_report = "\n".join(report)

send_email("Performance Agent – Son 30 Sinyal Analizi", final_report)
