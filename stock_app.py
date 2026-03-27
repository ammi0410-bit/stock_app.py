import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. 名稱對照
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
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 決策", "⚙️ 管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 啟動掃描", use_container_width=True):
        fx = 7.83
        results = []
        total_hkd = 0

        for _, r in st.session_state.df.iterrows():
            sym = str(r["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            # --- 混合數據引擎：抓不到數據也絕不消失 ---
            try:
                tk = yf.Ticker(sym)
                h = tk.history(period="5d") # 只抓5天增加成功率
                if h.empty: raise ValueError("API Timeout")
                cp = float(h['Close'].iloc[-1])
                y_low, y_high = h['Low'].min(), h['High'].max()
                has_data = True
            except:
                cp = float(r["成本"]) # 抓不到就用成本價保底顯示
                y_low, y_high = cp, cp
                has_data = False
            
            is_hk = ".HK" in sym
            val_hkd = (cp * r["數量"]) * (1 if is_hk else fx)
            total_hkd += val_hkd
            
            results.append({
                "sym": sym, "cp": cp, "bp": float(r["成本"]),
                "nm": NAMES.get(sym, sym), "is_hk": is_hk,
                "low": y_low, "high": y_high, "val": val_hkd, "has_data": has_data
            })

        st.metric("💰 總資產估值", f"HKD ${total_hkd:,.0f}")
        # 圓餅圖
        pie_df = pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results])
        st.plotly_chart(px.pie(pie_df, values='價值', names='股票', hole=.4, height=300), use_container_width=True)

        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            
            # 排版鎖定：使用純 Markdown 結構避開 CSS 溢出
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            st.write(f"**現價:** {curr}{item['cp']:.2f} | **買入價:** {curr}{item['bp']:.2f}")
            
            profit_color = "red" if p_pct < 0 else "green"
            st.markdown(f"<span style='color:{profit_color}; font-size:18px; font-weight:bold;'>盈虧: {p_pct:.1f}%</span>", unsafe_allow_html=True)
            
            # 分析框：移除所有固定寬度限制，改用內置系統組件
            if item["has_data"]:
                st.success(f"📍 分析：{item['nm']} 支撐 {curr}{item['low']:.2f}，目標 {curr}{item['high']:.2f}")
            else:
                st.warning(f"⚠️ {item['sym']} 目前無法取得實時行情，已顯示持倉基本資料。")
            st.divider()
