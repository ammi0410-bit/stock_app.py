import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.express as px
import time

# 1. 核心映射表
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 核心數據抓取引擎 (港股專用爬蟲) ---
def fetch_hk_price(symbol):
    try:
        code = symbol.split(".")[0].lstrip('0')
        # 爬取 ETNet 實時行情
        url = f"https://www.etnet.com.hk/www/tc/stocks/realtime/quote.php?code={code}"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        price_tag = soup.find('span', {'class': 'Price'})
        if price_tag:
            return float(price_tag.text.strip().replace(',', ''))
    except:
        return None
    return None

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

t1, t2 = st.tabs(["📊 實時決策", "⚙️ 持倉管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全資產深度掃描", use_container_width=True):
        fx = 7.83
        results, total_hkd = [], 0
        progress_bar = st.progress(0)
        
        for i, (idx, row) in enumerate(st.session_state.df.iterrows()):
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            cp, has_data = float(row["成本"]), False
            low, high = cp * 0.98, cp * 1.05 # 預設分析區間
            
            # --- 港股：優先使用爬蟲引擎 ---
            if ".HK" in sym:
                real_p = fetch_hk_price(sym)
                if real_p:
                    cp, has_data = real_p, True
                    low, high = cp * 0.95, cp * 1.10
            
            # --- 美股：使用 yfinance (海外伺服器連線穩定) ---
            if not has_data:
                try:
                    tk = yf.Ticker(sym)
                    h = tk.history(period="5d")
                    if not h.empty:
                        cp = float(h['Close'].iloc[-1])
                        low, high = h['Low'].min(), h['High'].max()
                        has_data = True
                except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": low, "high": high, "val": v_hkd, "has_data": has_data})
            progress_bar.progress((i + 1) / len(st.session_state.df))

        # 頂部儀表盤
        st.metric("💰 資產總市值 (HKD)", f"${total_hkd:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results]), values='價值', names='股票', hole=.4, height=350), use_container_width=True)
        st.divider()

        # 詳細卡片排版
        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            
            # 強制數字對齊與字體加粗
            st.markdown(f"""
                <div style="font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold;">
                    現價: {curr}{item['cp']:.2f} | 買入價: {curr}{item['bp']:.2f}<br>
                    <span style="color: {p_color}; font-size: 18px;">盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}%</span>
                </div>
            """, unsafe_allow_html=True)
            
            # 視覺化分析框：修復內容消失問題
            if item["has_data"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; border-left: 6px solid #2e7d32; padding: 12px; margin-top: 10px; border-radius: 4px;">
                    <strong style="color: #2e7d32;">📍 技術決策：</strong><br>
                    <span style="color: #1b5e20; font-size: 14px;">
                        支撐位在 <b>{curr}{item['low']:.2f}</b>，目標回報看 <b>{curr}{item['high']:.2f}</b>。
                    </span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.error(f"⚠️ {item['sym']} 數據鏈路異常，請檢查網絡。")
            st.divider()
