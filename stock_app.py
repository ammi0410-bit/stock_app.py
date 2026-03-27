import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 基礎配置
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("密鑰", type="password")
    if st.button("🔓 解鎖", use_container_width=True):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 2. 數據庫
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])
with t2: edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        res, v_hkd, p_hkd = [], 0.0, 0.0
        try: fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.825
        
        st.write(f"### 🌐 實時匯率: 1 USD = {fx:.4f} HKD")
        
        rows = edf.to_dict('records')
        for i, r in enumerate(rows):
            orig_sym = str(r["代號"]).strip()
            sym_to_try = [orig_sym]
            if orig_sym.startswith("0") and ".HK" in orig_sym.upper():
                sym_to_try.append(orig_sym.lstrip("0"))
            
            h, tk, success = None, None, False
            for s in sym_to_try:
                tk = yf.Ticker(s)
                h = tk.history(period="1y")
                if not h.empty: success = True; break
            
            if not success:
                st.warning(f"⚠️ {orig_sym} 數據獲取失敗，請檢查代號。")
                continue

            try:
                inf = tk.info
                # --- 強制獲取股票名稱與代號 ---
                name = inf.get('longName', orig_sym) # 優先獲取全名，失敗則用代號代替
                cp = float(h['Close'].iloc[-1])
                is_hk = ".HK" in orig_sym.upper()
                rate = 1.0 if is_hk else fx
                
                # 數據補足
                tgt = inf.get('targetMeanPrice', float(h['High'].max() * 0.98))
                low = inf.get('targetLowPrice', float(h['
