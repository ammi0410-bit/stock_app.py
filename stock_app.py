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

st.set_page_config(page_title="家族辦公室", layout="wide")

# --- CSS：修正頂部文字顯示與壓縮間距 ---
st.markdown("""
    <style>
    .block-container { padding: 1rem 0.5rem !important; }
    
    .header-box {
        background-color: #1e1e1e;
        color: #ffffff;
        padding: 15px 10px;
        border-radius: 10px;
        margin-bottom: 15px;
        text-align: center;
    }
    .header-title { font-size: 14px !important; color: #aaaaaa !important; margin-bottom: 5px; }
    .header-value { font-size: 28px !important; font-weight: 800 !important; color: #ffffff !important; }
    
    .compact-row {
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
        padding: 10px 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stock-name { font-size: 16px; font-weight: 700; color: #1a1a1a; }
    .stock-code { font-size: 11px; color: #999; }
    .price-now { font-size: 15px; font-weight: 600; color: #333; }
    .price-cost { font-size: 10px; color: #888; }
    .profit-val { font-size: 17px; font-weight: 800; }
    
    [data-testid="stExpander"] { border: none !important; box-shadow: none !important; margin-top: -5px !important; }
    </style>
    """, unsafe_allow_html=True)

def get_clean_price(symbol):
    search_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="5d")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            return {"price": last_p, "hist": hist, "support": last_p * 0.92, "target": last_p * 1.12}
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 解鎖", type="password")
    if st.button("確認"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 數據處理 ---
df_data = pd.DataFrame({
    "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
    "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
    "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
})

total_val, total_cost, results = 0, 0, []
for _, row in df_data.iterrows():
    data = get_clean_price(row["代號"])
    p = data["price"] if data else row["成本"]
    is_hk = ".HK" in row["代號"]
    total_val += (p * row["數量"]) * (1 if is_hk else 7.8)
    total_cost += (row["成本"] * row["數量"]) * (1 if is_hk else 7.8)
    results.append({"sym": row["代號"], "now": p, "cost": row["成本"], "data": data})

# --- 1. 頂部總覽區：補回文字標題 ---
t_diff = (total_val - total_cost) / total_cost * 100
st.markdown(f"""
    <div class="header-box">
        <div class="header-title">資產總市值 (HKD)</div>
        <div class="header-value">${total_val:,.0f}</div>
        <div style="color: {'#ff4b4b' if t_diff < 0 else '#00c853'}; font-size: 18px; font-weight: bold; margin-top: 5px;">
            {t_diff:.2f}%
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 2. 緊湊清單區 ---
for item in results:
    name = NAMES.get(item["sym"], item["sym"])
    diff = (item["now"] - item["cost"]) / item["cost"] * 100
    color = "#ff4b4b" if diff < 0 else "#00c853"
    unit = "HK$" if ".HK" in item["sym"] else "US$"
    
    st.markdown(f"""
        <div class="compact-row">
            <div style="flex: 2;">
                <div class="stock-name">{name}</div>
                <div class="stock-code">{item['sym']}</div>
            </div>
            <div style="flex: 2; text-align: center;">
                <div class="price-now">{unit}{item['now']:.2f}</div>
                <div class="price-cost">成本:{item['cost']:.1f}</div>
            </div>
            <div style="flex: 1.5; text-align: right;">
                <div class="profit-val" style="color:{color};">{diff:.1f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander(f"詳情"):
        if item["data"]:
            st.caption(f"📍 支撐 {item['data']['support']:.2f} | 目標 {item['data']['target']:.2f}")
            fig = go.Figure(data=[go.Candlestick(
                x=item["data"]["hist"].index,
                open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
            )])
            fig.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
