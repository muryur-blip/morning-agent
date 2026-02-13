import requests
import yfinance as yf
import smtplib
from email.mime.text import MIMEText

# -----------------------------
# GOLDAPI – METAL FİYATLARI
# -----------------------------
GOLDAPI_KEY = "goldapi-d1e919mljv85vj-io"

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
# RAPOR OLUŞTURMA
# -----------------------------
report_lines = []

# Metal fiyatları
gold = get_metal_price("XAU")
silver = get_metal_price("XAG")

report_lines.append("METAL FİYATLARI")
report_lines.append(f"  • Altın: {gold}")
report_lines.append(f"  • Gümüş: {silver}\n")

# Teknik analiz
report_lines.append("VARLIK ANALİZİ")

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

# -----------------------------
# E‑MAIL GÖNDER
# -----------------------------
send_email("Morning Agent – Çoklu Varlık Analizi", final_report)
