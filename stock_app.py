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
    """抓取最後報價並計算技術位"""
    search_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="5d")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            return {"price": last_p, "hist": hist, "support": last_p * 0.92, "target": last_p * 1.12}
    except:
        return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰解鎖", type="password")
    if st.button("確認進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 初始持倉數據
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

# --- UI 渲染 ---
st.title("🏦 家族辦公室資產監控")

if st.button("🚀 啟動大市總機掃描", use_container_width=True):
    total_val_hkd = 0
    total_cost_hkd = 0
    results = []
    
    with st.spinner('掃描全球數據鏈路中...'):
        for _, row in st.session_state.df.iterrows():
            data = get_clean_price(row["代號"])
            price = data["price"] if data else row["成本"]
            is_hk = ".HK" in row["代號"]
            
            curr_val = (price * row["數量"]) * (1 if is_hk else 7.8)
            curr_cost = (row["成本"] * row["數量"]) * (1 if is_hk else 7.8)
            
            total_val_hkd += curr_val
            total_cost_hkd += curr_cost
            results.append({"sym": row["代號"], "now": price, "cost": row["成本"], "data": data})

    # --- 1. 大市總機 (資產總覽區) ---
    st.markdown("### 📊 資產大市總機")
    c1, c2, c3 = st.columns(3)
    c1.metric("資產總市值 (HKD)", f"${total_val_hkd:,.0f}")
    
    total_diff = (total_val_hkd - total_cost_hkd) / total_cost_hkd * 100
    c2.metric("總盈虧率", f"{total_diff:.2f}%", delta=f"{total_diff:.2f}%")
    
    # 環形分佈圖簡易替代方案
    c3.write(f"今日掃描時間: {pd.Timestamp.now().strftime('%H:%M:%S')}")
    st.divider()

    # --- 2. 個股監控區 ---
    for item in results:
        name = NAMES.get(item["sym"], item["sym"])
        diff = (item["now"] - item["cost"]) / item["cost"] * 100
        color = "#ff4b4b" if diff < 0 else "#00c853"
        unit = "HK$" if ".HK" in item["sym"] else "US$"
        
        # 精簡排版，去除星號
        st.markdown(f"#### 💎 {name} ({item['sym']})")
        
        col_left, col_right = st.columns([2, 1])
        with col_left:
            st.markdown(f"現價: {unit}{item['now']:.2f} | 買入: {unit}{item['cost']:.2f}")
        with col_right:
            st.markdown(f"<div style='font-size:20px; font-weight:bold; color:{color}; text-align:right;'>{'▼' if diff < 0 else '▲'} {abs(diff):.2f}%</div>", unsafe_allow_html=True)
        
        if item["data"]:
            # 分析結論框
            st.info(f"📍 分析：支撐位 {unit}{item['data']['support']:.2f} | 目標位 {unit}{item['data']['target']:.2f}")
            
            with st.expander("📈 點擊展開走勢圖"):
                fig = go.Figure(data=[go.Candlestick(
                    x=item["data"]["hist"].index,
                    open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                    low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
                )])
                fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
        st.divider()
