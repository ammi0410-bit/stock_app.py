import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 基礎配置與解鎖 (實體按鈕)
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 存取控制")
    pwd = st.text_input("輸入密碼", type="password")
    if st.button("🔓 點擊解鎖系統", use_container_width=True):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 2. 持倉數據 (校對：引號與括號 OK)
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

# 3. 功能分頁
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])
with t2: edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

# 4. 核心掃描與分析摘要 (Backup)
with t1:
    if st.button("🚀 啟動掃描", use_container_width=True):
        res, v, p = [], 0.0, 0.0
        bar = st.progress(0)
        for i, r in edf.iterrows():
            try:
                tk = yf.Ticker(str(r["代號"]).strip())
                h = tk.history(period="1y")
                inf = tk.info
                if h.empty: continue
                cp = float(h['Close'].iloc[-1])
                tgt = inf.get('targetMeanPrice', cp*1.05)
                low = inf.get('targetLowPrice', cp*0.9)
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                res.append({"資產": r["代號"], "R/R": rr, "盈虧%": round(p_pct,1)})
                
                with st.expander(f"🔍 {r['代號']} (R/R: {rr})", expanded=(p_pct < -10)):
                    st.write(f"**分析摘要**: 評級 `{inf.get('recommendationKey','N/A')}` | 空間 `{(tgt-cp)/cp*100:.1f}%`")
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close']))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="green")
                    fig.add_hline(y=low, line_dash="dot", line_color="red")
                    fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                v += (cp * r["數量"]); p += ((cp - r["成本"]) * r["數量"])
            except: pass
            bar.progress((i+1)/len(edf))
        
        st.divider()
        st.metric("總市值", f"${v:,.0f}")
        st.metric("總盈虧", f"${p:,.0f}", f"{(p/max(1,v)*100):.2f}%")
        st.write("📋 決策建議 (按 R/R 排序)")
        st.dataframe(pd.DataFrame(res).sort_values("R/R", ascending=False), use_container_width=True)
    else: st.info("請點擊按鈕獲取數據。")
