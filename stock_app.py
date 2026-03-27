import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 映射表 (校正：06082 為壁仞科技)
HK_NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子"
}
US_NAMES = {"GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"}

# 2. 初始化數據
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 密鑰", type="password")
    if st.button("解鎖"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        try:
            fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.828
        
        st.write(f"### 🌐 實時匯率: 1 USD = {fx:.4f} HKD")
        
        for _, r in st.session_state.df.iterrows():
            sym = str(r["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            try:
                tk = yf.Ticker(sym); h = tk.history(period="1y")
                if h.empty: continue
                inf = tk.info; cp = float(h['Close'].iloc[-1]); bp = float(r["成本"])
                is_hk = ".HK" in sym
                nm = HK_NAMES.get(sym) if is_hk else US_NAMES.get(sym)
                if not nm: nm = inf.get('shortName', sym)
                p_pct = (cp - bp) / bp * 100
                curr = "HK$" if is_hk else "US$"
                
                # --- UI 渲染：核心修改處 ---
                st.markdown(f"#### 💎 {sym} | {nm}")
                
                # 使用 Table 佈局強制對齊所有元素，並移除所有 Markdown 語法
                row_style = "font-size: 16px; font-family: sans-serif; font-weight: bold; line-height: 1.5;"
                html_content = f"""
                <div style="{row_style}">
                    <span>現價: {curr}{cp:.2f}</span>
                    <span style="margin: 0 10px; color: #666;">|</span>
                    <span>買入價: {curr}{bp:.2f}</span>
                </div>
                <div style="{row_style} margin-top: 5px;">
                    <span style="color: {'#ff4b4b' if p_pct < 0 else '#00c853'};">
                        [ 評級: {str(inf.get('recommendationKey', 'N/A')).upper()} | 
                        R/R: {round((inf.get('targetMeanPrice', cp*1.1)-cp)/max(0.1, cp-inf.get('targetLowPrice', cp*0.9)), 2)} | 
                        盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}% ]
                    </span>
                </div>
                """
                st.markdown(html_content, unsafe_allow_html=True)
                
                # 分析提示
                tgt = inf.get('targetMeanPrice', 'N/A')
                st.success(f"📍 分析：目標價 {tgt}")
                
                with st.expander("📈 走勢圖"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close']))
                    fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                st.divider()
            except: continue
