import time
import requests
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

ALPHA_KEY = "YOUR_ALPHA_VANTAGE_KEY"

GMAIL_USER = "YOUR_GMAIL@gmail.com"
GMAIL_PASS = "YOUR_APP_PASSWORD"
ALERT_EMAIL = "TARGET_EMAIL@gmail.com"

# מניות קבועות (ל-MVP)
STOCKS = {
    "TSLA": {"target": 250, "percent": 2},
    "AAPL": {"target": 180, "percent": 2}
}

last_price = {}

def get_price(symbol):
    try:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_KEY}"
        r = requests.get(url)
        data = r.json()
        price = data.get("Global Quote", {}).get("05. price")
        return float(price) if price else None
    except:
        return None


def send_email(subject, body):
    try:
        msg = MIMEText(body)
        msg["Subject"] = subject
        msg["From"] = GMAIL_USER
        msg["To"] = ALERT_EMAIL

        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, ALERT_EMAIL, msg.as_string())
        server.quit()
    except:
        pass


def check():
    for symbol, cfg in STOCKS.items():

        price = get_price(symbol)
        if price is None:
            continue

        last = last_price.get(symbol, price)
        change = ((price - last) / last) * 100 if last else 0

        trigger = False
        reason = ""

        if price >= cfg["target"]:
            trigger = True
            reason = "Target reached"

        if abs(change) >= cfg["percent"]:
            trigger = True
            reason = f"Move {change:.2f}%"

        if trigger:
            send_email(
                f"Stock Alert {symbol}",
                f"{symbol}\nPrice: {price}\nChange: {change:.2f}%\nTime: {datetime.now()}\n{reason}"
            )

        last_price[symbol] = price


# -------------------------
# LOOP (AUTOMATION)
# -------------------------
while True:
    print("Checking stocks...")
    check()
    time.sleep(180)  # כל 3 דקות
