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

COMMENTS = {
    "06082.HK": "芯片國產化龍頭，受政策面支撐強，回調即是機會。",
    "03888.HK": "遊戲業務穩定，雲服務增長略慢，短期看 30 元支撐。",
    "01810.HK": "SU7 交付量創紀錄，估值進入修復期，長線看好。",
    "DEFAULT": "大市波幅加劇，建議嚴格執行止蝕，控制總倉位。"
}

st.set_page_config(page_title="家族辦公室監控", layout="wide")

# --- 2. 身份驗證 ---
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write("# 🔐 家族辦公室")
        pwd = st.text_input("輸入密碼", type="password")
        if st.button("登入", use_container_width=True):
            if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# --- 3. 數據抓取與清洗 (關鍵：確保數據類型正確) ---
@st.cache_data(ttl=300)
def load_data():
    try:
        df = pd.read_csv(SHEET_URL)
        df.columns = [c.strip() for c in df.columns]
        # 強制將成本與數量轉為數字
        df["成本"] = pd.to_numeric(df["成本"], errors='coerce').fillna(0.0)
        df["數量"] = pd.to_numeric(df["數量"], errors='coerce').fillna(0.0)
        df["代號"] = df["代號"].astype(str).str.strip()
        return df
    except: return pd.DataFrame(columns=["代號", "成本", "數量"])

# --- 4. CSS 樣式 ---
st.markdown("""
    <style>
    .block-container { padding: 1.5rem 0.5rem 1rem !important; }
    .compact-row { background-color: #ffffff; padding: 12px 8px; display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 1px solid #f0f0f0; }
    .analysis-box { background-color: #f8f9fa; padding: 10px 12px; border-radius: 8px; border-left: 4px solid #333; margin: 2px 8px 15px 8px; }
    .data-grid { display: flex; flex-wrap: wrap; gap: 10px; font-size: 13px; margin-bottom: 5px; }
    .comment-text { font-size: 12px; color: #666; font-style: italic; border-top: 1px solid #eee; padding-top: 5px; margin-top: 5px; }
    .label-tag { font-size: 10px; color: #999; margin-right: 3px; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. 側邊欄 ---
with st.sidebar:
    st.header("⚙️ 管理")
    st.markdown(f'### [📝 編輯雲端數據]({EDIT_URL})')
    if st.button("🔄 同步數據", use_container_width=True):
        st.cache_data.clear(); st.rerun()
    st.write("---")
    if st.button("🚪 登出"): st.session_state.auth = False; st.rerun()

# --- 6. 核心處理邏輯 (修復 6082 等代號抓取) ---
df_data = load_data()

def get_live(symbol):
    # 修復邏輯：針對港股 5 位數代號，嘗試去掉領頭 0 (如 06082 -> 6082)
    s = symbol.upper()
    search = s.replace(".HK", "").lstrip('0') + ".HK" if ".HK" in s else s
    try:
        tk = yf.Ticker(search)
        hist = tk.history(period="5d")
        if not hist.empty:
            curr = hist['Close'].iloc[-1]
            return {"price": curr, "hist": hist, "support": curr*0.9, "target": curr*1.2, "stop": curr*0.85}
    except: return None

total_val_hkd, total_cost_hkd, results = 0.0, 0.0, []

for _, row in df_data.iterrows():
    sym = str(row["代號"])
    if not sym or sym == 'nan': continue
    
    live = get_live(sym)
    # 修正：如果 live 抓不到，則用成本價作為現價計算
    now_p = live["price"] if live else float(row["成本"])
    qty = float(row["數量"])
    cost_p = float(row["成本"])
    
    rate = 1.0 if ".HK" in sym.upper() else 7.8
    
    # 計算單隻盈虧 (HKD)
    single_profit = (now_p - cost_p) * qty * rate
    
    total_val_hkd += (now_p * qty) * rate
    total_cost_hkd += (cost_p * qty) * rate
    results.append({"sym": sym, "now": now_p, "cost": cost_p, "live": live, "p_hkd": single_profit, "qty": qty})

# --- 7. UI 顯示 ---
# 總覽
total_diff = total_val_hkd - total_cost_hkd
profit_pct = (total_diff / total_cost_hkd * 100) if total_cost_hkd > 0 else 0
st.markdown(f"""
    <div style="background-color: #1e1e1e; padding: 25px 15px; border-radius: 12px; text-align: center; margin-bottom: 15px;">
        <div style="color: #ffffff; font-size: 32px; font-weight: 800;">${total_val_hkd:,.0f}</div>
        <div style="color: {'#ff4b4b' if profit_pct < 0 else '#00c853'}; font-size: 18px; font-weight: 700;">
            {profit_pct:+.2f}% (${total_diff:,.0f} HKD)
        </div>
    </div>
""", unsafe_allow_html=True)

for item in results:
    name = NAMES.get(item["sym"], item["sym"])
    pct = ((item["now"] - item["cost"]) / item["cost"] * 100) if item["cost"] > 0 else 0
    color = "#ff4b4b" if pct < 0 else "#00c853"
    unit = "HK$" if ".HK" in item["sym"].upper() else "US$"
    comment = COMMENTS.get(item["sym"], COMMENTS["DEFAULT"])
    
    st.markdown(f"""
        <div class="compact-row">
            <div style="flex: 2;">
                <div style="font-size: 15px; font-weight: 700;">{name}</div>
                <div style="font-size: 10px; color: #999;">{item['sym']}</div>
            </div>
            <div style="flex: 2.5; text-align: center;">
                <div style="font-size: 14px; font-weight: 600;">{unit}{item['now']:.2f}</div>
                <div style="font-size: 10px; color: #666;"><span class="label-tag">成本:</span>{unit}{item['cost']:.2f}</div>
                <div style="font-size: 12px; font-weight: bold; color: {color}; margin-top: 3px;">貢獻: ${item['p_hkd']:,.0f}</div>
            </div>
            <div style="flex: 1.2; text-align: right;">
                <div style="font-size: 17px; font-weight: 800; color: {color};">{pct:+.1f}%</div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    if item["live"]:
        st.markdown(f"""
            <div class="analysis-box">
                <div class="data-grid">
                    <span>📍 支撐: <b>{unit}{item['live']['support']:.2f}</b></span>
                    <span>🎯 目標: <b>{unit}{item['live']['target']:.2f}</b></span>
                    <span style="color: #d32f2f;">🛑 止蝕: <b>{unit}{item['live']['stop']:.2f}</b></span>
                </div>
                <div class="comment-text">💬 {comment}</div>
            </div>
        """, unsafe_allow_html=True)
        with st.expander("📈 展開走勢圖"):
            fig = go.Figure(data=[go.Candlestick(x=item["live"]["hist"].index, open=item["live"]["hist"]['Open'], high=item["live"]["hist"]['High'], low=item["live"]["hist"]['Low'], close=item["live"]["hist"]['Close'])])
            fig.update_layout(height=180, margin=dict(l=0, r=0, t=0, b=0), xaxis_rangeslider_visible=False)
            st.plotly_chart(fig, use_container_width=True)
