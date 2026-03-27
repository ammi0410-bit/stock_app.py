import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 安全與基礎配置
st.set_page_config(page_title="家族辦公室 | 全球決策終端", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業資產管理系統")
    pwd = st.text_input("輸入密鑰", type="password")
    if st.button("🔓 點擊解鎖系統", use_container_width=True):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 2. 持倉數據庫
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])
with t2: edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球/港股共識掃描", use_container_width=True):
        res, v_hkd, p_hkd = [], 0.0, 0.0
        try: usd_hkd = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: usd_hkd = 7.82
        
        st.info(f"💡 實時匯率：1 USD = {usd_hkd:.4f} HKD")
        
        bar = st.progress(0)
        rows = edf.to_dict('records')
        for i, r in enumerate(rows):
            try:
                tk = yf.Ticker(str(r["代號"]).strip())
                h = tk.history(period="1y")
                inf = tk.info
                if h.empty: continue
                
                cp = float(h['Close'].iloc[-1])
                is_hk = ".HK" in str(r["代號"]).upper()
                rate = 1.0 if is_hk else usd_hkd
                
                # --- 核心邏輯：數據回補機制 ---
                # 1. 評級回補
                rec = inf.get('recommendationKey', 'N/A').upper()
                if rec == 'N/A':
                    # 簡單技術面判斷 (港股常用)
                    ma50 = h['Close'].rolling(50).mean().iloc[-1]
                    rec = "BUY (技術轉強)" if cp > ma50 else "HOLD (區間震盪)"
                
                # 2. 目標價回補 (港股取52週高位)
                tgt = inf.get('targetMeanPrice')
                if not tgt: tgt = float(h['High'].max())
                
                low = inf.get('targetLowPrice')
                if not low: low = float(h['Low'].min())
                
                # 3. R/R 計算
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                
                # --- 顯示撮要 (文字化建議) ---
                st.subheader(f"📍 {r['代號']} ({'港幣' if is_hk else '美元'})")
                c1, c2, c3 = st.columns(3)
                c1.metric("當前評級", rec)
                c2.metric("預期升幅", f"{((tgt-cp)/cp*100):.1f}%")
                c3.metric("R/R 評分", rr)
                
                # 文字化財經建議彙整
                advice_txt = ""
                if rr > 2: advice_txt = "🔥 **共識建議：** 具備極高風險回報比。財經數據顯示現價處於相對低位，目標價指向 " + str(round(tgt,2)) + "，建議積極關注。"
                elif rr > 1: advice_txt = "⚖️ **共識建議：** 走勢穩健，目前處於價值合理區間。建議分批持有，觀察支撐位 " + str(round(low,2)) + "。"
                else: advice_txt = "⚠️ **共識建議：** 接近阻力位或下行風險較大。除非基本面有重大突破，否則不建議此時追高。"
                
                if p_pct < -15: advice_txt = "🆘 **緊急預警：** 帳面虧損已達 " + str(round(p_pct,1)) + "%。已跌穿心理防線，請務必查看下方圖表紅線支撐。"
                
                st.markdown(advice_txt)

                with st.expander("📈 查看技術走勢與阻力位"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close'], name="價格"))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="green", annotation_text="目標/阻力")
                    fig.add_hline(y=r["成本"], line_dash="solid", line_color="orange", annotation_text="你的成本")
                    fig.add_hline(y=low, line_dash="dot", line_color="red", annotation_text="支撐底線")
                    fig.update_layout(height=250, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                v_hkd += (cp * r["數量"] * rate)
                p_hkd += ((cp - r["成本"]) * r["數量"] * rate)
                res.append({"代號": r["代號"], "評級": rec, "R/R": rr, "盈虧%": round(p_pct, 1)})
                st.divider()
            except: pass
            bar.progress((i+1)/len(rows))
        
        # Dashboard
        st.header("🌍 全球資產看板 (統一 HKD)")
        d1, d2 = st.columns(2)
        d1.metric("總市值 (HKD)", f"HK${v_hkd:,.0f}")
        d2.metric("總損益 (HKD)", f"HK${p_hkd:,.0f}", f"{(p_hkd/max(1, v_hkd)*100):.2f}%")
        
        st.write("📋 投資優先級排名 (基於 R/R)")
        st.dataframe(pd.DataFrame(res).sort_values("R/R", ascending=False), use_container_width=True)
    else: st.info("請點擊啟動分析。")
