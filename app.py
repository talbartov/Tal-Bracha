
import streamlit as st
import yfinance as yf
from datetime import datetime

# -------------------------
# CONFIG
# -------------------------
st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.markdown("""
<style>
.stock-card {
    background: #ffffff;
    border-radius: 14px;
    padding: 12px;
    margin-bottom: 12px;
    border: 1px solid #e6eaf2;
    box-shadow: 0 2px 6px rgba(0,0,0,0.05);
}
</style>
""", unsafe_allow_html=True)

# -------------------------
# STATE
# -------------------------
if "stocks" not in st.session_state:
    st.session_state.stocks = ["TSLA"]

# -------------------------
# בסיס mapping שם -> סימבול
# (בהמשך נחבר API אמיתי)
# -------------------------
NAME_TO_SYMBOL = {
    "tesla": "TSLA",
    "apple": "AAPL",
    "nvidia": "NVDA",
    "microsoft": "MSFT",
    "nortstar": "NSTR.TA",
    "norstar": "NSTR.TA",
}

# -------------------------
# CACHE (קריטי)
# -------------------------
@st.cache_data(ttl=60)
def get_data(symbol):
    try:
        df = yf.Ticker(symbol).history(period="1d", interval="5m")
        if df is None or df.empty:
            return None
        return df
    except:
        return None

# -------------------------
# נרמול קלט
# -------------------------
def resolve_symbol(user_text):
    if not user_text:
        return None

    text = user_text.lower().strip()

    # אם המשתמש כתב שם ולא סימבול
    if text in NAME_TO_SYMBOL:
        return NAME_TO_SYMBOL[text]

    # אחרת נניח שזה סימבול ישיר
    return user_text.upper()

# -------------------------
# SIDEBAR
# -------------------------
st.sidebar.title("ניהול מניות")

user_input = st.sidebar.text_input("הוסף מניה (שם או סימבול)")

if st.sidebar.button("הוסף"):
    symbol = resolve_symbol(user_input)

    if symbol and symbol not in st.session_state.stocks:
        st.session_state.stocks.append(symbol)

remove = st.sidebar.selectbox("הסר מניה", st.session_state.stocks)

if st.sidebar.button("הסר"):
    st.session_state.stocks.remove(remove)

if st.sidebar.button("איפוס"):
    st.session_state.stocks = ["TSLA"]

st.sidebar.write("עודכן:", datetime.now().strftime("%H:%M:%S"))

# -------------------------
# MAIN UI
# -------------------------
st.title("📊 Stock Dashboard")

for symbol in st.session_state.stocks:

    df = get_data(symbol)

    st.markdown(f"<div class='stock-card'><h3>{symbol}</h3></div>", unsafe_allow_html=True)

    if df is None:
        st.error(f"לא נמצאו נתונים עבור {symbol}")
        continue

    col1, col2 = st.columns([3, 1])

    with col1:
        st.line_chart(df["Close"])

    with col2:
        last = df["Close"].iloc[-1]
        st.metric("מחיר אחרון", f"{last:.2f}")
