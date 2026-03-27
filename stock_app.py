import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 介面配置 ---
st.set_page_config(page_title="家族辦公室終端", layout="wide")
st.markdown("<style>.stMetric { background-color: #161b22; border-radius: 10px; padding: 15px; border: 1px solid #30363d; }</style>", unsafe_allow_html=True)

# --- 2. 安全閘口 ---
if 'auth' not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 家族資產管理系統")
    pwd = st.text_input("輸入密鑰並按 Enter", type="password")
    if pwd == "13579":
        st.session_state.auth = True
        st.rerun()
    elif pwd != "":
        st.error("密鑰無效")
    st.stop()

# --- 3. 持倉數據 (精簡版防止截斷) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"代號": "06082.HK", "成本": 38.20, "數量": 200.0},
        {"代號": "03888.HK", "成本": 32.00, "數量": 400.0},
        {"代號": "02888.HK", "成本": 182.0, "數量": 50.0},
        {"代號": "02562.HK", "成本": 4.267, "數量": 3000.0},
        {"代號": "02172.HK", "成本": 13.00, "數量": 1000.0},
        {"代號": "02050.HK", "成本": 39.80, "數量": 300.0},
        {"代號": "01810.HK", "成本": 34.75, "數量": 400.0},
        {"代號": "01530.HK", "成本": 28.54, "數量": 500.0},
        {"代號": "00699.HK", "成本": 19.00, "數量": 1000.0},
        {"代號": "GOOG", "成本": 319.58, "數量": 12.0},
        {"代號": "KO", "成本": 52.98, "數量": 1.0},
        {"代 --號": "RBLX", "成本": 121.56, "數量": 52.0},
        {"代號": "TEM", "成本": 77.92, "數量": 170.0}
    ]

# --- 4. 功能分欄 ---
tab1, tab2 = st.tabs(["📊 實時戰略", "⚙️ 數據管理"])

with tab2:
    edited_df = st.data_editor(pd.DataFrame(st.session_state.portfolio), num_rows="dynamic", use_container_width=True)
    if st.button("登出"):
        st.session_state.auth = False
        st.rerun()

with tab1:
    st.title("🏛️ 專業資產配置終端")
    if st.button("🚀 執行全球分析師共識掃描"):
        summary, total_val, total_pnl = [], 0.0, 0.0
        prog = st.progress(0)
        stocks = edited_df.to_dict('records')
        
        for i, s in enumerate(stocks):
            t = str(s["代號"]).upper().strip()
            try:
                tk = yf.Ticker(t)
                hist = tk.history(period="1y")
                info = tk.info
                if hist.empty: continue
                
                curr_p = float(hist['Close'].iloc[-1])
                target = info.get('targetMeanPrice', curr_p * 1.05)
                t_low = info.get('targetLowPrice', curr_p * 0.9)
                
                rr = round((target - curr_p) / max(0.01, curr_p - t_low), 2)
                mkt_val = curr_p * s["數量"]
                pnl = (curr_p - s["成本"]) * s["數量"]
                total_val += mkt_val
                total_pnl += pnl
                
                summary.append({
                    "資產": t, "現價": round(curr_p, 2), "R/R比率": rr, 
                    "盈虧%": round((curr_p-s["成本"])/s["成本"]*100, 1),
                    "目標": round(target, 2), "底線": round(t_low, 2)
                })
                
                with st.expander(f"🔍 {t} 部署 (R/R: {rr})", expanded=(curr_p < s["成本"])):
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="價格", line=dict(color='#00d1ff')))
                    fig.add_hline(y=target, line_dash="dash", line_color="#00ff00", annotation_text="止盈")
                    fig.add_hline(y=t_low, line_dash="dot", line_color="#ff4b4b", annotation_text="止蝕")
                    fig.add_hline(y=s["成本"], line_dash="solid", line_color="#ffd700", annotation_text="成本")
                    fig.update_layout(template="plotly_dark", height=300, margin=dict(l=0,r=0,t=30,b=0))
                    st.plotly_chart(fig, use_container_width=True)
            except: pass
            prog.progress((i+1)/len(stocks))

        st.divider()
        c1, c2, c3 = st.columns(3)
        c1.metric("總市值", f"${total_val:,.0f}")
        c2.metric("總損益", f"${total_pnl:,.0f}", f"{total_pnl/max(1, total_val)*100:.2f}%")
        c3.metric("高價值資產 (R/R>2)", len([x for x in summary if x['R/R比率'] > 2]))
        st.dataframe(pd.DataFrame(summary).sort_values(by="R/R比率", ascending=False), use_container_width=True)
    else:
        st.info("請點擊按鈕獲取最新市場共識建議。")
