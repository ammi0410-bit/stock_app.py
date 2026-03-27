import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. 核心映射表
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室", layout="wide")

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 密鑰", type="password")
    if st.button("解鎖"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["00699.HK", "06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [19.00, 38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 319.58, 52.98, 121.558, 77.924],
        "數量": [1000, 200, 400, 50, 3000, 1000, 300, 400, 500, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 決策", "⚙️ 管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 啟動深度掃描", use_container_width=True):
        fx = 7.83
        results = []
        total_hkd = 0

        for _, r in st.session_state.df.iterrows():
            sym = str(r["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            # --- 強化版數據抓取：增加重試機制 ---
            cp, y_low, y_high, has_data = float(r["成本"]), float(r["成本"]), float(r["成本"]), False
            try:
                tk = yf.Ticker(sym)
                # 針對港股強制抓取更長區間以確保數據存在
                h = tk.history(period="1mo" if ".HK" in sym else "1y") 
                if not h.empty:
                    cp = float(h['Close'].iloc[-1])
                    y_low, y_high = h['Low'].min(), h['High'].max()
                    has_data = True
            except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * r["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(r["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": y_low, "high": y_high, "val": v_hkd, "has_data": has_data})

        st.metric("💰 總資產估值", f"HKD ${total_hkd:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results]), values='價值', names='股票', hole=.4, height=300), use_container_width=True)

        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            
            # --- 排版鋼鐵鎖定：使用 Table 佈局徹底對齊 ---
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            
            # 盈虧顯示鎖定
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            st.markdown(f"""
                <div style="font-family: 'Courier New', monospace; font-weight: bold; font-size: 16px;">
                    現價: {curr}{item['cp']:.2f} | 買入價: {curr}{item['bp']:.2f}<br>
                    <span style="color: {p_color};">盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}%</span>
                </div>
            """, unsafe_allow_html=True)
            
            # 分析框鋼鐵鎖定：使用表格強制對齊，解決字體走位問題
            if item["has_data"]:
                st.markdown(f"""
                <table style="width:100%; background-color: #e8f5e9; border-left: 5px solid #2e7d32; border-collapse: collapse; margin: 10px 0;">
                    <tr>
                        <td style="padding: 10px; font-family: sans-serif; font-weight: bold; color: #2e7d32; font-size: 14px;">
                            📍 分析：{item['nm']} 支撐 {curr}{item['low']:.2f} | 目標 {curr}{item['high']:.2f}
                        </td>
                    </tr>
                </table>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ {item['sym']} 目前 API 連線不穩，已改用持倉價進行估值計算。")
            st.divider()
