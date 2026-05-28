import streamlit as st
import yfinance as yf

st.title("זירת מסחר")

symbol = st.text_input("הכנס סימול מניה", "AAPL")

if st.button("בדיקה"):
    stock = yf.Ticker(symbol)
    data = stock.history(period="1d")

    if not data.empty:
        st.write("מחיר אחרון:", data["Close"].iloc[-1])
    else:
        st.write("אין נתונים")
