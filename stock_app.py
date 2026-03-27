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

# 2. 港股繁體中文映射
HK_NAMES = {
    "06082.HK": "騰訊控股", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "中銀航空租賃", "02172.HK": "微創醫療", "02050.HK": "索信達控股",
    "01810.HK": "小米集團", "01530.HK": "三生製藥", "00699.HK": "神州租車"
}

# 3. 數據庫
if 'df' not in st.session_state:
    d = {"代號": list(HK_NAMES.keys()) + ["GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df
