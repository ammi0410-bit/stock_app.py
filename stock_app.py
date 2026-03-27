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

# --- CSS：極致壓縮排版 ---
st.markdown("""
    <style>
    /* 移除 Streamlit 預設的多餘間距 */
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    div[data-testid="stVerticalBlock"] > div { padding: 2px 0px !important; }
    
    /* 緊湊型列表樣式 */
    .compact-row {
        background-color: #ffffff;
        border-bottom: 1px solid #eee;
        padding: 8px 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .stock-info { flex: 2; }
    .stock-name { font-size: 16px !important; font-weight: 700; color: #1a1a1a; margin-bottom: -2px; }
    .stock-code { font-size: 11px; color: #888; }
    .price-group { flex: 2; text-align: center; line-height: 1.2; }
    .price-now { font-size: 15px; font-weight: 600; color: #000; }
    .price-cost { font-size: 11px; color: #777; }
    .profit-group { flex: 1.5; text-align: right; }
    .profit-val { font-size: 18px !important; font-weight: 800 !important; }
    
    /* 隱藏預設 divider 的間距 */
    hr { margin: 0.5rem 0px !important; }
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
    pwd = st.text_input("🔐 密鑰", type="password")
    if st.button("進入"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 頂部總機 (極簡化) ---
total_val, total_cost, results = 0, 0, []
df_data = pd.DataFrame({
    "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
    "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
    "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
})

# 自動啟動掃描 (不需手動按鈕以節省空間)
for _, row in df_data.iterrows():
    data = get_clean_price(row["代號"])
    p = data["price"] if data else row["成本"]
    is_hk = ".HK" in row["代號"]
    total_val += (p * row["數量"]) * (1 if is_hk else 7.8)
    total_cost += (row["成本"] * row["數量"]) * (1 if is_hk else 7.8)
    results.append({"sym": row["代號"], "now": p, "cost": row["成本"], "data": data})

t_diff = (total_val - total_cost) / total_cost * 100
st.markdown(f"### 🏦 總市值: **HK${total_val:,.0f}** ({'+' if t_diff>=0 else ''}{t_diff:.2f}%)")
st.divider()

# --- 列表清單 ---
for item in results:
    name = NAMES.get(item["sym"], item["sym"])
    diff = (item["now"] - item["cost"]) / item["cost"] * 100
    color = "#ff4b4b" if diff < 0 else "#00c853"
    unit = "HK$" if ".HK" in item["sym"] else "US$"
    
    # 採用 Flexbox 水平排列，節省垂直空間
    st.markdown(f"""
        <div class="compact-row">
            <div class="stock-info">
                <div class="stock-name">{name}</div>
                <div class="stock-code">{item['sym']}</div>
            </div>
            <div class="price-group">
                <div class="price-now">{unit}{item['now']:.2f}</div>
                <div class="price-cost">成本:{item['cost']:.1f}</div>
            </div>
            <div class="profit-group">
                <div class="profit-val" style="color:{color};">{'+' if diff>=0 else ''}{diff:.1f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 只有展開才顯示分析與圖表，預設隱藏以節省空間
    with st.expander(f"查看分析 {item['sym']}"):
        if item["data"]:
            st.caption(f"支撐 {item['data']['support']:.2f} | 目標 {item['data']['target']:.2f}")
            fig = go.Figure(data=[go.Candlestick(
                x=item["data"]["hist"].index,
                open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
            )])
            fig.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
