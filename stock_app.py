import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. 網頁配置 ---
st.set_page_config(page_title="全資產智能決策大腦", layout="wide")
st.title("🌐 全資產 (股市 & 加密貨幣) 診斷與換倉系統")

# --- 2. 側邊欄：觀察清單與參數 ---
st.sidebar.header("🎯 換倉/買入觀察清單")
watch_list_raw = st.sidebar.text_area("輸入目標 (如: NVDA, BTC-USD, ETH-USD, 2800.HK)", "NVDA, BTC-USD, ETH-USD, 0700.HK")
watch_list = [x.strip().upper() for x in watch_list_raw.split(",")]

st.sidebar.divider()
st.sidebar.header("🛡️ 智能止損參數 (ATR)")
atr_multiplier = st.sidebar.slider("ATR 波動倍數 (建議 2.0)", 1.0, 3.5, 2.0)

# --- 3. 主頁面：持倉編輯器 ---
st.subheader("💼 我的持倉清單 (支持股票及加密貨幣)")
st.caption("提示：加密貨幣請用 'BTC-USD' 格式；港股用 '0005.HK'。")

default_data = [
    {"代號": "0005.HK", "成本": 68.5, "數量": 1000},
    {"代號": "BTC-USD", "成本": 62000.0, "數量": 0.1},
    {"代號": "9988.HK", "成本": 85.0, "數量": 500}
]
df_input = pd.DataFrame(default_data)
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# --- 4. 核心診斷邏輯 ---
if st.button("🚀 執行全資產分析"):
    st.divider()
    total_exit_cash_hkd = 0.0
    summary = []
    
    with st.spinner('正在分析市場數據與波動率...'):
        for _, row in edited_df.iterrows():
            t = row["代號"].upper().strip()
            cost, qty = row["成本"], row["數量"]
            try:
                # 抓取數據 (1年歷史以計算 ATR)
                df = yf.download(t, period="1y", progress=False)
                if df.empty: continue
                
                # 數據平整化
                close = df['Close'][t] if isinstance(df.columns, pd.MultiIndex) else df['Close']
                high = df['High'][t] if isinstance(df.columns, pd.MultiIndex) else df['High']
                low = df['Low'][t] if isinstance(df.columns, pd.MultiIndex) else df['Low']
                
                curr_p = float(close.iloc[-1])
                
                # --- ATR 智能止損計算 ---
                # TR = max(high-low, abs(high-prev_close), abs(low-prev_close))
                tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
                atr = tr.rolling(window=14).mean().iloc[-1]
                smart_stop = curr_p - (atr * atr_multiplier)
                
                # --- 趨勢判斷 (20/60 均線) ---
                ma20 = close.rolling(20).mean().iloc[-1]
                ma60 = close.rolling(60).mean().iloc[-1]
                trend = "🚀 多頭" if ma20 > ma60 else "📉 空頭"
                
                # --- 財務計算 ---
                pnl_pct = (curr_p - cost) / cost * 100
                market_val = curr_p * qty
                
                # 判定是否建議換倉
                should_sell = ma20 < ma60 or curr_p < smart_stop
