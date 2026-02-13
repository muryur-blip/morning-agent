import requests
import smtplib
import yfinance as yf
from email.mime.text import MIMEText

API_KEY = "goldapi-d1e919mljv85vj-io"
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

    return data.get("price")

report_lines = []

for symbol in assets:
    df = get_data(symbol)
    price = df["Close"].iloc[-1]
    change = daily_change(df)
    rsi_val = rsi(df)
    tr = trend(df)

    report_lines.append(
        f"{symbol}\n"
        f"  • Fiyat: {price:.2f}\n"
        f"  • Günlük değişim: {change:.2f}%\n"
        f"  • RSI: {rsi_val:.1f}\n"
        f"  • Trend: {tr}\n"
    )

final_report = "\n".join(report_lines)

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
