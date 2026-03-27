import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 頁面基礎配置 ---
st.set_page_config(page_title="家族辦公室決策終端", layout="wide")
st.markdown("<style>.stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }</style>", unsafe_allow_html=True)

# --- 2. 安全認證 (含實體按鈕) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 家族資產管理系統")
    pwd = st.text_input("Access Code", type="password", placeholder="輸入密碼...")
    if st.button("🔓 解鎖系統 (Enter)", use_container_width=True):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("密鑰錯誤")
    st.stop()

# --- 3. 初始化數據 (DataFrame 格式最穩) ---
if 'portfolio' not in st.session_state:
    d = {
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.0, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.56, 77.92],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    }
    st.session_state.portfolio = pd.DataFrame(d)

# --- 4. 功能分欄 ---
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 數據管理"])

with t2:
    edf = st.data_editor(st.session_state.portfolio, num_rows="dynamic", use_container_width=True)
    if st.sidebar.button("登出"):
        st.session_state.auth = False
        st.rerun()

with t1:
    st.title("🏛️ 專業資產配置終端")
    if st.button("🚀 啟動掃描", use_container_width=True):
        summary, total_v, total_p = [], 0.0, 0.0
        bar = st.progress(0)
        
        for i, r in edf.iterrows():
            sym = str(r["代號"]).upper().strip()
            try:
                tk = yf.Ticker(sym)
                h = tk.history(period="1y")
                inf = tk.info
                if h.empty: continue
                
                cp = float(h['Close'].iloc[-1])
                tgt = inf.get('targetMeanPrice', cp * 1.05)
                low = inf.get('targetLowPrice', cp * 0.9)
                rr = round((tgt - cp) / max(0.01, cp - low), 2)
                
                # 計算摘要數據
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                summary.append({"資產": sym, "現價": round(cp, 2), "R/R": rr, "盈虧%": round(p_pct, 1), "目標": round(tgt, 2)})
                
                with st.expander(f"🔍 {sym} 診斷 (R/R: {rr})", expanded=(p_pct < -10)):
                    c1, c2 = st.
