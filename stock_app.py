import streamlit as st
import pandas as pd
import yfinance as yf
import requests
from bs4 import BeautifulSoup
import plotly.express as px

# 1. 名稱對應表
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 終極引擎：Google Finance 全球搜尋爬蟲 ---
def get_global_price(symbol):
    try:
        # 模擬 Google 搜尋行為，這是最難被封鎖的路徑
        query = f"{symbol} price"
        url = f"https://www.google.com/search?q={query}&hl=en"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        # 尋找 Google Finance 的實時報價區塊
        for el in soup.find_all('span'):
            txt = el.text.replace(',', '')
            try:
                # 判斷是否為數字且不等於持倉成本（避免假數據）
                val = float(txt)
                if val > 0: return val
            except: continue
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

t1, t2 = st.tabs(["📊 實時看板", "⚙️ 管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全資產深度掃描", use_container_width=True):
        fx = 7.83
        results, total_hkd = [], 0
        
        bar = st.progress(0)
        for i, (_, row) in enumerate(st.session_state.df.iterrows()):
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            cp, has_data = float(row["成本"]), False
            low, high = 0, 0
            
            # --- 優先使用 Google 搜尋引擎獲取現價 ---
            real_p = get_global_price(sym)
            if real_p and real_p != cp:
                cp, has_data = real_p, True
            
            # --- 若 Google 失敗，回退至 yfinance 獲取分析數據 ---
            try:
                tk = yf.Ticker(sym)
                if not has_data:
                    h = tk.history(period="1d")
                    if not h.empty:
                        cp = float(h['Close'].iloc[-1])
                        has_data = True
                # 獲取支撐/目標位
                hist = tk.history(period="1mo")
                if not hist.empty:
                    low, high = hist['Low'].min(), hist['High'].max()
            except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_hkd += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": low, "high": high, "val": v_hkd, "has_data": has_data})
            bar.progress((i + 1) / len(st.session_state.df))

        # 頂部儀表盤
        st.metric("💰 全球資產淨值 (HKD)", f"${total_hkd:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股票": x["nm"], "價值": x["val"]} for x in results]), values='價值', names='股票', hole=.4, height=300), use_container_width=True)
        st.divider()

        # 詳細卡片
        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            p_pct = (item["cp"] - item["bp"]) / item["bp"] * 100
            p_color = "#ff4b4b" if p_pct < 0 else "#00c853"
            
            st.markdown(f"### 💎 {item['sym']} | {item['nm']}")
            
            # 視覺鎖定：強制背景塊與等寬字體
            st.markdown(f"""
                <div style="font-family: 'Courier New', monospace; background-color: #f1f3f4; padding: 12px; border-radius: 8px; border: 1px solid #ddd;">
                    <div style="font-size: 16px; color: #555;">現價: <b>{curr}{item['cp']:.2f}</b> | 買入價: <b>{curr}{item['bp']:.2f}</b></div>
                    <div style="font-size: 22px; font-weight: bold; color: {p_color}; margin-top: 5px;">
                        盈虧: {'🔴' if p_pct < 0 else '🟢'} {p_pct:.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            # 分析框鎖定
            if item["has_data"] and item["cp"] != item["bp"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; border-left: 6px solid #2e7d32; padding: 12px; margin-top: 10px; border-radius: 4px;">
                    <b style="color: #2e7d32;">📍 技術分析：</b><br>
                    <span style="color: #1b5e20; font-size: 14px;">支撐位 <b>{curr}{item['low']:.2f}</b> | 目標價 <b>{curr}{item['high']:.2f}</b></span>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="background-color: #fff3e0; border-left: 6px solid #ef6c00; padding: 12px; margin-top: 10px; border-radius: 4px;">
                    <span style="color: #e65100; font-size: 13px;"><b>⏳ 數據掃描中：</b> 目前顯示持倉基本資料。</span>
                </div>
                """, unsafe_allow_html=True)
            st.divider()
