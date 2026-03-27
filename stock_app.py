import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 基礎配置
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("密鑰", type="password")
    if st.button("🔓 解鎖", use_container_width=True):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 2. 數據庫
if 'df' not in st.session_state:
    d = {"代號": ["06082.HK","03888.HK","02888.HK","02562.HK","02172.HK","02050.HK","01810.HK","01530.HK","00699.HK","GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])
with t2: edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        res, v_hkd, p_hkd = [], 0.0, 0.0
        try: fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.825
        
        st.write(f"### 🌐 實時匯率: 1 USD = {fx:.4f} HKD")
        
        rows = edf.to_dict('records')
        for i, r in enumerate(rows):
            sym = str(r["代號"]).strip()
            try:
                tk = yf.Ticker(sym)
                h = tk.history(period="1y")
                inf = tk.info
                if h.empty:
                    st.warning(f"⚠️ {sym} 暫無交易數據")
                    continue
                
                cp = float(h['Close'].iloc[-1])
                is_hk = ".HK" in sym.upper()
                rate = 1.0 if is_hk else fx
                
                # --- 強制港股分析回補 ---
                tgt = inf.get('targetMeanPrice')
                if not tgt: tgt = (float(h['High'].max()) + float(h['Low'].min())) / 2 # 取中軸為目標
                
                low = inf.get('targetLowPrice')
                if not low: low = float(h['Low'].min())
                
                rec = str(inf.get('recommendationKey', 'N/A')).upper()
                if rec == 'N/A': rec = "BUY (技術轉強)" if cp > h['Close'].mean() else "HOLD (盤整)"
                
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                
                # --- UI: 大字體、現價、評級、升幅 ---
                st.markdown(f"## 💎 {sym} | 現價: {'HK$' if is_hk else 'US$'}{cp:.2f}")
                
                # 強制輸出文字建議
                st.write(f"**市場評級**: `{rec}` | **預期升幅**: `{((tgt-cp)/cp*100):.1f}%` | **R/R 評分**: `{rr}`")
                
                adv = f"💡 **財經分析：** 根據數據，{sym} 目標價看 **{tgt:.2f}**。 "
                if rr > 2: adv += "現價風險回報比極佳，屬於低風險高收益區間，建議重點配置。"
                elif rr > 1: adv += "走勢相對平穩，建議分批吸納，長線持有。"
                else: adv += "接近前期阻力位，上行空間相對有限，建議觀望或減持。"
                
                if p_pct < -15: adv = f"🆘 **止蝕警告：** 目前帳面虧損 {p_pct:.1f}%，建議緊盯支撐位 **{low:.2f}**，跌破需執行保護性減倉。"
                
                st.markdown(adv)

                with st.expander("📈 展開技術圖表"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close']))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="green", annotation_text="目標")
                    fig.add_hline(y=low, line_dash="dot", line_color="red", annotation_text="底線")
                    fig.update_layout(height=180, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                v_hkd += (cp * r["數量"] * rate)
                p_hkd += ((cp - r["成本"]) * r["數量"] * rate)
                res.append({"代號": sym, "R/R": rr, "現價": cp, "評級": rec})
                st.divider()
            except Exception as e:
                st.error(f"解析 {sym} 時發生錯誤: {e}")
        
        st.header("🌍 全域看板 (HKD)")
        d1, d2 = st.columns(2)
        d1.metric("總市值", f"HK${v_hkd:,.0f}")
        d2.metric("總損益", f"HK${p_hkd:,.0f}", f"{(p_hkd/max(1, v_hkd)*100):.2f}%")
        st.dataframe(pd.DataFrame(res).sort_values("R/R", ascending=False), use_container_width=True)
    else:
        st.info("👋 系統已就緒，請點擊上方按鈕執行掃描。")
