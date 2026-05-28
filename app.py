import streamlit as st
import yfinance as yf
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# -------------------------
# PAGE CONFIG
# -------------------------
st.set_page_config(page_title="Smart Stock Dashboard", layout="wide")

# -------------------------
# THEME (TradingView-light feel)
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
    padding: 16px;
    border-radius: 14px;
    margin-bottom: 12px;
}

.title {
    font-size: 28px;
    font-weight: 700;
    color: #7dd3fc;
}

.subtitle {
    color: #94a3b8;
    margin-bottom: 20px;
}

.metric {
    font-size: 18px;
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

# -------------------------
# EMAIL CONFIG
# -------------------------
GMAIL_USER = "YOUR_GMAIL@gmail.com"
GMAIL_PASS = "YOUR_APP_PASSWORD"
ALERT_EMAIL = "TARGET_EMAIL@gmail.com"

# -------------------------
# STATE
# -------------------------
if "stocks" not in st.session_state:
    st.session_state.stocks = {
        "TSLA": {"target": 250, "percent": 3},
        "AAPL": {"target": 180, "percent": 2}
    }

if "last_price" not in st.session_state:
    st.session_state.last_price = {}

# -------------------------
# DATA
# -------------------------
def get_data(symbol):
    try:
        df = yf.download(symbol, period="5d", interval="1d", progress=False, threads=False)
        if df is None or df.empty:
            return None
        return df
    except:
        return None

def get_price(symbol):
    df = get_data(symbol)
    if df is None:
        return None
    return float(df["Close"].iloc[-1])

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
            reason = "Target price reached"

        if abs(change) >= cfg["percent"]:
            trigger = True
            reason = f"Move {change:.2f}%"

        if trigger:
            send_email(
                f"Stock Alert {s}",
                f"{s}\nPrice: {price}\nChange: {change:.2f}%\nTime: {datetime.now()}\n{reason}"
            )

        st.session_state.last_price[s] = price

# -------------------------
# HEADER
# -------------------------
st.markdown("<div class='title'>📊 Smart Stock Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Light TradingView-style monitoring system</div>", unsafe_allow_html=True)

# -------------------------
# TABS
# -------------------------
tab1, tab2, tab3 = st.tabs(["Overview", "Alerts", "Manage"])

# -------------------------
# OVERVIEW
# -------------------------
with tab1:

    colA, colB = st.columns([2, 1])

    with colA:
        st.subheader("Live Stocks")

        for s in st.session_state.stocks.keys():

            price = get_price(s)

            st.markdown(f"<div class='card'><h3>{s}</h3>", unsafe_allow_html=True)

            if price is None:
                st.write("No data")
                st.markdown("</div>", unsafe_allow_html=True)
                continue

            st.metric("Price", f"{price:.2f}")

            df = get_data(s)
            if df is not None:
                st.line_chart(df["Close"])

            st.markdown("</div>", unsafe_allow_html=True)

    with colB:
        st.subheader("Control")

        if st.button("Run Check Now"):
            check_alerts()
            st.success("Checked")

# -------------------------
# ALERTS
# -------------------------
with tab2:
    st.subheader("Alert Rules")

    for s, cfg in st.session_state.stocks.items():
        st.markdown(f"""
        <div class="card">
        <b>{s}</b><br>
        Target: {cfg['target']}<br>
        Percent: {cfg['percent']}%
        </div>
        """, unsafe_allow_html=True)

# -------------------------
# MANAGE
# -------------------------
with tab3:

    st.subheader("Add Stock")

    sym = st.text_input("Symbol")
    target = st.number_input("Target Price", value=0.0)
    percent = st.number_input("Alert %", value=2.0)

    if st.button("Add"):
        st.session_state.stocks[sym.upper()] = {
            "target": target,
            "percent": percent
        }
        st.success("Added")

# -------------------------
# REFRESH CONTROL
# -------------------------
st.caption("Refresh page (F5) for updates")
