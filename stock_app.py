import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 基礎配置與實體解鎖
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("🛡️ 專業資產管理系統")
    pwd = st.text_input("輸入密碼", type="password")
    if st.button("🔓 點擊解鎖系統", use_container_width=True):
        if pwd == "13579":
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 2. 持倉數據庫 (校對 OK)
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])
with t2: edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 啟動全球匯率同步掃描", use_container_width=True):
        res, v_mix, p_mix, v_hkd, p_hkd = [], 0.0, 0.0, 0.0, 0.0
        try: 
            usd_hkd = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: 
            usd_hkd = 7.82
        
        st.info(f"💡 匯率：1 USD = {usd_hkd:.4f} HKD")
        st.write("---")
        st.write("**🏛️ 操作邏輯：** R/R > 2 為優質標的；港股若無分析數據則取 52 週高位為壓力位；虧損 > 15% 觸發止蝕預警。")

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
                
                # 目標價補足與 R/R 計算
                tgt = inf.get('targetMeanPrice', float(h['High'].max()))
                low = inf.get('targetLowPrice', float(h['Low'].min()))
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                
                # 直接顯示撮要 (不需打開箭咀)
                st.subheader(f"📍 {r['代號']} ({'HKD' if is_hk else 'USD'})")
                c1, c2, c3 = st.columns(3)
                c1.write(f"**評級**: {str(inf.get('recommendationKey','N/A')).upper()}")
                c2.write(f"**升幅**: {((tgt-cp)/cp*100):.1f}%")
                c3.write(f"**R/R**: {rr}")
                
                adv = "✅ 具博弈價值" if rr > 2 else "⚠️ 觀望/持有"
                if p_pct < -15: adv = "🆘 嚴格止蝕預警"
                st.success(f"建議策略：{adv}")

                with st.expander("📈 查看技術走勢圖"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close']))
                    fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                # 累加計算 (校對 OK)
                mv = cp * r["數量"]; pn = (cp - r["成本"]) * r["數量"]
                v_mix += mv; p_mix += pn
                v_hkd += (mv * rate); p_hkd += (pn * rate)
                res.append({"代號": r["代號"], "R/R": rr, "盈虧%": round(p_pct, 1)})
            except: 
                st.warning(f"{r['代號']} 數據抓取失敗")
            bar.progress((i+1)/len(rows))
        
        # Dashboard 顯示 (港美分開校對)
        st.divider()
        st.header("🌍 全域看板")
        col_a, col_b, col_c = st.columns(3)
        col_a.metric("混合(面值)", f"${v_mix:,.0f}", f"損益: ${p_mix:,.0f}")
        col_b.metric("港幣(HKD)", f"HK${v_hkd:,.0f}", f"{(p_hkd/max(1, v_hkd)*100):.2f}%")
        col_c.metric("美元(USD)", f"US${(v_hkd/usd_hkd):,.0f}")
        
        st.write("📋 決策排行 (R/R)")
        st.dataframe(pd.DataFrame(res).sort_values("R/R", ascending=False), use_container_width=True)
    else: 
        st.info("請點擊按鈕執行分析。")
