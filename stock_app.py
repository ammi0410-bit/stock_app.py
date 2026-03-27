import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import requests
from bs4 import BeautifulSoup

# 1. 核心名稱映射
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室", layout="wide")

# --- 港股專用爬蟲引擎 (避開 API 封鎖) ---
def get_hk_price(symbol):
    try:
        code = symbol.split(".")[0].lstrip('0')
        url = f"https://www.etnet.com.hk/www/tc/stocks/realtime/quote.php?code={code}"
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5)
        soup = BeautifulSoup(r.text, 'html.parser')
        price = soup.find('span', {'class': 'Price'}).text.strip()
        return float(price.replace(',', ''))
    except:
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

t1, t2 = st.tabs(["📊 實時決策", "⚙️ 管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 啟動深度校準", use_container_width=True):
        fx = 7.83
        results, total_hkd = [], 0
        
        for _, row in st.session_state.df.iterrows():
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            cp, y_low, y_high, has_data = float(row["成本"]), 0, 0, False
            
            # --- 雙引擎邏輯 ---
            if ".HK" in sym:
                web_p = get_hk_price(sym)
                if web_p:
                    cp, has_data = web_p, True
                    y_low, y_high = cp * 0.95, cp * 1.05 # 爬蟲版估算支撐目標
            
            if not has_data: # 嘗試 yfinance (美股或爬蟲失敗時)
                try:
                    tk = yf.Ticker(sym)
                    h = tk.history(period="1mo")
                    if not h.empty:
                        cp = float(h['Close'].iloc[-1])
                        y_low, y_high = h['Low'].min(), h['High'].max()
                        has_data = True
                except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": y_low, "high": y_high, "val": v_hkd, "has_data": has_data})

        st.metric("💰 總資產淨值", f"HKD ${total_hkd:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results]), values='價值', names='股票', hole=.4, height=350), use_container_width=True)
        st.divider()

        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            st.markdown(f"""
                <div style="font-family: monospace; font-size: 16px; font-weight: bold; margin-bottom: 5px;">
                    現價: {curr}{item['cp']:.2f} | 買入價: {curr}{item['bp']:.2f}
                </div>
                <div style="color: {p_color}; font-family: monospace; font-size: 18px; font-weight: bold; margin-bottom: 12px;">
                    盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.1f}%
                </div>
            """, unsafe_allow_html=True)
            
            if item["has_data"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; border-left: 6px solid #2e7d32; padding: 12px; border-radius: 4px; line-height: 1.5; width: 100%;">
                    <span style="color: #2e7d32; font-weight: bold;">📍 技術分析：</span><br>
                    <span style="color: #1b5e20; font-size: 14px;">支撐位 <b>{curr}{item['low']:.2f}</b> | 目標價 <b>{curr}{item['high']:.2f}</b></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #fff3e0; border-left: 6px solid #ef6c00; padding: 12px; border-radius: 4px; width: 100%;">
                    <span style="color: #e65100; font-weight: bold;">⚠️ 數據延遲：</span><br>
                    <span style="color: #e65100; font-size: 13px;">伺服器無法連接行情，盈虧計算基於成本。</span>
                </div>
                """, unsafe_allow_html=True)
            st.divider()
