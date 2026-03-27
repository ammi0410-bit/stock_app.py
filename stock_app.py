import streamlit as st
import pandas as pd
import yfinance as yf
import requests
import time

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
    # 1. 嘗試 Finnhub (專治港股封鎖)
    try:
        fin_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
        url = f"https://finnhub.io/api/v1/quote?symbol={fin_sym}&token={FINNHUB_KEY}"
        res = requests.get(url, timeout=3).json()
        if 'c' in res and res['c'] > 0: return float(res['c'])
    except: pass
    
    # 2. 備援：yfinance 快速抓取
    try:
        tk = yf.Ticker(symbol)
        p = tk.fast_info.last_price
        if p and p > 0: return p
    except: pass
    
    return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰解鎖", type="password")
    if st.button("確認進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 預設數據
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
    if st.button("🚀 點擊刷新實時行情", use_container_width=True):
        fx, results, total_val = 7.83, [], 0
        progress = st.progress(0)
        
        for i, (_, row) in enumerate(st.session_state.df.iterrows()):
            sym = str(row["代號"]).strip().upper()
            p_now = get_price(sym)
            cp = p_now if p_now else float(row["成本"])
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_val += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "real": (p_now is not None)})
            progress.progress((i + 1) / len(st.session_state.df))

        st.metric("💰 總資產市值 (HKD)", f"${total_val:,.0f}")
        st.divider()

        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            diff = (item["cp"] - item["bp"]) / item["bp"] * 100
            color = "#ff4b4b" if diff < 0 else "#00c853"
            
            st.markdown(f"#### 💎 {item['nm']} ({item['sym']})")
            # 視覺鎖定：強化盈虧顯示
            st.markdown(f"""
                <div style="font-family: sans-serif; background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 8px solid {color}; margin-bottom: 5px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <span style="color: #666; font-size: 14px;">現價</span><br>
                            <span style="font-size: 20px; font-weight: bold;">{curr}{item['cp']:.2f}</span>
                        </div>
                        <div style="text-align: right;">
                            <span style="color: #666; font-size: 14px;">盈虧率</span><br>
                            <span style="font-size: 24px; font-weight: 800; color: {color};">
                                {'▼' if diff < 0 else '▲'} {abs(diff):.2f}%
                            </span>
                        </div>
                    </div>
                    <div style="margin-top: 10px; border-top: 1px solid #eee; pt: 5px; font-size: 12px; color: #999;">
                        買入成本: {curr}{item['bp']:.2f} | 狀態: {"🟢 實時連線" if item['real'] else "🟡 顯示成本"}
                    </div>
                </div>
            """, unsafe_allow_html=True)
