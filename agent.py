import requests
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import csv
import os

# -----------------------------
# GOLDAPI – METAL FİYATLARI
# -----------------------------
GOLDAPI_KEY = "BURAYA_KENDİ_KEYİNİ_YAZ"

def get_metal_price(metal):
    url = f"https://www.goldapi.io/api/{metal}/USD"
    headers = {"x-access-token": GOLDAPI_KEY}
    r = requests.get(url, headers=headers)
    data = r.json()
    return data.get("price", None)

# -----------------------------
# E‑MAIL GÖNDERME
# -----------------------------
def send_email(subject, body):
    sender = "YOUR_EMAIL"
    password = "YOUR_APP_PASSWORD"
    receiver = "YOUR_EMAIL"

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())

# -----------------------------
# YAHOO FINANCE – TEKNİK ANALİZ
# -----------------------------
assets = ["SQQQ", "EWZ", "AEP", "PPTA", "AMZN", "FRO", "CGNX", "BNTX"]

def get_data(symbol):
    ticker = yf.Ticker(symbol)
    df = ticker.history(period="200d")
    return df

def daily_change(df):
    return (df["Close"].iloc[-1] - df["Close"].iloc[-2]) / df["Close"].iloc[-2] * 100

def rsi(df, period=14):
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs.iloc[-1]))

def trend(df):
    ma50 = df["Close"].rolling(50).mean().iloc[-1]
    ma200 = df["Close"].rolling(200).mean().iloc[-1]
    return "Pozitif trend" if ma50 > ma200 else "Zayıf trend"

# -----------------------------
# RSI(40) + RSI MA50 + HACİM SİNYALİ
# -----------------------------
def rsi_signal(df):
    period = 40
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    rsi40 = 100 - (100 / (1 + rs.iloc[-1]))

    rsi_series = 100 - (100 / (1 + (gain / loss)))
    rsi_ma50 = rsi_series.rolling(50).mean().iloc[-1]

    vol = df["Volume"].iloc[-1]
    vol_avg = df["Volume"].rolling(20).mean().iloc[-1]

    if rsi40 < rsi_ma50 and rsi40 < 40 and vol > vol_avg * 1.2:
        return "AL", rsi40, rsi_ma50, vol, vol_avg
    elif rsi40 > rsi_ma50 and rsi40 > 60 and vol > vol_avg * 1.2:
        return "SAT", rsi40, rsi_ma50, vol, vol_avg
    else:
        return "YOK", rsi40, rsi_ma50, vol, vol_avg

# -----------------------------
# LOGGING KATMANI (FAZ 1)
# -----------------------------
LOG_FILE = "log.csv"

def write_log(row):
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "tarih", "varlik", "fiyat", "rsi14",
                "rsi40", "rsi_ma50", "hacim", "hacim_ort",
                "sinyal"
            ])
        writer.writerow(row)

# -----------------------------
# RAPOR OLUŞTURMA
# -----------------------------
report_lines = []

gold = get_metal_price("XAU")
silver = get_metal_price("XAG")

report_lines.append("METAL FİYATLARI")
report_lines.append(f"  • Altın: {gold}")
report_lines.append(f"  • Gümüş: {silver}\n")

report_lines.append("VARLIK ANALİZİ")

today = datetime.now().strftime("%Y-%m-%d")

for symbol in assets:
    df = get_data(symbol)
    price = df["Close"].iloc[-1]
    change = daily_change(df)
    rsi14 = rsi(df)
    tr = trend(df)

    sinyal, r40, r40ma, vol, volavg = rsi_signal(df)

    report_lines.append(
        f"{symbol}\n"
        f"  • Fiyat: {price:.2f}\n"
        f"  • Günlük değişim: {change:.2f}%\n"
        f"  • RSI(14): {rsi14:.1f}\n"
        f"  • Trend: {tr}\n"
        f"  • Sinyal: {sinyal} (RSI40={r40:.1f}, MA50={r40ma:.1f})\n"
    )

    # LOG SATIRI
    write_log([
        today, symbol, price, round(rsi14, 2),
        round(r40, 2), round(r40ma, 2),
        int(vol), int(volavg),
        sinyal
    ])

final_report = "\n".join(report_lines)

# -----------------------------
# E‑MAIL GÖNDER
# -----------------------------
send_email("Morning Agent – Analiz + Sinyaller + Log", final_report)


