import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 配置與安全 (實體 Enter 按鈕)
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 存取控制")
    pwd = st.text_input("密碼", type="password")
    if st.button("🔓 點擊解鎖系統", use_container_width=True):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
        else: st.error("錯誤")
    st.stop()

# 2. 持倉數據 (精簡 DataFrame)
if 'df' not in st.session_state:
    d = {
        "代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
        "成本": [38.2, 32.0, 182.0, 4.267, 13.0, 39.8, 34.75, 28.54, 19.0, 319.58, 52.98, 121.56, 77.92],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    }
    st.session_state.df = pd.DataFrame(d)

# 3. 功能分頁
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])
with t2:
    edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球分析師共識掃描", use_container_width=True):
        res, v, p = [], 0.0, 0.0
        bar = st.progress(0)
        for i, r in edf.iterrows():
            try:
                tk = yf.Ticker(str(r["代號"]).strip())
                h = tk.history(period="1y")
                inf = tk.info
                cp = float(h['Close'].iloc[-1])
                tgt = inf.get('targetMeanPrice', cp * 1.05)
                low = inf.get('targetLowPrice', cp * 0.9)
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                res.append({"資產": r["代號"], "現價": cp, "R/R": rr, "盈虧%": round(p_pct,1)})
                
                with st.expander(f"🔍 {r['代號']} (R/R: {rr})", expanded=(p_pct < -10)):
                    st.write(f"**評級**: {inf.get('recommendationKey','N/A').upper()} | **空間**: {(tgt-cp)/cp*100:.1f}%")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=h.index, y=h['Close'], name="Price"))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="lime")
                    fig.add_hline(y=low, line_dash="dot", line_color="red")
                    fig.update_layout(template="plotly_dark", height=250, margin=dict(l=0,r=0,t=0,b=0))
                    st.plotly_chart(fig, use_container_width=True)
                v += (cp
