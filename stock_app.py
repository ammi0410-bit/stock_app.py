import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 專業風格配置 ---
st.set_page_config(page_title="私人家族辦公室系統", layout="wide", initial_sidebar_state="collapsed")

# 自定義 CSS 讓介面更精緻
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 安全認證 ---
st.sidebar.title("🔐 身分驗證")
pwd = st.sidebar.text_input("Access Code", type="password")
if pwd != "13579":
    st.info("⚠️ 請在側邊欄輸入密碼以啟動決策大腦。")
    st.stop()

# --- 3. 持倉數據庫 ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"代號": "06082.HK", "成本": 38.20, "數量": 200.0, "類型": "港股"},
        {"代號": "03888.HK", "成本": 32.00, "數量": 400.0, "類型": "港股"},
        {"代號": "02888.HK", "成本": 182.00, "數量": 50.0, "類型": "港股"},
        {"代號": "02562.HK", "成本": 4.267, "數量": 3000.0, "類型": "港股"},
        {"代號": "02172.HK", "成本": 13.00, "數量": 1000.0, "類型": "港股"},
        {"代號": "02050.HK", "成本": 39.80, "數量": 300.0, "類型": "港股"},
        {"代號": "01810.HK", "成本": 34.75, "數量": 400.0, "類型": "港股"},
        {"代號": "01530.HK", "成本": 28.54, "數量": 500.0, "類型": "港股"},
        {"代號": "00699.HK", "成本": 19
