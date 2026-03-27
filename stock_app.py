import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 核心配置 ---
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

def get_clean_price(symbol):
    """自動修正格式並獲取最後收盤價"""
    # 港股自動去零處理：03888.HK -> 3888.HK
    search_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="5d")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            return {"price": last_p, "hist": hist, "support": last_p * 0.95, "target": last_p * 1.15}
    except:
        return None

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

st.header("💰 家族辦公室資產監控")

if st.button("🚀 啟動全資產深度掃描", use_container_width=True):
    total_val, results = 0, []
    progress = st.progress(0)
    
    for i, (_, row) in enumerate(st.session_state.df.iterrows()):
        data = get_clean_price(row["代號"])
        price = data["price"] if data else row["成本"]
        is_hk = ".HK" in row["代號"]
        val_hkd = (price * row["數量"]) * (1 if is_hk else 7.8)
        total_val += val_hkd
        results.append({"sym": row["代號"], "now": price, "cost": row["成本"], "data": data})
        progress.progress((i + 1) / len(st.session_state.df))

    st.metric("總資產價值 (HKD)", f"${total_val:,.0f}")
    st.divider()

    for item in results:
        name = NAMES.get(item["sym"], item["sym"])
        diff = (item["now"] - item["cost"]) / item["cost"] * 100
        color = "#ff4b4b" if diff < 0 else "#00c853"
        unit = "HK$" if ".HK" in item["sym"] else "US$"
        
        # 修正後的整齊排版
        st.markdown(f"### 💎 {name} ({item['sym']})")
        
        c1, c2 = st.columns(2)
        c1.markdown(f"**現價：** {unit}{item['now']:.2f}  \n**買入：** {unit}{item['cost']:.2f}")
        c2.markdown(f"<div style='font-size:24px; font-weight:bold; color:{color};'>盈虧：{'▲' if diff>=0 else '▼'} {abs(diff):.2f}%</div>", unsafe_allow_html=True)
        
        if item["data"]:
            # 分析框與圖表回歸
            st.success(f"📍 分析結論：支撐位 {unit}{item['data']['support']:.2f} | 目標位 {unit}{item['data']['target']:.2f}")
            with st.expander("📈 點擊查看歷史走勢圖"):
                fig = go.Figure(data=[go.Candlestick(
                    x=item["data"]["hist"].index,
                    open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                    low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
                )])
                fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ 數據鏈路休眠中，目前顯示持倉成本。")
        st.divider()
