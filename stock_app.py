import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 配置與安全 (移除三引號，改用單行定義)
st.set_page_config(page_title="家族辦公室 | 財務終端", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業資產管理系統")
    pwd = st.text_input("輸入密鑰", type="password")
    if st.button("🔓 點擊解鎖系統", use_container_width=True):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 2. 持倉數據 (校對：引號對齊 OK)
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

# 3. 功能分頁
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 持倉管理"])
with t2: edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# 4. 核心邏輯 (校對：逐行防截斷 OK)
with t1:
    if st.button("🚀 執行全球匯率同步掃描", use_container_width=True):
        res, v_mix, p_mix, v_hkd, p_hkd = [], 0.0, 0.0, 0.0, 0.0
        
        # 匯率抓取
        try: usd_hkd = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: usd_hkd = 7.82
        
        st.info(f"💡 當前參考匯率：1 USD = {usd_hkd:.4f} HKD")
        st.subheader("🏛️ 家族資產操作邏輯備忘")
        st.write("本系統以 Risk/Reward (R/R) 為核心。針對港股，若無分析師目標價，自動取 52 週高位為壓力位。R/R > 2 視為優質博弈機會。若虧損超過 15% 則觸發預警。所有市值已統一換算至港幣及美金。")

        bar = st.progress(0)
        rows = edf.to_dict('records')
        
        for i, r in enumerate(rows):
            try:
                tk = yf.Ticker(str(r["代號"]).strip())
