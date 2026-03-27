import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 配置區 ---
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

COMMENTS = {
    "06082.HK": "近期受國產芯片替代潮帶動，走勢偏強，建議回調至支撐位分批吸納。",
    "03888.HK": "軟件板塊整體受壓，需關注業績發布後的指引，短期維持區間震盪。",
    "DEFAULT": "大市波幅較大，建議嚴格執行止盈止蝕策略。"
}

st.set_page_config(page_title="家族辦公室", layout="wide")

# --- CSS 樣式 ---
st.markdown("""
    <style>
    .block-container { padding: 2.5rem 0.5rem 1rem !important; }
    .compact-row {
        background-color: #ffffff;
        padding: 12px 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f0f0f0;
    }
    .analysis-section {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0 15px 0;
    }
    .stExpander { border: none !important; background-color: transparent !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 側邊欄：持倉管理 ---
with st.sidebar:
    st.header("📋 持倉管理")
    # 預設數據
    default_data = "06082.HK,38.2,200\n03888.HK,32.0,400\n02888.HK,182.0,50\n02562.HK,4.267,3000"
    user_csv = st.text_area("格式: 代號,成本,數量 (每行一隻)", default_data, height=300)
    
    # 解析數據
    rows = [r.split(',') for r in user_csv.split('\n') if r]
    df_data = pd.DataFrame(rows, columns=["代號", "成本", "數量"])
    df_data["成本"] = pd.to_numeric(df_data["成本"])
    df_data["數量"] = pd.to_numeric(df_data["數量"])

def get_stock_data(symbol):
    search_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="1mo")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            return {"price": last_p, "hist": hist, "support": last_p * 0.92, "target": last_p * 1.15}
    except: return None

if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔐 解鎖", type="password")
    if st.button("確認"):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 數據計算 ---
total_val, total_cost, results = 0, 0, []
for _, row in df_data.iterrows():
    data = get_stock_data(row["代號"])
    p = data["price"] if data else row["成本"]
    is_hk = ".HK" in row["代號"]
    total_val += (p * row["數量"]) * (1 if is_hk else 7.8)
    total_cost += (row["成本"] * row["數量"]) * (1 if is_hk else 7.8)
    results.append({"sym": row["代號"], "now": p, "cost": row["成本"], "data": data})

# --- 頂部總覽區 ---
t_diff = (total_val - total_cost) / total_cost * 100
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 25px 15px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
        <div style="color: #ffffff; display: flex; align-items: baseline; justify-content: center; gap: 8px;">
            <span style="color: #bbbbbb; font-size: 14px;">資產總市值</span>
            <span style="font-size: 32px; font-weight: 800; line-height: 1;">${total_val:,.0f}</span>
        </div>
        <div style="color: {'#ff4b4b' if t_diff < 0 else '#00c853'}; font-size: 20px; font-weight: 700; margin-top: 10px;">
            {'+' if t_diff >= 0 else ''}{t_diff:.2f}%
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 列表與直接顯示的分析區 ---
for item in results:
    name = NAMES.get(item["sym"], item["sym"])
    diff = (item["now"] - item["cost"]) / item["cost"] * 100
    color = "#ff4b4b" if diff < 0 else "#00c853"
    unit = "HK$" if ".HK" in item["sym"] else "US$"
    comment = COMMENTS.get(item["sym"], COMMENTS["DEFAULT"])
    
    # 1. 股票基本行
    st.markdown(f"""
        <div class="compact-row">
            <div style="flex: 2;">
                <div style="font-size: 16px; font-weight: 700;">{name}</div>
                <div style="font-size: 11px; color: #999;">{item['sym']}</div>
            </div>
            <div style="flex: 2; text-align: center;">
                <div style="font-size: 15px; font-weight: 600;">{unit}{item['now']:.2f}</div>
                <div style="font-size: 10px; color: #888;">成本:{item['cost']:.1f}</div>
            </div>
            <div style="flex: 1.5; text-align: right;">
                <div style="font-size: 17px; font-weight: 800; color: {color};">{'+' if diff >= 0 else ''}{diff:.1f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. 直接顯示分析結論
    if item["data"]:
        st.markdown(f"""
            <div class="analysis-section">
                <p style="margin:0; font-size:12px; color:#666;">📍 分析結論</p>
                <p style="margin:0 0 8px 0; font-weight:bold; font-size:14px;">支撐位: {unit}{item['data']['support']:.2f} | 目標位: {unit}{item['data']['target']:.2f}</p>
                <p style="margin:0; font-size:12px; color:#666;">📝 大市評論</p>
                <p style="margin:0; font-size:13px; line-height:1.4;">{comment}</p>
            </div>
        """, unsafe_allow_html=True)
        
        # 3. 唯獨 K 線圖表預設隱藏
        with st.expander("📈 查看走勢圖"):
            fig = go.Figure(data=[go.Candlestick(
                x=item["data"]["hist"].index,
                open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
            )])
            fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
