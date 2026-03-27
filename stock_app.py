import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go
import datetime

# --- 配置區 ---
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

def get_stock_data(symbol):
    """獲取最後收盤價、支撐位與目標位"""
    try:
        tk = yf.Ticker(symbol)
        # 獲取最近兩天的數據以確保拿到最後收盤價
        hist = tk.history(period="5d")
        if not hist.empty:
            last_price = hist['Close'].iloc[-1]
            prev_price = hist['Close'].iloc[-2]
            # 簡單技術分析邏輯
            support = last_price * 0.92
            target = last_price * 1.15
            return {"price": last_price, "support": support, "target": target, "hist": hist}
    except:
        return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰解鎖", type="password")
    if st.button("確認進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 持倉數據
if 'df' not in st.session_state:
    st.session_state.df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })

# --- UI 渲染 ---
st.title("💰 家族辦公室資產監控")

if st.button("🚀 啟動全資產深度掃描", use_container_width=True):
    total_val_hkd = 0
    results = []
    
    for _, row in st.session_state.df.iterrows():
        data = get_stock_data(row["代號"])
        price = data["price"] if data else row["成本"]
        is_hk = ".HK" in row["代號"]
        val = (price * row["數量"]) * (1 if is_hk else 7.8)
        total_val_hkd += val
        results.append({"sym": row["代號"], "now": price, "cost": row["成本"], "data": data})

    # 1. 總資產與環形圖
    st.metric("總資產價值 (HKD)", f"${total_val_hkd:,.0f}")
    
    # 2. 個股詳情卡片
    for item in results:
        name = NAMES.get(item["sym"], item["sym"])
        diff = (item["now"] - item["cost"]) / item["cost"] * 100
        color = "#ff4b4b" if diff < 0 else "#00c853"
        unit = "HK$" if ".HK" in item["sym"] else "US$"
        
        st.markdown(f"### 💎 {item['sym']} | {name}")
        
        # 價格與盈虧列
        col1, col2 = st.columns(2)
        col1.write(f"**現價:** {unit}{item['now']:.2f} | **買入價:** {unit}{item['cost']:.2f}")
        col2.markdown(f"<span style='color:{color}; font-size:20px; font-weight:bold;'>盈虧: {diff:.1f}%</span>", unsafe_allow_html=True)
        
        if item["data"]:
            # 分析結論框
            st.success(f"📍 分析：{name} 支撐 {unit}{item['data']['support']:.2f}，目標 {unit}{item['data']['target']:.2f}")
            
            # 走勢詳情圖表
            with st.expander("📈 查看走勢詳情"):
                fig = go.Figure(data=[go.Candlestick(
                    x=item["data"]["hist"].index,
                    open=item["data"]["hist"]['Open'],
                    high=item["data"]["hist"]['High'],
                    low=item["data"]["hist"]['Low'],
                    close=item["data"]["hist"]['Close']
                )])
                fig.update_layout(height=300, margin=dict(l=0, r=0, t=0, b=0))
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("⚠️ 目前無法取得實時行情，已顯示持倉基本資料。")
        st.divider()
