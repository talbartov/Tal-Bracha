import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

# -------------------------
# עיצוב
# -------------------------
st.set_page_config(page_title="זירת מסחר", layout="wide")

st.markdown("""
<style>
body {
    background-color: #f5f7fb;
}
.card {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border: 1px solid #e6e6e6;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

st.title("📊 זירת המסחר")

# -------------------------
# מצב
# -------------------------
if "stocks" not in st.session_state:
    st.session_state.stocks = ["NSTR.TA"]  # נורסטאר כברירת מחדל

# -------------------------
# פונקציה
# -------------------------
@st.cache_data(ttl=60)
def get_data(symbol):
    stock = yf.Ticker(symbol)
    hist = stock.history(period="1d", interval="5m")
    return hist, stock

def add_stock(symbol):
    if symbol and symbol not in st.session_state.stocks:
        if len(st.session_state.stocks) < 40:
            st.session_state.stocks.append(symbol)

def remove_stock(symbol):
    st.session_state.stocks.remove(symbol)

# -------------------------
# חיפוש
# -------------------------
st.subheader("הוספת מניה")

symbol_input = st.text_input("הקלד סימבול (למשל AAPL / NVDA / POLI.TA)")

if st.button("הוסף מניה"):
    add_stock(symbol_input.upper())

# -------------------------
# רענון אוטומטי (UI בלבד)
# -------------------------
st.caption(f"עודכן: {datetime.now().strftime('%H:%M:%S')}")

# -------------------------
# דשבורד
# -------------------------
for symbol in st.session_state.stocks:
    try:
        hist, stock = get_data(symbol)

        if hist.empty:
            continue

        last_price = hist["Close"].iloc[-1]
        prev_price = hist["Close"].iloc[-2] if len(hist) > 1 else last_price
        change = ((last_price - prev_price) / prev_price) * 100

        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            st.markdown(f"### {symbol}")

        with col2:
            st.metric("מחיר", f"{last_price:.2f}", f"{change:.2f}%")

        with col3:
            if st.button(f"הסר {symbol}"):
                remove_stock(symbol)
                st.rerun()

        st.line_chart(hist["Close"])

        st.markdown("---")

    except Exception as e:
        st.warning(f"שגיאה ב-{symbol}")
