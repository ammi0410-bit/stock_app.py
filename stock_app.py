import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. 頁面配置 ---
st.set_page_config(page_title="全資產智能決策大腦", layout="wide")
st.title("🌐 全資產診斷與換倉系統")

# --- 2. 側邊欄設定 ---
st.sidebar.header("🎯 換倉觀察清單")
watch_list_raw = st.sidebar.text_area("輸入目標 (如: NVDA, BTC-USD, 2800.HK)", "NVDA, BTC-USD, ETH-USD, 0700.HK, 2800.HK")
watch_list = [x.strip().upper() for x in watch_list_raw.split(",")]

st.sidebar.divider()
st.sidebar.header("🛡️ 智能止損 (ATR)")
# 2.0 是標準，2.5 以上適合波動極大的幣種
atr_multiplier = st.sidebar.slider("ATR 波動倍數", 1.0, 4.0, 2.0)

# --- 3. 持倉編輯器 ---
st.subheader("💼 我的持倉清單")
default_data = [
    {"代號": "0005.HK", "成本": 68.0, "數量": 1000},
    {"代號": "BTC-USD", "成本": 60000.0, "數量": 0.1}
]
df_input = pd.DataFrame(default_data)
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# --- 4. 執行診斷 ---
if st.button("🚀 執行全資產分析及換倉部署"):
    st.divider()
    total_exit_cash = 0.0
    summary = []
    
    with st.spinner('正在分析市場波動率...'):
        for _, row in edited_df.iterrows():
            t = row["代號"].upper().strip()
            cost, qty = row["成本"], row["數量"]
            try:
                # 抓取 1 年數據以計算 ATR
                df = yf.download(t, period="1y", progress=False)
                if df.empty: continue
                
                # 數據平整化
                if isinstance(df.columns, pd.MultiIndex):
                    close = df['Close'][t]
                    high = df['High'][t]
                    low = df['Low'][t]
                else:
                    close, high, low = df['Close'], df['High'], df['Low']
                
                curr_p = float(close.iloc[-1])
                
                # --- ATR 智能止損 ---
                tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
                atr = tr.rolling(window=14).mean().iloc[-1]
                smart_stop = curr_p - (atr * atr_multiplier)
                
                # --- 趨勢判斷 ---
                ma20 = close.rolling(20).mean().iloc[-1]
                ma60 = close.rolling(60).mean().iloc[-1]
                trend = "🚀 多頭" if ma20 > ma60 else "📉 空頭"
                
                # --- 財務計算 ---
                pnl_pct = (curr_p - cost) / cost * 100
                market_val = curr_p * qty
                
                # 判定建議：若趨勢轉空 或 跌破智能止損
                should_sell = (ma20 < ma60) or (curr_p < smart_stop)
                if should_sell:
                    total_exit_cash += market_val
                
                summary.append({
                    "資產": t,
                    "現價": f"{curr_p:,.2f}",
                    "盈虧": f"{pnl_pct:.1f}%",
                    "趨勢": trend,
                    "智能止損位": round(smart_stop, 2),
                    "狀態": "⚠️ 建議撤退" if should_sell else "✅ 穩定持有"
                })
            except Exception as e:
                st.error(f"無法分析 {t}: {e}")

    # 顯示分析表
    if summary:
        st.subheader("📋 診斷報告")
        st.dataframe(pd.DataFrame(summary), use_container_width=True)

        # --- 5. 換倉決策 ---
        st.divider()
        st.subheader(f"🔄
