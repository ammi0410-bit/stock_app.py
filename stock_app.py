import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# 1. 名稱映射表
HK_NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子"
}
US_NAMES = {"GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰", type="password")
    if st.button("解鎖系統"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 數據初始化
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 實時決策監控", "⚙️ 資產配置管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 啟動全資產掃描", use_container_width=True):
        try:
            fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.828
        
        results = []
        total_hkd = 0

        # --- 第一階段：獨立抓取，互不干擾 ---
        for _, r in st.session_state.df.iterrows():
            sym = str(r["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            try:
                tk = yf.Ticker(sym)
                h = tk.history(period="1y")
                if h.empty: continue
                
                cp = float(h['Close'].iloc[-1])
                is_hk = ".HK" in sym
                val_hkd = (cp * r["數量"]) * (1 if is_hk else fx)
                total_hkd += val_hkd
                
                results.append({
                    "sym": sym, "h": h, "cp": cp, "bp": float(r["成本"]),
                    "is_hk": is_hk, "val_hkd": val_hkd,
                    "nm": HK_NAMES.get(sym) or US_NAMES.get(sym) or sym
                })
            except: continue

        # --- 第二階段：頂部看板 ---
        if results:
            st.subheader(f"💰 資產總值: HK${total_hkd:,.0f}")
            pie_df = pd.DataFrame([{"股票": x["nm"], "價值": x["val_hkd"]} for x in results])
            fig_pie = px.pie(pie_df, values='價值', names='股票', hole=.4, height=300)
            fig_pie.update_layout(margin=dict(l=0,r=0,t=0,b=0))
            st.plotly_chart(fig_pie, use_container_width=True)
            st.divider()

        # --- 第三階段：詳細分析 (解決溢出與對齊) ---
        for item in results:
            sym, h, cp, bp, nm = item["sym"], item["h"], item["cp"], item["bp"], item["nm"]
            curr = "HK$" if item["is_hk"] else "US$"
            y_high, y_low = h['High'].max(), h['Low'].min()
            p_pct = (cp - bp) / bp * 100
            rr = round((y_high - cp) / max(0.1, cp - y_low), 2)
            
            is_danger = cp <= y_low * 1.05 # 警告閾值
            bg = "#ffebee" if is_danger else "#e8f5e9"
            border = "#c62828" if is_danger else "#2e7d32"
            
            st.markdown(f"#### 💎 {sym} | {nm} (佔比: {item['val_hkd']/total_hkd*100:.1f}%)")
            
            # 使用 Flexbox 解決排版走位與文字溢出
            st.markdown(f"""
                <div style="font-family: sans-serif; font-weight: bold; font-size: 15px; line-height: 1.6;">
                    現價: {curr}{cp:.2f} | 買入價: {curr}{bp:.2f}<br>
                    <span style="color: {'#ff4b4b' if p_pct < 0 else '#00c853'};">
                        [ R/R: {rr} | 盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}% ]
                    </span>
                </div>
                <div style="background-color: {bg}; padding: 10px; border-radius: 6px; border-left: 5px solid {border}; margin: 10px 0; word-wrap: break-word;">
                    <span style="color: {border}; font-weight: bold; font-family: sans-serif; font-size: 14px;">
                        📍 分析：{nm} 支撐 {curr}{y_low:.2f}，目標 {curr}{y_high:.2f}。
                        { '⚠️ 警告：接近一年低位！' if is_danger else '' }
                    </span>
                </div>
            """, unsafe_allow_html=True)
            
            with st.expander("📈 走勢詳情"):
                fig = go.Figure(go.Scatter(x=h.index, y=h['Close'], line=dict(color=border)))
                fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                st.plotly_chart(fig, use_container_width=True)
            st.divider()
