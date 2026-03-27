import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. 配置區 ---
SHEET_ID = "10HANZmUKPzTPJsse_DpPvNhJWSxML1pl_MmUaU5gckE"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
EDIT_URL = "https://docs.google.com/spreadsheets/d/10HANZmUKPzTPJsse_DpPvNhJWSxML1pl_MmUaU5gckE/edit?usp=drivesdk"

NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 2. 身份驗證 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
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
    st.stop()

# --- 3. 數據抓取函數 ---
@st.cache_data(ttl=600)
def load_data_from_sheets():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        st.error("讀取失敗，請確認 Google Sheet 已開啟「知道連結的任何人」檢視權限。")
        return pd.DataFrame(columns=["代號", "成本", "數量"])

# --- 4. CSS 樣式 ---
st.markdown("""
    <style>
    .block-container { padding: 2.5rem 0.5rem 1rem !important; }
    .compact-row { background-color: #ffffff; padding: 12px 8px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; }
    .analysis-section { background-color: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #1e1e1e; margin: 5px 8px 15px 8px; }
    .stExpander { border: none !important; margin: 0 8px !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄 (已移除管理輸入框) ---
with st.sidebar:
    st.header("⚙️ 系統管理")
    st.success("✅ 已連接至 Google Sheets")
    
    # 僅保留更新連結和同步按鈕
    st.markdown(f'### [📝 編輯持倉數據]({EDIT_URL})')
    st.caption("點擊上方連結跳轉至試算表修改數據")
    
    if st.button("🔄 立即同步最新數據", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.write("---")
    if st.button("🚪 登出系統", use_container_width=True):
        st.session_state.auth = False
        st.rerun()

# --- 6. 處理數據 ---
df_data = load_data_from_sheets()

def get_stock_info(symbol):
    sym_str = str(symbol).strip().upper()
    search_sym = sym_str.lstrip('0') if ".HK" in sym_str else sym_str
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="1mo")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            return {"price": last_p, "hist": hist, "support": last_p * 0.92, "target": last_p * 1.12}
    except: return None

total_val_hkd, total_cost_hkd, results = 0, 0, []
for _, row in df_data.iterrows():
    sym = str(row["代號"]).strip()
    data = get_stock_info(sym)
    now_p = data["price"] if data else row["成本"]
    is_hk = ".HK" in sym.upper()
    rate = 1 if is_hk else 7.8
    
    total_val_hkd += (now_p * row["數量"]) * rate
    total_cost_hkd += (row["成本"] * row["數量"]) * rate
    results.append({"sym": sym, "now": now_p, "cost": row["成本"], "data": data})

# --- 7. UI 顯示 ---
profit_pct = (total_val_hkd - total_cost_hkd) / total_cost_hkd * 100 if total_cost_hkd != 0 else 0
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 25px 15px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
        <div style="color: #ffffff; display: flex; align-items: baseline; justify-content: center; gap: 8px;">
            <span style="color: #bbbbbb; font-size: 14px;">資產總市值 (HKD)</span>
            <span style="font-size: 32px; font-weight: 800; line-height: 1;">${total_val_hkd:,.0f}</span>
        </div>
        <div style="color: {'#ff4b4b' if profit_pct < 0 else '#00c853'}; font-size: 20px; font-weight: 700; margin-top: 10px;">
            {profit_pct:+.2f}%
        </div>
    </div>
""", unsafe_allow_html=True)

for item in results:
    name = NAMES.get(item["sym"], item["sym"])
    diff = (item["now"] - item["cost"]) / item["cost"] * 100 if item["cost"] != 0 else 0
    color = "#ff4b4b" if diff < 0 else "#00c853"
    unit = "HK$" if ".HK" in item["sym"].upper() else "US$"
    
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
                <div style="font-size: 17px; font-weight: 800; color: {color};">{diff:+.1f}%</div>
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
        with st.expander("📈 查看走勢圖"):
            fig = go.Figure(data=[go.Candlestick(
                x=item["data"]["hist"].index, open=item["data"]["hist"]['Open'],
                high=item["data"]["hist"]['High'], low=item["data"]["hist"]['Low'],
                close=item["data"]["hist"]['Close']
            )])
            fig.update_layout(height=220, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
