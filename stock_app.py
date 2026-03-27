import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 介面與安全性校對 (確保 S25 Ultra 顯示正常)
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

# 2. 持倉數據庫 (校對：引號對稱與逗號 OK)
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

# 3. 功能分區 (Tab 邏輯校對 OK)
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 持倉管理"])
with t2: 
    edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# 4. 核心分析邏輯 (逐行審查優化)
with t1:
    if st.button("🚀 執行全球匯率同步掃描", use_container_width=True):
        # 初始化統計變量
        res, v_mix, p_mix, v_hkd, p_hkd = [], 0.0, 0.0, 0.0, 0.0
        
        # 實時匯率抓取校對
        try:
            usd_hkd = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except:
            usd_hkd = 7.82 # 萬一 API 失效的備用值
            
        st.info(f"💡 當前參考匯率：1 USD = {usd_hkd:.4f} HKD")
        
        # 投資邏輯說明 (約 200 字)
        st.write("---")
        st.markdown("""
        **🏛️ 決策邏輯備忘錄** 本終端以 **Risk/Reward (R/R)** 作為第一判斷基準。對於缺乏分析師目標價的港股，系統自動選取 **52週高位** 作為技術壓力位。  
        * **R/R > 2**: 風險回報優質，建議維持倉位或在低位吸納。  
        * **虧損 > 15%**: 系統將標註為「風險預警」，需檢查技術底線。  
        所有市值已根據實時匯率換算為 HKD 及 USD 進行
