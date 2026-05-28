import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stock Dashboard", layout="wide")

st.title("📊 Stock Dashboard")

# קלט משתמש
ticker = st.text_input("Enter stock symbol (e.g. AAPL, TSLA, NVDA)", "AAPL")

period = st.selectbox(
    "Select time range",
    ["1mo", "3mo", "6mo", "1y", "5y", "max"]
)

if ticker:
    try:
        stock = yf.Ticker(ticker)

        hist = stock.history(period=period)

        if hist.empty:
            st.warning("No data found for this ticker")
        else:
            st.subheader(f"{ticker} Price Chart")

            st.line_chart(hist["Close"])

            st.subheader("Latest Data")
            st.dataframe(hist.tail())

            info = stock.info

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Current Price", info.get("currentPrice", "N/A"))

            with col2:
                st.metric("Market Cap", info.get("marketCap", "N/A"))

            with col3:
                st.metric("P/E Ratio", info.get("trailingPE", "N/A"))

    except Exception as e:
        st.error(f"Error loading data: {e}")
