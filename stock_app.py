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
    search_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="5d")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            # 自定義支撐位與目標位邏輯
            return {"price": last_p, "hist": hist, "support": last_p * 0.92, "target": last_p * 1.12}
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 家族密鑰解鎖", type="password")
    if st.button("確認進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 頁面標題
st.title("🏦 家族辦公室資產監控")

# --- 功能控制開關 ---
col_set1, col_set2 = st.columns(2)
show_charts = col_set1.toggle("📊 開啟走勢圖模式", value=False)
run_scan = st.button("🚀 啟動全資產總機掃描", use_container_width=True)

if run_scan:
    total_val, total_cost, results = 0, 0, []
    
    for _, row in pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    }).iterrows():
        data = get_clean_price(row["代號"])
        p = data["price"] if data else row["成本"]
        is_hk = ".HK" in row["代號"]
        total_val += (p * row["數量"]) * (1 if is_hk else 7.8)
        total_cost += (row["成本"] * row["數量"]) * (1 if is_hk else 7.8)
        results.append({"sym": row["代號"], "now": p, "cost": row["成本"], "data": data})

    # 1. 大市總機板面
    st.subheader("📊 大市總機概覽")
    m1, m2 = st.columns(2)
    m1.metric("資產總市值 (HKD)", f"${total_val:,.0f}")
    t_diff = (total_val - total_cost) / total_cost * 100
    m2.metric("總盈虧率", f"{t_diff:.2f}%", delta=f"{t_diff:.2f}%")
    st.divider()

    # 2. 個股明細排版優化
    for item in results:
        name = NAMES.get(item["sym"], item["sym"])
        diff = (item["now"] - item["cost"]) / item["cost"] * 100
        color = "#ff4b4b" if diff < 0 else "#00c853"
        unit = "HK$" if ".HK" in item["sym"] else "US$"
        
        # 💎 標題區
        st.markdown(f"#### 💎 {name} ({item['sym']})")
        
        # 價格區：分兩行顯示避免重疊
        p1, p2 = st.columns([1, 1])
        p1.write(f"**現價：** {unit}{item['now']:.2f}")
        p1.write(f"**成本：** {unit}{item['cost']:.2f}")
        p2.markdown(f"<div style='font-size:26px; font-weight:bold; color:{color}; text-align:right; padding-top:10px;'>{'▼' if diff<0 else '▲'} {abs(diff):.2f}%</div>", unsafe_allow_html=True)
        
        if item["data"]:
            # 分析結論
            st.info(f"📍 分析：支撐 {unit}{item['data']['support']:.2f} | 目標 {unit}{item['data']['target']:.2f}")
            
            # 走勢圖選擇性顯示
            if show_charts:
                fig = go.Figure(data=[go.Candlestick(
                    x=item["data"]["hist"].index,
                    open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                    low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
                )])
                fig.update_layout(height=250, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
                st.plotly_chart(fig, use_container_width=True)
        st.divider()
