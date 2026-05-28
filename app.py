import streamlit as st
import yfinance as yf
import smtplib
import time
from email.mime.text import MIMEText
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Smart Stock Dashboard", layout="wide")

GMAIL_USER = "YOUR_GMAIL@gmail.com"
GMAIL_PASS = "YOUR_APP_PASSWORD"
ALERT_EMAIL = "TARGET_EMAIL@gmail.com"

# -------------------------
# STYLE (modern dark UI)
# -------------------------
st.markdown("""
<style>
body {
    background-color: #0b1220;
    color: #e6edf3;
}

.block-container {
    padding-top: 2rem;
}

.card {
    background: #111a2e;
    border: 1px solid #22304a;
    padding: 14px;
    border-radius: 14px;
    margin-bottom: 12px;
}

.title {
    font-size: 28px;
    font-weight: 700;
    color: #7dd3fc;
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# STATE
# -------------------------
if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "TSLA": {"target": 250, "percent": 2},
        "AAPL": {"target": 180, "percent": 2}
    }

if "last_price" not in st.session_state:
    st.session_state.last_price = {}

# -------------------------
# DATA
# -------------------------
def get_price(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1d", progress=False)
        if df is None or df.empty:
            return None
        return float(df["Close"].iloc[-1])
    except:
        return None

# -------------------------
# EMAIL
# -------------------------
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

# -------------------------
# ALERT ENGINE
# -------------------------
def check_alerts():
    for s, cfg in st.session_state.stocks.items():

        price = get_price(s)
        if price is None:
            continue

        last = st.session_state.last_price.get(s, price)
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
                f"Stock Alert {s}",
                f"""
Symbol: {s}
Price: {price}
Change: {change:.2f}%
Time: {datetime.now()}
Reason: {reason}
"""
            )

        st.session_state.last_price[s] = price

# -------------------------
# HEADER
# -------------------------
st.markdown("<div class='title'>📊 Smart Stock Dashboard</div>", unsafe_allow_html=True)

# -------------------------
# SIDEBAR (manage stocks)
# -------------------------
st.sidebar.header("➕ Add Stock")

symbol = st.sidebar.text_input("Symbol")
target = st.sidebar.number_input("Target Price", value=0.0)
percent = st.sidebar.number_input("Alert %", value=2.0)

if st.sidebar.button("Add / Update"):
    if symbol:
        st.session_state.stocks[symbol.upper()] = {
            "target": target,
            "percent": percent
        }

if st.sidebar.button("Check Now"):
    check_alerts()
    st.sidebar.success("Checked")

# -------------------------
# AUTO REFRESH OPTION
# -------------------------
refresh = st.sidebar.checkbox("Auto refresh (60s)")

if refresh:
    time.sleep(60)
    st.rerun()

# -------------------------
# MAIN UI
# -------------------------
for s, cfg in st.session_state.stocks.items():

    price = get_price(s)

    st.markdown(f"<div class='card'><h3>{s}</h3>", unsafe_allow_html=True)

    if price is None:
        st.error("No data")
        st.markdown("</div>", unsafe_allow_html=True)
        continue

    st.metric("Price", f"{price:.2f}")

    st.write("Target:", cfg["target"])
    st.write("Alert %:", cfg["percent"])

    df = yf.download(s, period="1mo", interval="1d", progress=False)
    if df is not None and not df.empty:
        st.line_chart(df["Close"])

    st.markdown("</div>", unsafe_allow_html=True)
