import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

# --- 1. 頁面配置 ---
st.set_page_config(page_title="全資產智能決策大腦", layout="wide")
st.title("🌐 全資產診斷與換倉系統")

# --- 2. 側邊欄：換倉觀察清單 ---
st.sidebar.header("🎯 換倉觀察清單")
watch_list_raw = st.sidebar.text_area("輸入目標 (如: NVDA, BTC-USD)", "NVDA, BTC-USD, ETH-USD, 2800.HK")
watch_list = [x.strip().upper() for x in watch_list_raw.split(",") if x.strip()]

st.sidebar.divider()
atr_multiplier = st.sidebar.slider("🛡️ ATR 智能止損倍數", 1.0, 4.0, 2.0)

# --- 3. 持倉編輯器 ---
st.subheader("💼 我的持倉清單")
df_input = pd.DataFrame([
    {"代號": "0005.HK", "成本": 68.0, "數量": 1000.0},
    {"代號": "BTC-USD", "成本": 60000.0, "數量": 0.1}
])
edited_df = st.data_editor(df_input, num_rows="dynamic", use_container_width=True)

# --- 4. 執行分析 ---
if st.button("🚀 執行全資產分析"):
    st.divider()
    total_exit_cash = 0.0
    summary = []
    
    with st.spinner('數據計算中...'):
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
                
                # ATR 計算
                tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
                atr = tr.rolling(14).mean().iloc[-1]
                smart_stop = curr_p - (atr * atr_multiplier)
                
                # 趨勢與財務
                ma20, ma60 = close.rolling(20).mean().iloc[-1], close.rolling(60).mean().iloc[-1]
                pnl_pct = (curr_p - cost) / cost * 100
                should_sell = (ma20 < ma60) or (curr_p < smart_stop)
                
                if should_sell: total_exit_cash += (curr_p * qty)
                
                summary.append({
                    "資產": t, "現價": round(curr_p, 2), "盈虧": f"{pnl_pct:.1f}%",
                    "趨勢": "🚀 多頭" if ma20 > ma60 else "📉 空頭",
                    "智能止損": round(smart_stop, 2),
                    "狀態": "⚠️ 建議撤退" if should_sell else "✅ 持有"
                })
            except: st.error(f"無法分析 {t}")

    if summary:
        st.subheader("📋 診斷報告")
        st.dataframe(pd.DataFrame(summary), use_container_width=True)

        if total_exit_cash > 0:
            st.divider()
            st.subheader(f"🔄 換倉建議 (預計可用資金: ${total_exit_cash:,.1f})")
            col_l, col_r = st.columns(2)
            with col_l:
                st.warning("🪜 分批撤退計畫")
                st.write(f"1. 立即減持 (30%): ${total_exit_cash*0.3:,.0f}")
                st.write(f"2. 破位減持 (40%): ${total_exit_cash*0.4:,.0f}")
                st.write(f"3. 確認轉向 (30%): ${total_exit_cash*0.3:,.0f}")
            with col_r:
                st.success("🎯 強勢換入目標")
                recommends = []
                for wt in watch_list:
                    try:
                        w_df = yf.download(wt, period="1y", progress=False)
                        w_c = w_df['Close'][wt] if isinstance(w_df.columns, pd.MultiIndex) else w_df['Close']
                        if w_c.rolling(20).mean().iloc[-1] > w_c.rolling(60).mean().iloc[-1]:
                            w_curr = float(w_c.iloc[-1])
                            recommends.append({"目標": wt, "現價": w_curr, "可買數量": int(total_exit_cash/w_curr)})
                    except: continue
                if recommends: st.table(pd.DataFrame(recommends))
                else: st.write("觀察名單暫無強勢標的")
else:
    st.info("👈 請在上方輸入持倉，並點擊按鈕分析。")
