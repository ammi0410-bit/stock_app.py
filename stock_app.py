import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 數據初始化 (含繁體中文映射)
HK_NAMES = {
    "06082.HK": "騰訊控股", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "中銀航空租賃", "02172.HK": "微創醫療", "02050.HK": "索信達控股",
    "01810.HK": "小米集團", "01530.HK": "三生製藥", "00699.HK": "神州租車"
}

if 'df' not in st.session_state:
    d = {"代號": list(HK_NAMES.keys()) + ["GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

# 2. 安全解鎖
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("密鑰", type="password")
    if st.button("🔓 解鎖系統", use_container_width=True):
        if pwd == "13579": 
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. 主分頁
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])
with t2:
    edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    st.session_state.df = edf

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        res, v_hkd, p_hkd, c_hkd = [], 0.0, 0.0, 0.0
        try: fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.825
        
        st.write(f"### 🌐 實時匯率: 1 USD = {fx:.4f} HKD")
        stocks = st.session_state.df.to_dict('records')
        
        for r in stocks:
            s_orig = str(r["代號"]).strip().upper()
            is_hk = ".HK" in s_orig
            s_list = [s_orig, s_orig.lstrip("0")] if s_orig.startswith("0") and is_hk else [s_orig]
            
            h, tk, ok = None, None, False
            for s in s_list:
                try:
                    tk = yf.Ticker(s); h = tk.history(period="1y")
                    if not h.empty: ok = True; break
                except: continue
            if not ok: continue

            try:
                inf = tk.info
                nm = HK_NAMES.get(s_orig, inf.get('shortName', s_orig)) if is_hk else inf.get('longName', s_orig)
                cp = float(h['Close'].iloc[-1])
                bp = float(r["成本"])
                rate =
