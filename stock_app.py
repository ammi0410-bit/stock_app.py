import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 介面與 CSS 美化 ---
st.set_page_config(page_title="私人家族辦公室 | 決策終端", layout="wide")

st.markdown("""
    <style>
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    div[data-testid="stExpander"] { border: 1px solid #30363d; border-radius: 10px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 安全閘口 ---
st.sidebar.title("🔐 身分驗證")
pwd = st.sidebar.text_input("輸入解鎖密碼", type="password")
if pwd != "13579":
    st.info("請輸入密碼以啟動專業分析儀表板。")
    st.stop()

# --- 3. 初始化持倉數據 (修正了報錯的語法) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"代號": "06082.HK", "成本": 38.20, "數量": 200.0},
        {"代號": "03888.HK", "成本": 32.00, "數量": 400.0},
        {"代號": "02888.HK", "成本": 182.00, "數量": 50.0},
        {"代號": "02562.HK", "成本": 4.267, "數量": 3000.0},
        {"代號": "02172.HK", "成本": 13.00, "數量": 1000.0},
        {"代號": "02050.HK", "成本": 39.80, "數量": 300.0},
        {"代號": "01810.HK", "成本": 34.75, "數量": 400.0},
        {"代號": "01530.HK", "成本": 28.54, "數量": 500.0},
        {"代號": "00699.HK", "成本": 19.00, "數量": 1000.0},
        {"代號": "GOOG", "成本": 319.58, "數量": 12.0},
        {"代號": "KO", "成本": 52.98, "數量": 1.0},
        {"代號": "RBLX", "成本": 121.558, "數量": 52.0},
        {"代號": "TEM", "成本": 77.924, "數量": 170.0}
    ]

# --- 4. 功能分欄 (Tabs) ---
tab1, tab2 = st
