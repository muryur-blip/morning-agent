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
# RSI(40) + RSI MA50 + HACİM SİNYALİ
# -----------------------------
def rsi_signal(df):
    # RSI(40)
    period = 40
    delta = df["Close"].diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = -delta.clip(upper=0).rolling(period).mean()
    rs = gain / loss
    rsi40 = 100 - (100 / (1 + rs.iloc[-1]))

    # RSI serisi (MA50 için)
    rsi_series = 100 - (100 / (1 + (gain / loss)))
    rsi_ma50 = rsi_series.rolling(50).mean().iloc[-1]

    # Hacim
    vol = df["Volume"].iloc[-1]
    vol_avg = df["Volume"].rolling(20).mean().iloc[-1]

    # Sinyal mantığı
    if rsi40 < rsi_ma50 and rsi40 < 40 and vol > vol_avg * 1.2:
        return f"ALIM SİNYALİ (RSI40={rsi40:.1f}, MA50={rsi_ma50:.1f}, Hacim yüksek)"
    elif rsi40 > rsi_ma50 and rsi40 > 60 and vol > vol_avg * 1.2:
        return f"SATIŞ SİNYALİ (RSI40={rsi40:.1f}, MA50={rsi_ma50:.1f}, Hacim yüksek)"
    else:
        return f"Sinyal yok (RSI40={rsi40:.1f}, MA50={rsi_ma50:.1f})"

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
    signal = rsi_signal(df)

    report_lines.append(
        f"{symbol}\n"
        f"  • Fiyat: {price:.2f}\n"
        f"  • Günlük değişim: {change:.2f}%\n"
        f"  • RSI(14): {rsi_val:.1f}\n"
        f"  • Trend: {tr}\n"
        f"  • Sinyal: {signal}\n"
    )

final_report = "\n".join(report_lines)

# -----------------------------
# E‑MAIL GÖNDER
# -----------------------------
send_email("Morning Agent – Çoklu Varlık Analizi + Sinyaller", final_report)

