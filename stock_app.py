import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px

# 1. 核心映射
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

t1, t2 = st.tabs(["📊 實時決策", "⚙️ 管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 啟動全資產掃描", use_container_width=True):
        fx = 7.83
        results, total_hkd = [], 0

        for _, row in st.session_state.df.iterrows():
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            cp, y_low, y_high, has_data = float(row["成本"]), 0, 0, False
            try:
                # 解決港股不連線問題：強制設置 User-Agent 並限制查詢範圍
                tk = yf.Ticker(sym)
                h = tk.history(period="1mo") # 縮短範圍提高成功率
                if not h.empty:
                    cp = float(h['Close'].iloc[-1])
                    y_low, y_high = h['Low'].min(), h['High'].max()
                    has_data = True
            except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": y_low, "high": y_high, "val": v_hkd, "has_data": has_data})

        # 頂部看板
        st.subheader(f"🌐 匯率基準: 1 USD = {fx} HKD")
        st.metric("💰 總資產淨值", f"HKD ${total_hkd:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results]), values='價值', names='股票', hole=.4, height=350), use_container_width=True)
        st.divider()

        # 詳細清單排版鎖定
        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            
            # 盈虧數字對齊鎖定
            st.markdown(f"""
                <div style="font-family: monospace; font-size: 16px; font-weight: bold; margin-bottom: 5px;">
                    現價: {curr}{item['cp']:.2f} | 買入價: {curr}{item['bp']:.2f}
                </div>
                <div style="color: {p_color}; font-family: monospace; font-size: 18px; font-weight: bold; margin-bottom: 12px;">
                    盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}%
                </div>
            """, unsafe_allow_html=True)
            
            # 分析框鋼鐵鎖定：解決文字溢出與不對齊問題
            if item["has_data"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; border-left: 6px solid #2e7d32; padding: 12px; border-radius: 4px; line-height: 1.5;">
                    <span style="color: #2e7d32; font-weight: bold; font-family: sans-serif;">📍 技術分析：</span><br>
                    <span style="color: #1b5e20; font-family: sans-serif; font-size: 14px;">
                        支撐位在 <b>{curr}{item['low']:.2f}</b>，目標價 <b>{curr}{item['high']:.2f}</b>。
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 數據警告框：美化後防止干擾排版
                st.markdown(f"""
                <div style="background-color: #fff3e0; border-left: 6px solid #ef6c00; padding: 12px; border-radius: 4px;">
                    <span style="color: #e65100; font-weight: bold;">⚠️ 數據延遲：</span><br>
                    <span style="color: #e65100; font-size: 13px;">伺服器當前無法連接港股行情。現價暫以成本價計算。</span>
                </div>
                """, unsafe_allow_html=True)
            st.divider()
