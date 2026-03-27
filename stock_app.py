import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 映射表 (根據你的截圖 100% 校正)
HK_NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子"
}
US_NAMES = {"GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"}

# 2. 頁面基本配置
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 密鑰", type="password")
    if st.button("解鎖"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 3. 初始化數據
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        try:
            fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.828
        
        for _, r in st.session_state.df.iterrows():
            sym = str(r["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            try:
                # --- 絕招 1：只抓 History，不依賴 Info ---
                tk = yf.Ticker(sym)
                h = tk.history(period="1y") 
                if h.empty: continue
                
                cp = float(h['Close'].iloc[-1]) # 最新現價
                bp = float(r["成本"])
                is_hk = ".HK" in sym
                curr = "HK$" if is_hk else "US$"
                nm = HK_NAMES.get(sym) if is_hk else US_NAMES.get(sym)
                if not nm: nm = sym
                
                # --- 絕招 2：手動計算分析指標，確保 100% 顯示 ---
                y_high = h['High'].max() # 一年最高作為壓力/目標
                y_low = h['Low'].min()   # 一年最低作為支撐
                p_pct = (cp - bp) / bp * 100
                rr = round((y_high - cp) / max(0.1, cp - y_low), 2)

                # --- 絕招 3：HTML 全封鎖渲染 (解決字體一致性) ---
                st.markdown(f"#### 💎 {sym} | {nm}")
                
                # 使用系統預設無襯線字體，並強制不換行，確保 US/HK 與數字對齊
                common_style = "font-family: sans-serif; font-weight: bold; font-size: 16px;"
                
                st.markdown(f"""
                <div style="{common_style} margin-bottom: 5px;">
                    現價: {curr}{cp:.2f} | 買入價: {curr}{bp:.2f}
                </div>
                <div style="{common_style} color: {'#ff4b4b' if p_pct < 0 else '#00c853'};">
                    [ R/R: {rr} | 盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}% ]
                </div>
                <div style="background-color: #e8f5e9; padding: 12px; border-radius: 6px; border-left: 6px solid #2e7d32; margin-top: 10px;">
                    <p style="color: #2e7d32; {common_style} margin: 0; white-space: nowrap;">
                        📍 分析：{nm} 支撐位 {curr}{y_low:.2f}，目標價 {curr}{y_high:.2f}。
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📈 查看走勢圖"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close'], line=dict(color='#00c853')))
                    fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                st.divider()
                
            except:
                continue
