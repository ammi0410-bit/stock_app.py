import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import plotly.express as px

# --- 自動配置區 ---
FINNHUB_KEY = "d72vu4hr01qn7f074rp0d72vu4hr01qn7f074rpg" 

NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

def get_price(symbol):
    # Finnhub 港股格式修正：03888.HK -> 3888.HK
    fin_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={fin_sym}&token={FINNHUB_KEY}"
        res = requests.get(url, timeout=5).json()
        if 'c' in res and res['c'] > 0: return float(res['c'])
    except: pass
    
    # 備援：yfinance (美股依然穩定)
    try:
        tk = yf.Ticker(symbol)
        return tk.fast_info.last_price
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰解鎖", type="password")
    if st.button("確認進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 實時監控", "⚙️ 持倉配置"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球行情深度刷新", use_container_width=True):
        fx, results, total_val = 7.83, [], 0
        progress = st.progress(0)
        
        for i, (_, row) in enumerate(st.session_state.df.iterrows()):
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            p_now = get_price(sym)
            cp = p_now if p_now else float(row["成本"])
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_val += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "has_data": (p_now is not None)})
            progress.progress((i + 1) / len(st.session_state.df))

        st.metric("💰 總資產市值 (HKD)", f"${total_val:,.0f}")
        st.divider()

        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            diff = (item["cp"] - item["bp"]) / item["bp"] * 100
            color = "#ff4b4b" if diff < 0 else "#00c853"
            
            st.markdown(f"#### 💎 {item['nm']} ({item['sym']})")
            # 視覺鋼鐵對齊卡片
            st.markdown(f"""
                <div style="font-family: 'Courier New', monospace; background-color: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 6px solid {color}; shadow: 2px 2px 5px #ddd;">
                    <div style="color: #666; font-size: 13px;">
                        現價 <b>{curr}{item['cp']:.2f}</b> | 買入 <b>{curr}{item['bp']:.2f}</b>
                    </div>
                    <div style="font-size: 24px; font-weight: bold; color: {color}; margin-top: 5px;">
                        {'▼' if diff < 0 else '▲'} {abs(diff):.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if not item["has_data"]:
                st.caption("⚠️ 鏈路繁忙，目前顯示持倉基本數據。")
            st.divider()
