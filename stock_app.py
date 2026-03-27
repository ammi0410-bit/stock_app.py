import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.express as px

# 1. 名稱對應表
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 核心引擎：解決 IP 封鎖的穩定抓取邏輯 ---
def fetch_realtime_price(symbol):
    try:
        tk = yf.Ticker(symbol)
        # 嘗試獲取最近一個交易日的數據，這比即時快照更穩定突破封鎖
        data = tk.history(period="1d", interval="1m")
        if not data.empty:
            return float(data['Close'].iloc[-1])
        # 備援：獲取最新快照
        return tk.fast_info.last_price
    except:
        return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 密鑰解鎖", type="password")
    if st.button("確認進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 數據初始化
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

t1, t2 = st.tabs(["📊 監控看板", "⚙️ 持倉管理"])

with t2:
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🔄 刷新全球實時行情", use_container_width=True):
        fx = 7.83
        results, total_val = [], 0
        
        progress_bar = st.progress(0)
        for i, (_, row) in enumerate(st.session_state.df.iterrows()):
            sym = str(row["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            p_now = fetch_realtime_price(sym)
            cp = p_now if p_now else float(row["成本"])
            
            # 獲取支撐/阻力參考
            low, high = 0, 0
            try:
                tk = yf.Ticker(sym)
                h = tk.history(period="5d")
                if not h.empty:
                    low, high = h['Low'].min(), h['High'].max()
            except: pass
            
            is_hk = ".HK" in sym
            v_hkd = (cp * row["數量"]) * (1 if is_hk else fx)
            total_val += v_hkd
            results.append({"sym": sym, "cp": cp, "bp": float(row["成本"]), "nm": NAMES.get(sym, sym), "is_hk": is_hk, "low": low, "high": high, "val": v_hkd, "has_data": (p_now is not None)})
            progress_bar.progress((i + 1) / len(st.session_state.df))

        st.metric("💰 總資產估值 (HKD)", f"${total_val:,.0f}")
        st.plotly_chart(px.pie(pd.DataFrame([{"股": x["nm"], "V": x["val"]} for x in results]), values='V', names='股', hole=.4, height=300), use_container_width=True)
        st.divider()

        for item in results:
            curr = "HK$" if item["is_hk"] else "US$"
            diff = (item["cp"] - item["bp"]) / item["bp"] * 100
            color = "#ff4b4b" if diff < 0 else "#00c853"
            
            st.markdown(f"#### 💎 {item['nm']} ({item['sym']})")
            
            # 鋼鐵排版鎖定：HTML 卡片
            st.markdown(f"""
                <div style="font-family: monospace; background-color: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 5px solid {color};">
                    <div style="color: #666; font-size: 13px;">
                        現價 <b>{curr}{item['cp']:.2f}</b> | 成本 <b>{curr}{item['bp']:.2f}</b>
                    </div>
                    <div style="font-size: 22px; font-weight: bold; color: {color}; margin-top: 5px;">
                        盈虧 {'▼' if diff < 0 else '▲'} {abs(diff):.2f}%
                    </div>
                </div>
            """, unsafe_allow_html=True)
            
            if item["has_data"] and item["cp"] != item["bp"]:
                st.markdown(f"""
                <div style="background-color: #e8f5e9; padding: 10px; border-radius: 5px; margin-top: 8px; font-size: 14px;">
                    <span style="color: #2e7d32;">📍 <b>波動範圍：</b></span> 
                    支撐位 {curr}{item['low']:.2f} / 目標位 {curr}{item['high']:.2f}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info(f"⏳ {item['sym']} 數據鏈路獲取中，請稍後刷新。")
            st.divider()
