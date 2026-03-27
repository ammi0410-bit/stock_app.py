import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# 1. 核心名稱映射
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 強化版港股爬蟲引擎 (針對海外伺服器封鎖優化) ---
def get_hk_price_web(symbol):
    try:
        code = symbol.split(".")[0].lstrip('0')
        # 使用 ETNet 作為第一備份源
        url = f"https://www.etnet.com.hk/www/tc/stocks/realtime/quote.php?code={code}"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7'
        }
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        price_span = soup.find('span', {'class': 'Price'})
        if price_span:
            return float(price_span.text.strip().replace(',', ''))
    except:
        return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰", type="password")
    if st.button("啟動系統"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 數據初始化
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 實時決策", "⚙️ 配置管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球數據校準", use_container_width=True):
        fx = 7.83
        results, total_hkd = [], 0
        
        for _, row in st.session_state.df.iterrows():
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            cp, has_data = float(row["成本"]), False
            low, high = 0, 0
            
            # --- 港股邏輯：優先爬蟲，失敗則回退 yfinance ---
            if ".HK" in sym:
                web_p = get_hk_price_web(sym)
                if web_p:
                    cp, has_data = web_p, True
                    low, high = cp * 0.96, cp * 1.08 # 爬蟲源手動計算支撐/目標
            
            if not has_data:
                try:
                    tk = yf.Ticker(sym)
                    h = tk.history(period="1mo")
                    if not h.empty:
                        cp = float(h['Close'].iloc[-1])
                        low, high = h['Low'].min(), h['High'].max()
                        has_data = True
                except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": low, "high": high, "val": v_hkd, "has_data": has_data})

        # 看板顯示
        st.metric("💰 資產總淨值 (HKD)", f"${total_hkd:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results]), values='價值', names='股票', hole=.4, height=350), use_container_width=True)
        st.divider()

        # 詳細卡片顯示
        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            
            # 視覺鎖定：強制等寬字體對齊
            st.markdown(f"""
                <div style="font-family: 'Courier New', monospace; font-size: 16px; font-weight: bold; margin-bottom: 5px;">
                    現價: {curr}{item['cp']:.2f} | 買入價: {curr}{item['bp']:.2f}
                </div>
                <div style="color: {p_color}; font-family: 'Courier New', monospace; font-size: 18px; font-weight: bold; margin-bottom: 15px;">
                    盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.2f}%
                </div>
            """, unsafe_allow_html=True)
            
            if item["has_data"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; border-left: 6px solid #2e7d32; padding: 12px; border-radius: 4px; width: 100%;">
                    <span style="color: #2e7d32; font-weight: bold;">📍 技術分析：</span><br>
                    <span style="color: #1b5e20; font-size: 14px;">支撐位在 <b>{curr}{item['low']:.2f}</b>，目標回報 <b>{curr}{item['high']:.2f}</b>。</span>
                </div>
                """, unsafe_allow_html=True)
            else:
                # 警告框美化
                st.markdown(f"""
                <div style="background-color: #ffebee; border-left: 6px solid #d32f2f; padding: 12px; border-radius: 4px;">
                    <span style="color: #c62828; font-weight: bold;">⚠️ 數據鏈路中斷：</span><br>
                    <span style="color: #c62828; font-size: 13px;">伺服器無法連接港股行情。現價暫按持倉成本計算。</span>
                </div>
                """, unsafe_allow_html=True)
            st.divider()
