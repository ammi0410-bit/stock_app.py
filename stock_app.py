import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. 配置區：在此修改股票名稱與評論 ---
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

# 這裡加入你對大市的總結評論
COMMENTS = {
    "06082.HK": "近期受國產芯片替代潮帶動，走勢偏強，建議回調至支撐位分批吸納。",
    "03888.HK": "軟件板塊整體受壓，需關注業績發布後的指引，短期維持區間震盪。",
    "02888.HK": "息率環境利好銀行股，渣打基本面穩健，適合中長線持有。",
    "DEFAULT": "大市近期波幅較大，建議嚴格執行止盈止蝕策略，保持現金流。"
}

st.set_page_config(page_title="家族辦公室", layout="wide")

# --- CSS 樣式優化 ---
st.markdown("""
    <style>
    .block-container { padding: 2.5rem 0.5rem 1rem !important; }
    .compact-row {
        background-color: #ffffff;
        border-bottom: 1px solid #f0f0f0;
        padding: 12px 5px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .analysis-box {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        border-left: 4px solid #1e1e1e;
        margin-bottom: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

def get_stock_data(symbol):
    search_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="1mo")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            # 這裡可以自定義計算邏輯，或手動輸入
            return {
                "price": last_p, "hist": hist, 
                "support": last_p * 0.90,  # 示意支撐位
                "target": last_p * 1.15    # 示意目標位
            }
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
    data = get_stock_data(row["代號"])
    p = data["price"] if data else row["成本"]
    is_hk = ".HK" in row["代號"]
    total_val += (p * row["數量"]) * (1 if is_hk else 7.8)
    total_cost += (row["成本"] * row["數量"]) * (1 if is_hk else 7.8)
    results.append({"sym": row["代號"], "now": p, "cost": row["成本"], "data": data})

# --- 頂部總覽區 ---
t_diff = (total_val - total_cost) / total_cost * 100
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 25px 15px; border-radius: 12px; text-align: center; margin-bottom: 15px;">
        <div style="color: #ffffff; display: flex; align-items: baseline; justify-content: center; gap: 8px;">
            <span style="color: #bbbbbb; font-size: 14px;">資產總市值</span>
            <span style="font-size: 32px; font-weight: 800; line-height: 1;">${total_val:,.0f}</span>
        </div>
        <div style="color: {'#ff4b4b' if t_diff < 0 else '#00c853'}; font-size: 20px; font-weight: 700; margin-top: 10px;">
            {'+' if t_diff >= 0 else ''}{t_diff:.2f}%
        </div>
    </div>
""", unsafe_allow_html=True)

# --- 列表與詳情分析區 ---
for item in results:
    name = NAMES.get(item["sym"], item["sym"])
    diff = (item["now"] - item["cost"]) / item["cost"] * 100
    color = "#ff4b4b" if diff < 0 else "#00c853"
    unit = "HK$" if ".HK" in item["sym"] else "US$"
    comment = COMMENTS.get(item["sym"], COMMENTS["DEFAULT"])
    
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
    
    with st.expander(f"📊 分析與歷史走勢"):
        if item["data"]:
            # 顯示支撐位與目標位
            st.markdown(f"""
                <div class="analysis-box">
                    <p style='margin:0; font-size:13px; color:#666;'>📍 分析結論</p>
                    <p style='margin:0; font-weight:bold;'>支撐位: {unit}{item['data']['support']:.2f} | 目標位: {unit}{item['data']['target']:.2f}</p>
                </div>
                <div style="padding: 5px 0;">
                    <p style='margin:0; font-size:13px; color:#666;'>📝 大市評論</p>
                    <p style='margin:0; font-size:14px;'>{comment}</p>
                </div>
            """, unsafe_allow_html=True)
            
            # 歷史走勢圖
            fig = go.Figure(data=[go.Candlestick(
                x=item["data"]["hist"].index,
                open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
            )])
            fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
