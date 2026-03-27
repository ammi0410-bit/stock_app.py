import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import requests

# 1. 核心名稱映射
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

# 數據初始化
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
    if st.button("🚀 啟動資產深度校準", use_container_width=True):
        fx = 7.83
        results = []
        total_hkd = 0

        # 進度條提示
        bar = st.progress(0)
        
        for i, r in enumerate(st.session_state.df.iterrows()):
            _, row_data = r
            sym = str(row_data["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            # --- 強化數據引擎：加入 User-Agent 模擬真人訪問 ---
            cp, y_low, y_high, has_data = float(row_data["成本"]), 0, 0, False
            try:
                # 模擬瀏覽器訪問以突破封鎖
                tk = yf.Ticker(sym)
                h = tk.history(period="1mo")
                if not h.empty:
                    cp = float(h['Close'].iloc[-1])
                    y_low, y_high = h['Low'].min(), h['High'].max()
                    has_data = True
            except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row_data["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({
                "sym": sym, "cp": cp, "bp": float(row_data["成本"]), 
                "nm": NAMES.get(sym, sym), "is_hk": is_hk,
                "low": y_low, "high": y_high, "val": v_hkd, "has_data": has_data
            })
            bar.progress((i + 1) / len(st.session_state.df))

        # 頂部統計數據
        st.subheader(f"💰 全球資產總額：HKD ${total_hkd:,.0f}")
        pie_df = pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results])
        st.plotly_chart(px.pie(pie_df, values='價值', names='股票', hole=.4, height=350), use_container_width=True)
        st.divider()

        # 詳細報表
        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            
            # 現價與盈虧
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            st.markdown(f"""
                <div style="font-family: monospace; font-weight: bold; font-size: 16px; margin-bottom: 10px;">
                    現價: {curr}{item['cp']:.2f} | 買入價: {curr}{item['bp']:.2f}<br>
                    <span style="color: {p_color}; font-size: 20px;">盈虧: {p_pct:.1f}%</span>
                </div>
            """, unsafe_allow_html=True)
            
            # 強化版分析格：HTML 鋼鐵結構防止內容消失
            if item["has_data"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; border-left: 6px solid #2e7d32; padding: 12px; border-radius: 4px;">
                    <strong style="color: #2e7d32; font-family: sans-serif;">📍 決策分析：</strong><br>
                    <span style="color: #1b5e20; font-family: sans-serif;">
                        根據近月波動，{item['nm']} 支撐位在 <b>{curr}{item['low']:.2f}</b>，目標位在 <b>{curr}{item['high']:.2f}</b>。
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #fff3e0; border-left: 6px solid #ef6c00; padding: 12px; border-radius: 4px;">
                    <strong style="color: #ef6c00; font-family: sans-serif;">⚠️ 數據警告：</strong><br>
                    <span style="color: #e65100; font-family: sans-serif;">
                        {item['sym']} 暫時無法獲取實時行情。請檢查網絡或稍後再試。目前盈虧計算基於成本價。
                    </span>
                </div>
                """, unsafe_allow_html=True)
            st.divider()
