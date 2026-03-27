import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 頁面配置 ---
st.set_page_config(page_title="私人資產配置大腦", layout="wide")

# --- 2. 安全登入系統 (Secrets) ---
# 在側邊欄建立密碼輸入框
st.sidebar.header("🔐 安全認證")
password_input = st.sidebar.text_input("輸入解鎖密碼", type="password")

# 定義你的密碼
CORRECT_PASSWORD = "13579"

# 檢查密碼
if password_input != CORRECT_PASSWORD:
    if password_input == "":
        st.warning("請在左側側邊欄輸入密碼以解鎖持倉數據。")
    else:
        st.error("密碼錯誤，請重新輸入。")
    # 密碼錯誤時停止執行後續代碼
    st.stop()

# --- 🔓 登入成功後顯示的內容 ---
st.title("🌐 私人資產診斷與戰略圖表")

# --- 3. 側邊欄：換倉觀察清單 ---
st.sidebar.divider()
st.sidebar.header("🎯 換倉觀察清單")
watch_list_raw = st.sidebar.text_area("輸入目標 (如: BTC-USD, NVDA)", "2800.HK, BTC-USD, NVDA")
watch_list = [x.strip().upper() for x in watch_list_raw.split(",") if x.strip()]

st.sidebar.divider()
atr_mult = st.sidebar.slider("🛡️ 止損 ATR 倍數", 1.0, 4.0, 2.0)

# --- 4. 持倉記憶區 (已根據截圖更新) ---
st.subheader("💼 我的現有持倉 (已解鎖)")

if 'portfolio' not in st.session_state:
    # 根據圖片精確錄入的持倉數據
    st.session_state.portfolio = [
        # --- 港股部分 (注意港股代號格式需補 0 且加 .HK) ---
        {"代號": "06082.HK", "成本": 38.20, "數量": 200.0}, # 壁仞科技
        {"代號": "03888.HK", "成本": 32.00, "數量": 400.0}, # 金山軟件
        {"代號": "02888.HK", "成本": 182.00, "數量": 50.0},  # 渣打集團
        {"代號": "02562.HK", "成本": 4.267, "數量": 3000.0}, # 獅騰控股
        {"代號": "02172.HK", "成本": 13.00, "數量": 1000.0}, # 微創腦科學
        {"代號": "02050.HK", "成本": 39.80, "數量": 300.0},  # 三花智控
        {"代號": "01810.HK", "成本": 34.75, "數量": 400.0},  # 小米集團-W
        {"代號": "01530.HK", "成本": 28.54, "數量": 500.0},  # 三生製藥
        {"代號": "00699.HK", "成本": 19.00, "數量": 1000.0}, # 均勝電子
        # --- 美股部分 ---
        {"代號": "GOOG", "成本": 319.58, "數量": 12.0},     # 谷歌-C
        {"代號": "KO", "成本": 52.98, "數量": 1.0},         # 可口可樂
        {"代號": "RBLX", "成本": 121.558, "數量": 52.0},    # Roblox
        {"代號": "TEM", "成本": 77.924, "數量": 170.0}       # Tempus AI
    ]

# 使用數據編輯器顯示持倉
edited_df = st.data_editor(pd.DataFrame(st.session_state.portfolio), num_rows="dynamic", use_container_width=True)

# --- 5. 執行分析 ---
if st.button("🚀 執行全方位戰略分析"):
    st.divider()
    total_exit_cash = 0.0
    summary = []
    
    # 建立一個進度條
    progress_bar = st.progress(0)
    num_stocks = len(edited_df)
    
    for index, row in edited_df.iterrows():
        t = str(row["代號"]).upper().strip()
        cost, qty = float(row["成本"]), float(row["數量"])
        try:
            # 抓取數據 (1y)
            df = yf.download(t, period="1y", progress=False)
            if df.empty: continue
            
            # 數據提取
            if isinstance(df.columns, pd.MultiIndex):
                close = df['Close'][t]
                high = df['High'][t]
                low = df['Low'][t]
            else:
                close, high, low = df['Close'], df['High'], df['Low']
            
            curr_p = float(close.iloc[-1])
            
            # ATR 計算與止盈止損位
            tr = np.maximum(high - low, np.maximum(abs(high - close.shift(1)), abs(low - close.shift(1))))
            atr = tr.rolling(14).mean().iloc[-1]
            s_stop = curr_p - (atr * atr_mult)
            tp_s, tp_m, tp_l = curr_p + atr, curr_p + (atr*2), curr_p + (atr*3)
            
            # 趨勢判斷 (20/60MA)
            ma20 = close.rolling(20).mean().iloc[-1]
            ma60 = close.rolling(60).mean().iloc[-1]
            pnl_pct = (curr_p - cost) / cost * 100
            should_sell = (ma20 < ma60) or (curr_p < s_stop)
            if should_sell: total_exit_cash += (curr_p * qty)
            
            summary.append({
                "資產": t, "現價": round(curr_p, 2), "盈虧": f"{pnl_pct:.1f}%",
                "趨勢": "🚀 多頭" if ma20 > ma60 else "📉 空頭",
                "短期止盈": round(tp_s, 2), "中期止盈": round(tp_m, 2), "長期止盈": round(tp_l, 2),
                "智能止損": round(s_stop, 2), "狀態": "⚠️ 建議撤退" if should_sell else "✅ 持有"
            })

            # --- 繪製部署圖 ---
            with st.expander(f"📊 查看 {t} ({pnl_pct:.1f}%) 戰略部署圖", expanded=(pnl_pct < -20)):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=close.index, y=close, name="現價", line=dict(color='white', width=2)))
                fig.add_hline(y=cost, line_dash="dash", line_color="yellow", annotation_text="你的成本")
                fig.add_hline(y=s_stop, line_dash="dot", line_color="red", annotation_text="智能止損")
                fig.add_hline(y=tp_s, line_dash="dash", line_color="green", annotation_text="短期止盈")
                fig.add_hline(y=tp_l, line_dash="dash", line_color="cyan", annotation_text="長期目標")
                fig.update_layout(title=f"{t} 戰略位置", template="plotly_dark", height=400, margin=dict(l=20, r=20, t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
            
            # 更新進度條
            progress_bar.progress((index + 1) / num_stocks)

        except: st.error(f"分析 {t} 時出錯")

    # 顯示總結表
    if summary:
        st.divider()
        st.subheader("📋 全資產診斷與三重止盈清單")
        
        # 排序：將虧損最多的放在最上面
        summary_df = pd.DataFrame(summary)
        summary_df['pnl_num'] = summary_df['盈虧'].str.replace('%','').astype(float)
        summary_df = summary_df.sort_values(by='pnl_num', ascending=True).drop(columns=['pnl_num'])
        
        st.dataframe(summary_df, use_container_width=True)
        
        if total_exit_cash > 0:
            st.warning(f"🔄 建議撤退資金 (蝕緊/趨勢差): 約 ${total_exit_cash:,.1f} (可用於轉入強勢觀察標的)")
else:
    st.info("👈 確認持倉無誤後，點擊「執行分析」按鈕。")
