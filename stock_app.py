import streamlit as st
import pandas as pd
import yfinance as yf
import plotly.graph_objects as go

# --- 1. 配置區 ---
SHEET_ID = "10HANZmUKPzTPJsse_DpPvNhJWSxML1pl_MmUaU5gckE"
SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv"
EDIT_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/edit"

NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子",
    "GOOG": "谷歌-C", "KO": "可口可樂", "RBLX": "Roblox", "TEM": "Tempus AI"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 2. 身份驗證 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("# 🔐 家族辦公室")
        pwd = st.text_input("請輸入訪問密碼", type="password")
        if st.button("登入系統", use_container_width=True):
            if pwd == "13579":
                st.session_state.auth = True; st.rerun()
    st.stop()

# --- 3. 數據抓取與清洗 (關鍵修復點) ---
@st.cache_data(ttl=300)
def load_data_from_sheets():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns] # 去除標題空格
        
        # 強制轉換數據類型，報錯的改為 0
        df["成本"] = pd.to_numeric(df["成本"], errors='coerce').fillna(0)
        df["數量"] = pd.to_numeric(df["數量"], errors='coerce').fillna(0)
        df["代號"] = df["代號"].astype(str).str.strip()
        
        return df
    except:
        st.error("❌ Google Sheet 讀取失敗，請檢查標題是否為：代號、成本、數量")
        return pd.DataFrame(columns=["代號", "成本", "數量"])

# --- 4. CSS ---
st.markdown("""
    <style>
    .block-container { padding: 2.5rem 0.5rem 1rem !important; }
    .compact-row { background-color: #ffffff; padding: 12px 8px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f0f0f0; }
    .analysis-section { background-color: #f8f9fa; padding: 12px; border-radius: 8px; border-left: 4px solid #1e1e1e; margin: 5px 8px 15px 8px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 系統管理")
    st.markdown(f'### [📝 編輯持倉數據]({EDIT_URL})')
    if st.button("🔄 同步最新數據", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.write("---")
    if st.button("🚪 登出"): st.session_state.auth = False; st.rerun()

# --- 6. 核心處理 ---
df_data = load_data_from_sheets()

def get_stock_info(symbol):
    search_sym = symbol.lstrip('0') if ".HK" in symbol.upper() else symbol
    try:
        tk = yf.Ticker(search_sym)
        hist = tk.history(period="5d")
        if not hist.empty:
            last_p = hist['Close'].iloc[-1]
            return {"price": last_p, "hist": hist, "support": last_p * 0.92, "target": last_p * 1.12}
    except: return None

total_val_hkd, total_cost_hkd, results = 0, 0, []

for _, row in df_data.iterrows():
    sym = str(row["代號"])
    if not sym or sym == 'nan': continue
    
    data = get_stock_info(sym)
    # 確保 now_p 是浮點數
    now_p = float(data["price"]) if data else float(row["成本"])
    cost_p = float(row["成本"])
    qty = float(row["數量"])
    
    rate = 1 if ".HK" in sym.upper() else 7.8
    total_val_hkd += (now_p * qty) * rate
    total_cost_hkd += (cost_p * qty) * rate
    results.append({"sym": sym, "now": now_p, "cost": cost_p, "data": data})

# --- 7. UI 渲染 ---
profit_pct = (total_val_hkd - total_cost_hkd) / total_cost_hkd * 100 if total_cost_hkd != 0 else 0
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 25px 15px; border-radius: 12px; text-align: center; margin-bottom: 20px;">
        <div style="color: #ffffff; display: flex; align-items: baseline; justify-content: center; gap: 8px;">
            <span style="color: #bbbbbb; font-size: 14px;">資產總市值 (HKD)</span>
            <span style="font-size: 32px; font-weight: 800;">${total_val_hkd:,.0f}</span>
        </div>
        <div style="color: {'#ff4b4b' if profit_pct < 0 else '#00c853'}; font-size: 20px; font-weight: 700;">{profit_pct:+.2f}%</div>
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
        with st.expander(f"📍 分析：支撐 {unit}{item['data']['support']:.1f} | 目標 {unit}{item['data']['target']:.1f}"):
            fig = go.Figure(data=[go.Candlestick(x=item["data"]["hist"].index, open=item["data"]["hist"]['Open'], high=item["data"]["hist"]['High'], low=item["data"]["hist"]['Low'], close=item["data"]["hist"]['Close'])])
            fig.update_layout(height=200, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
