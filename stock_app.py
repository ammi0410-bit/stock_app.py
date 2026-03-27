import streamlit as st
import yfinance as yf
import pandas as pd

# 1. 名稱映射 (100% 準確)
HK_NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子"
}

# 2. 初始化數據 (對照你的真實持倉)
if 'df' not in st.session_state:
    data = {
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    }
    st.session_state.df = pd.DataFrame(data)

# 3. 安全設置
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("🔐 密鑰", type="password")
    if st.button("解鎖"):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 4. 主介面
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])

with t2:
    # 這裡的編輯會直接更新到 session_state
    st.session_state.df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    st.info("💡 修改後請切換到『決策分析』並執行掃描。")

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        try:
            fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except:
            fx = 7.828
        
        st.write(f"### 🌐 匯率: 1 USD = {fx:.4f} HKD")
        v_hkd, c_hkd = 0.0, 0.0
        
        for _, r in st.session_state.df.iterrows():
            sym = str(r["代號"]).strip().upper()
            if not sym or sym == "NAN": continue
            
            try:
                tk = yf.Ticker(sym)
                h = tk.history(period="5d")
                if h.empty: continue
                
                cp = float(h['Close'].iloc[-1])
                bp, qty = float(r["成本"]), float(r["數量"])
                rate = 1.0 if ".HK" in sym else fx
                
                nm = HK_NAMES.get(sym, sym)
                p_pct = (cp - bp) / bp * 100
                color = "🔴" if p_pct < -10 else "🟢"
                
                # UI 顯示
                st.markdown(f"#### 💎 {sym} | {nm}")
                st.markdown(f"**現價:** HK${cp*rate:.2f} | **盈虧:** {color} {p_pct:.1f}%")
                st.divider()
                
                v_hkd += (cp * qty * rate)
                c_hkd += (bp * qty * rate)
            except:
                continue
        
        if v_hkd > 0:
            st.header("🌍 總結")
            st.metric("總市值 (HKD)", f"${v_hkd:,.0f}", f"{(v_hkd-c_hkd):,.0f}")
