import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 頁面配置 ---
st.set_page_config(page_title="全資產智能決策大腦", layout="wide")
st.title("🌐 全資產診斷、三重止盈與戰略圖表")

# --- 2. 側邊欄：換倉觀察清單 ---
st.sidebar.header("🎯 換倉觀察清單")
watch_list_raw = st.sidebar.text_area("輸入目標 (如: NVDA, BTC-USD)", "NVDA, BTC-USD, ETH-USD, 2800.HK")
watch_list = [x.strip().upper() for x in watch_list_raw.split(",") if x.strip()]

st.sidebar.divider()
atr_mult = st.sidebar.slider("🛡️ 止損 ATR 倍數", 1.0, 4.0, 2.0)

# --- 3. 持倉記憶區 (請在此修改你的真實持倉) ---
st.subheader("💼 我的持倉清單")
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"代號": "0005.HK", "成本": 68.0, "數量": 1000.0},
        {"代號": "BTC-USD", "成本": 60000.0, "數量": 0.1},
        {"代號": "NVDA", "成本": 115.0, "數量": 20.0}
    ]

edited_df = st.data_editor(pd.DataFrame(st.session_state.portfolio), num_rows="dynamic", use_container_width=True)

# --- 4. 執行分析 ---
if st.button("🚀 執行全方位戰略分析"):
    st.divider()
    total_exit_cash = 0.0
    summary = []
    
    for _, row in edited_df.iterrows():
        t = str(row["代號"]).upper().strip()
        cost, qty = float(row["成本"]), float(row["數量"])
        try:
            df = yf.download(t, period="1y", progress=False)
            if df.empty: continue
            
            # 數據提取
            close = df['Close'][t] if isinstance(df.columns, pd.MultiIndex) else df['Close']
            high = df['High'][t] if isinstance(df.columns, pd.MultiIndex) else df['High']
            low = df['Low'][t] if isinstance(df.columns, pd.MultiIndex) else df['Low']
            curr_p = float(close.iloc[-1])
            
            # ATR 計算與止盈止損位
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            atr = tr.rolling(14).mean().iloc[-1]
            s_stop = curr_p - (atr * atr_mult)
            tp_s, tp_m, tp_l = curr_p + atr, curr_p + (atr*2), curr_p + (atr*3)
            
            # 趨勢判斷
            ma20 = close.rolling(20).mean().iloc[-1]
            ma60 = close.rolling(60).mean().iloc[-1]
            should_sell = (ma20 < ma60) or (curr_p < s_stop)
            if should_sell: total_exit_cash += (curr_p * qty)
            
            summary.append({
                "資產": t, "現價": round(curr_p, 2), "盈虧": f"{(curr_p-cost)/cost*100:.1f}%",
                "趨勢": "🚀 多頭" if ma20 > ma60 else "📉 空頭",
                "短期止盈": round(tp_s, 2), "中期止盈": round(tp_m, 2), "長期止盈": round(tp_l, 2),
                "智能止損": round(s_stop, 2), "狀態": "⚠️ 建議撤退" if should_sell else "✅ 持有"
            })

            # --- 繪製部署圖 ---
            with st.expander(f"📊 查看 {t} 戰略部署圖", expanded=True):
                fig = go.Figure()
                # 股價線
                fig.add_trace(go.Scatter(x=close.index, y=close, name="現價", line=dict(color='white', width=2)))
                # 成本線
                fig.add_hline(y=cost, line_dash="dash", line_color="yellow", annotation_text="你的成本")
                # 止損線
                fig.add_hline(y=s_stop, line_dash="dot", line_color="red", annotation_text="智能止損")
                # 止盈線
                fig.add_hline(y=tp_s, line_dash="dash", line
