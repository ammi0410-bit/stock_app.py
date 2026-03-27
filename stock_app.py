import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. 名稱與評論配置 ---
NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 2. 身份驗證 (放在最前面，確保攔截所有內容) ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    # 居中顯示登入界面
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("# 🔐 家族辦公室")
        pwd = st.text_input("請輸入訪問密碼", type="password")
        if st.button("登入系統", use_container_width=True):
            if pwd == "13579":
                st.session_state.auth = True
                st.rerun()
            else:
                st.error("密碼錯誤")
    st.stop()  # 徹底停止後續所有代碼執行，包括側邊欄

# --- 3. 進入系統後的 CSS 樣式 ---
st.markdown("""
    <style>
    .block-container { padding: 2.5rem 0.5rem 1rem !important; }
    .compact-row {
        background-color: #ffffff;
        padding: 12px 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #f0f0f0;
    }
    .analysis-section {
        background-color: #f8f9fa;
        padding: 12px;
        border-radius: 8px;
        border-left: 4px solid #1e1e1e;
        margin: 5px 8px 15px 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. 持倉管理 (只有登入後才會執行到這裡) ---
with st.sidebar:
    st.header("📋 持倉管理")
    full_inventory = """06082.HK,38.2,200
03888.HK,32.0,400
02888.HK,182.0,50
02562.HK,4.267,3000
02172.HK,13.0,1000
02050.HK,39.8,300
01810.HK,34.75,400
01530.HK,28.54,500
00699.HK,19.0,1000
GOOG,319.58,12
KO,52.98,1
RBLX,121.558,52
TEM,77.924,170"""
    
    user_csv = st.text_area("編輯持倉 (代號,成本,數量)", full_inventory, height=400)
    
    # 解析數據
    rows = [r.split(',') for r in user_csv.split('\n') if r]
    df_data = pd.DataFrame(rows, columns=["代號", "成本", "數量"])
    df_data["成本"] = pd.to_numeric(df_data["成本"])
    df_data["數量"] = pd.to_numeric(df_data["數量"])
    
    if st.button("登出系統"):
        st.session_state.auth = False
        st.rerun()

# --- 5. 數據處理與顯示邏輯 ---
def get_stock_data(symbol):
    search_sym = symbol.lstrip('0') if ".HK" in symbol else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="1mo")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            return {"price": last_p, "hist": hist, "support": last_p * 0.92, "target": last_p * 1.12}
    except: return None

total_val_hkd, total_cost_hkd, results = 0, 0, []
for _, row in df_data.iterrows():
    data = get_stock_data(row["代號"])
    now_p = data["price"] if data else row["成本"]
    is_hk = ".HK" in row["代號"]
    rate = 1 if is_hk else 7.8
    total_val_hkd += (now_p * row["數量"]) * rate
    total_cost_hkd += (row["成本"] * row["數量"]) * rate
    results.append({"sym": row["代號"], "now": now_p, "cost": row["成本"], "data": data})

# --- 6. 頁面渲染 (總市值 + 列表) ---
profit_pct = (total_val_hkd - total_cost_hkd) / total_cost_hkd * 100
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 25px 15px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
        <div style="color: #ffffff; display: flex; align-items: baseline; justify-content: center; gap: 8px;">
            <span style="color: #bbbbbb; font-size: 14px;">資產總市值 (HKD)</span>
            <span style="font-size: 32px; font-weight: 800; line-height: 1;">${total_val_hkd:,.0f}</span>
        </div>
        <div style="color: {'#ff4b4b' if profit_pct < 0 else '#00c853'}; font-size: 20px; font-weight: 700; margin-top: 10px;">
            {'+' if profit_pct >= 0 else ''}{profit_pct:.2f}%
        </div>
    </div>
""", unsafe_allow_html=True)

for item in results:
    name = NAMES.get(item["sym"], item["sym"])
    diff = (item["now"] - item["cost"]) / item["cost"] * 100
    color = "#ff4b4b" if diff < 0 else "#00c853"
    unit = "HK$" if ".HK" in item["sym"] else "US$"
    
    st.markdown(f"""
        <div class="compact-row">
            <div style="flex: 2.2;">
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
    
    if item["data"]:
        st.markdown(f"""
            <div class="analysis-section">
                <p style="margin:0; font-size:12px; color:#666;">📍 分析結論</p>
                <p style="margin:0; font-weight:bold; font-size:14px;">支撐: {unit}{item['data']['support']:.2f} | 目標: {unit}{item['data']['target']:.2f}</p>
            </div>
        """, unsafe_allow_html=True)
        with st.expander("📈 展開查看走勢圖"):
            fig = go.Figure(data=[go.Candlestick(
                x=item["data"]["hist"].index,
                open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'],
                low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close']
            )])
            fig.update_layout(height=220, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
