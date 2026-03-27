import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 介面與安全性
st.set_page_config(page_title="家族辦公室 | 決策終端", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業資產管理系統")
    pwd = st.text_input("輸入密鑰", type="password")
    if st.button("🔓 點擊解鎖系統", use_container_width=True):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 2. 持倉數據庫 (校對 OK)
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 持倉管理"])
with t2: edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球/港股共識掃描", use_container_width=True):
        res, v_hkd, p_hkd = [], 0.0, 0.0
        try: usd_hkd = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: usd_hkd = 7.82
        
        st.info(f"💡 實時匯率：1 USD = {usd_hkd:.4f} HKD")
        
        bar = st.progress(0)
        rows = edf.to_dict('records')
        for i, r in enumerate(rows):
            try:
                tk = yf.Ticker(str(r["代號"]).strip())
                h = tk.history(period="1y")
                inf = tk.info
                if h.empty: continue
                
                cp = float(h['Close'].iloc[-1])
                is_hk = ".HK" in str(r["代號"]).upper()
                rate = 1.0 if is_hk else usd_hkd
                curr_sym = "HKD" if is_hk else "USD"
                
                # --- 港股數據補足核心邏輯 ---
                tgt = inf.get('targetMeanPrice')
                if not tgt: # 港股自救方案：取 (52週高位 + 250天線) 的平均值作為估算目標
                    ma250 = h['Close'].rolling(250).mean().iloc[-1] if len(h)>250 else h['Close'].mean()
                    tgt = (float(h['High'].max()) + ma250) / 2
                
                low = inf.get('targetLowPrice')
                if not low: low = float(h['Low'].min())
                
                # 評級自救：如果 N/A，根據股價相對於 50天線的位置判定
                rec = str(inf.get('recommendationKey', 'N/A')).upper()
                if rec == 'N/A':
                    ma50 = h['Close'].rolling(50).mean().iloc[-1]
                    rec = "STRONG BUY (技術走牛)" if cp > ma50 * 1.05 else "BUY (回調吸納)" if cp > ma50 else "UNDERPERFORM (弱勢)"
                
                # R/R 與 升幅
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                upside = ((tgt - cp) / cp * 100)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                
                # --- UI 渲染：加大字體與 Heading ---
                st.markdown(f"## 💎 {r['代號']} | 現價: {curr_sym} {cp:.2f}")
                
                c1, c2, c3, c4 = st.
