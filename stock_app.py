import streamlit as st
import pandas as pd
import yfinance as yf
import requests

# --- 核心配置 ---
FINNHUB_KEY = "d72vu4hr01qn7f074rp0d72vu4hr01qn7f074rpg" 
FX_RATE = 7.83 # 預設匯率

NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# 多重格式報價引擎
def get_live_price(symbol):
    if ".HK" in symbol:
        # 嘗試格式 1: 3888.HK | 格式 2: 03888.HK
        symbols_to_try = [symbol.lstrip('0'), symbol]
        for s in symbols_to_try:
            try:
                url = f"https://finnhub.io/api/v1/quote?symbol={s}&token={FINNHUB_KEY}"
                res = requests.get(url, timeout=3).json()
                if res.get('c', 0) > 0: return float(res['c'])
            except: continue
    
    # 備援：yfinance (美股最穩)
    try:
        tk = yf.Ticker(symbol)
        p = tk.fast_info.last_price
        if p and p > 0: return p
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 密鑰解鎖", type="password")
    if st.button("確認進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 實時監控", "⚙️ 資產配置"])

with t2:
    st.info("可以在此修改持倉數量或代號")
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球深度掃描", use_container_width=True):
        results, total_val = [], 0
        p_bar = st.progress(0)
        
        for i, (_, row) in enumerate(st.session_state.df.iterrows()):
            sym = str(row["代號"]).strip().upper()
            p_now = get_live_price(sym)
            
            # 盈虧計算
            cp = p_now if p_now else float(row["成本"])
            is_hk = ".HK" in sym
            val_hkd = (cp * row["數量"]) * (1 if is_hk else FX_RATE)
            total_val += val_hkd
            
            results.append({
                "sym": sym, "now": cp, "cost": float(row["成本"]), 
                "name": NAMES.get(sym, sym), "is_hk": is_hk, "real": (p_now is not None)
            })
            p_bar.progress((i + 1) / len(st.session_state.df))

        st.metric("💰 總資產估值 (HKD)", f"${total_val:,.0f}")
        st.divider()

        for item in results:
            diff = (item["now"] - item["cost"]) / item["cost"] * 100
            color = "#ff4b4b" if diff < 0 else "#00c853"
            unit = "HK$" if item["is_hk"] else "US$"
            
            st.markdown(f"#### 💎 {item['name']} ({item['sym']})")
            # 視覺鎖定：仿彭博終端樣式
            st.markdown(f"""
                <div style="background-color: #f8f9fa; padding: 15px; border-radius: 10px; border-left: 10px solid {color};">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #666;">現價: <b>{unit}{item['now']:.2f}</b></span>
                        <span style="font-size: 24px; font-weight: bold; color: {color};">
                            {'▲' if diff >= 0 else '▼'} {abs(diff):.2f}%
                        </span>
                    </div>
                    <div style="font-size: 12px; color: #999; margin-top: 8px;">
                        買入: {unit}{item['cost']:.2f} | 狀態: {"🟢 連線中" if item['real'] else "🟡 離線/休市"}
                    </div>
                </div>
            """, unsafe_allow_html=True)
            st.divider()
