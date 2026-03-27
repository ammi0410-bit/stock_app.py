import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px
from streamlit_components_auth import st_search # 模擬組件邏輯

# 1. 核心映射表
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 核心引擎：多維度數據校準 ---
def fetch_price_dynamic(symbol):
    try:
        # 混合模式：優先使用 fast_info 減少伺服器負擔
        tk = yf.Ticker(symbol)
        price = tk.fast_info.last_price
        if price and price > 0:
            return price
        # 備援模式：獲取當日收盤
        hist = tk.history(period="1d")
        if not hist.empty:
            return float(hist['Close'].iloc[-1])
    except:
        return None
    return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰", type="password")
    if st.button("啟動系統"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 實時看板", "⚙️ 配置"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全資產深度掃描", use_container_width=True):
        fx = 7.83
        results, total_hkd = [], 0
        
        progress = st.progress(0)
        for i, (_, row) in enumerate(st.session_state.df.iterrows()):
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            # 獲取現價
            real_p = fetch_price_dynamic(sym)
            cp = real_p if real_p else float(row["成本"])
            
            # 獲取分析數據
            low, high, has_data = 0, 0, (real_p is not None)
            try:
                tk = yf.Ticker(sym)
                h = tk.history(period="1mo")
                if not h.empty:
                    low, high = h['Low'].min(), h['High'].max()
            except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": low, "high": high, "val": v_hkd, "has_data": has_data})
            progress.progress((i + 1) / len(st.session_state.df))

        # 頂部統計
        st.metric("💰 資產總市值 (HKD)", f"${total_hkd:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股": x["nm"], "V": x["val"]} for x in results]), values='V', names='股', hole=.4, height=300), use_container_width=True)
        st.divider()

        # 卡片呈現
        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            
            # 強制排版鎖定：使用 HTML Table 確保絕對對齊
            st.markdown(f"""
                <div style="font-family: 'Courier New', monospace; background-color: #f8f9fa; padding: 15px; border-radius: 10px; border: 1px solid #eee;">
                    <table style="width:100%; border:none;">
                        <tr>
                            <td style="font-size: 14px; color: #666;">現價: <b>{curr}{item['cp']:.2f}</b></td>
                            <td style="text-align:right; font-size: 14px; color: #666;">買入: <b>{curr}{item['bp']:.2f}</b></td>
                        </tr>
                    </table>
                    <div style="font-size: 24px; font-weight: bold; color: {p_color}; margin-top: 10px;">
                        盈虧: {'▼' if p_pct < 0 else '▲'} {abs(p_pct):.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 技術分析框
            if item["has_data"] and item["cp"] != item["bp"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; border-left: 5px solid #2e7d32; padding: 12px; margin-top: 10px; border-radius: 5px;">
                    <b style="color: #2e7d32;">📍 技術決策：</b><br>
                    <span style="color: #1b5e20; font-size: 14px;">支撐 <b>{curr}{item['low']:.2f}</b> | 目標 <b>{curr}{item['high']:.2f}</b></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning(f"⚠️ {item['sym']} 伺服器連線受限，請嘗試刷新頁面。")
            st.divider()
