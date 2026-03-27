import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 介面與 CSS 配置 ---
st.set_page_config(page_title="家族辦公室決策終端", layout="wide")
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    .stExpander { border: 1px solid #30363d !important; border-radius: 10px !important; }
    div.stButton > button:first-child { background-color: #238636; color: white; width: 100%; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 安全認證 (含實體解鎖按鈕) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 家族資產管理系統")
    st.write("請輸入存取密鑰以開啟深度分析。")
    pwd_input = st.text_input("Access Code", type="password", placeholder="輸入密碼...")
    
    if st.button("🔓 解鎖系統 (Enter)"):
        if pwd_input == "13579":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("密鑰錯誤")
    st.stop()

# --- 3. 持倉數據庫 (校對完畢：無語法錯誤) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"代號": "06082.HK", "成本": 38.20, "數量": 200.0},
        {"代號": "03888.HK", "成本": 32.00, "數量": 400.0},
        {"代號": "02888.HK", "成本": 182.0, "數量": 50.0},
        {"代號": "02562.HK", "成本": 4.267, "數量": 3000.0},
        {"代號": "02172.HK", "成本": 13.00, "數量": 1000.0},
        {"代號": "02050.HK", "成本": 39.80, "數量": 300.0},
        {"代號": "01810.HK", "成本": 34.75, "數量": 400.0},
        {"代號": "01530.HK", "成本": 28.54, "數量": 500.0},
        {"代號": "
