import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 介面與 CSS 佈局 ---
st.set_page_config(page_title="私人家族辦公室 | 決策終端", layout="wide")

# 強制暗黑模式感與元件美化
st.markdown("""
    <style>
    .stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }
    div[data-testid="stExpander"] { border: 1px solid #30363d; border-radius: 10px; margin-bottom: 10px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #238636; color: white; }
    </style>
""", unsafe_allow_html=True)

# --- 2. 安全閘口 (支援 Enter 鍵) ---
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🛡️ 家族資產管理系統")
    st.write("請輸入存取密鑰以解鎖全球分析數據。")
    # label_visibility="collapsed" 讓介面更簡潔
    pwd = st.text_input("Access Code", type="password", placeholder="輸入密碼後按 Enter 鍵")
    
    if pwd == "13579":
        st.session_state.authenticated = True
        st.rerun() # 立即刷新頁面進入主程式
    elif pwd != "":
        st.error("密鑰無效，請重新輸入。")
    st.stop()

# --- 🔓 驗證成功後的內容 ---

# --- 3. 初始化持倉數據 (已校對) ---
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
        {"代號": "
