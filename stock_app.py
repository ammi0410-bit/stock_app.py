import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 映射表 (對照富途截圖)
HK_NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子"
}
US_NAMES = {"GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"}

# 2. 頁面配置
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
                tk = yf.Ticker(sym)
                h = tk.history(period="1y") # 抓取一年歷史數據
                if h.empty: continue
                
                # --- 絕招：手動運算核心指標 (避開 yfinance 空值) ---
                cp = float(h['Close'].iloc[-1]) # 最新收盤價
                bp = float(r["成本"])
                is_hk = ".HK" in sym
                curr = "HK$" if is_hk else "US$"
                nm = HK_NAMES.get(sym) if is_hk else US_NAMES.get(sym)
                if not nm: nm = sym
                
                # 計算支撐與目標 (即時技術分析)
                y_high = h['High'].max()
                y_low = h['Low'].min()
                
                # 如果 API 沒給分析師數據，強制使用 52 週高低位模擬
                tgt = tk.info.get('targetMeanPrice') or y_high
                sup = tk.info.get('targetLowPrice') or y_low
                rec = str(tk.info.get('recommendationKey', 'HOLD')).upper().replace('_', ' ')
                p_pct = (cp - bp) / bp * 100
                rr = round((tgt - cp) / max(0.1, cp - sup), 2)

                # --- UI 渲染 (強制字體鎖定) ---
                st.markdown(f"#### 💎 {sym} | {nm}")
                
                style = "font-family: 'Roboto', sans-serif; font-weight: 800; font-size: 16px;"
                st.markdown(f"""
                <div style="{style} margin-bottom: 5px;">
                    現價: {curr}{cp:.2f} | 買入價: {curr}{bp:.2f}
                </div>
                <div style="{style} color: {'#ff4b4b' if p_pct < 0 else '#00c853'};">
                    [ 評級: {rec} | R/R: {rr} | 盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}% ]
                </div>
                <div style="background-color: #e8f5e9; padding: 12px; border-radius: 6px; border-left: 6px solid #2e7d32; margin-top: 10px;">
                    <p style="color: #2e7d32; {style} margin: 0; white-space: nowrap;">
                        📍 分析：{nm} 支撐位 {curr}{sup:.2f}，目標價 {curr}{tgt:.2f}。
                    </p>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander("📈 查看走勢圖"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close'], line=dict(color='#00c853')))
                    fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                st.divider()
                
            except Exception as e:
                continue
