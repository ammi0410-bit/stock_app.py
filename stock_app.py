import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 介面配置 ---
st.set_page_config(page_title="家族辦公室決策終端", layout="wide")
st.markdown("<style>.stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }</style>", unsafe_allow_html=True)

# --- 2. 安全閘口 (實體解鎖按鈕) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 家族資產管理系統")
    pwd_input = st.text_input("Access Code", type="password", placeholder="輸入密碼...")
    if st.button("🔓 解鎖系統 (Enter)", use_container_width=True):
        if pwd_input == "13579":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("密鑰錯誤")
    st.stop()

# --- 3. 持倉數據 (採用 DataFrame 定義，語法最穩) ---
if 'portfolio' not in st.session_state:
    data = {
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.0, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.56, 77.92],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    }
    st.session_state.portfolio = pd.DataFrame(data)

# --- 4. 功能分欄 ---
tab1, tab2 = st.tabs(["📊 決策分析畫板", "⚙️ 數據管理"])

with tab2:
    edited_df = st.data_editor(st.session_state.portfolio, num_rows="dynamic", use_container_width=True)
    if st.sidebar.button("登出"):
        st.session_state.auth = False
        st.rerun()

with tab1:
    st.title("🏛️ 專業資產配置終端")
    if st.button("🚀 啟動全球分析師共識掃描", use_container_width=True):
        summary, total_val, total_pnl = [], 0.0, 0.0
        prog = st.progress(0)
        
        for i, row in edited_df.iterrows():
            t = str(row["代號"]).upper().strip()
            try:
                tk = yf.Ticker(t)
                hist = tk.history(period="1y")
                info = tk.info
                if hist.empty: continue
                
                curr_p = float(hist['Close'].iloc[-1])
                target = info.get('targetMeanPrice', curr_p * 1.05)
                t_low = info.get('targetLowPrice', curr_p * 0.9)
                rec = info.get('recommendationKey', 'N/A').upper()
                
                # R/R 計算與摘要
                rr = round((target - curr_p) / max(0.01, curr_p - t_low), 2)
                upside = (target - curr_p) / curr_p * 100
                pnl_pct = (curr_p - row["成本"]) / row["成本"] * 100
                
                summary.append({"資產": t, "現價": round(curr_p, 2), "R/R": rr, "盈虧%": round(pnl_pct, 1), "目標": round(target, 2), "底線": round(t_low, 2)})
                
                with st.expander(f"🔍 {t} 深度診斷 (R/R: {rr})", expanded=(pnl_pct < -10)):
                    c1, c2 = st.columns([2, 1])
                    with c1:
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="價格", line=dict(color='#00d1ff')))
                        fig.add_hline(y=target, line_dash="dash", line_color="#00ff00", annotation_text="目標")
                        fig.add_hline(y=t_low, line_dash="dot", line_color="#ff4b4b", annotation_text="底線")
                        fig.add_hline(y=row["成本"], line_dash="solid", line
