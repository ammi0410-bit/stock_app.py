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
            orig_sym = str(r["代號"]).strip()
            # 港股格式自動修復邏輯
            sym_list = [orig_sym]
            if orig_sym.startswith("0") and ".HK" in orig_sym.upper():
                sym_list.append(orig_sym.lstrip("0")) # 嘗試去零版本
            
            h, tk, success = None, None, False
            for s in sym_list:
                tk = yf.Ticker(s)
                h = tk.history(period="1y")
                if not h.empty:
                    success = True; break
            
            if not success:
                st.error(f"❌ {orig_sym} 數據獲取失敗，請檢查代號是否正確。")
                continue

            try:
                inf = tk.info
                cp = float(h['Close'].iloc[-1])
                is_hk = ".HK" in orig_sym.upper()
                rate = 1.0 if is_hk else fx
                
                # 數據補足
                tgt = inf.get('targetMeanPrice', float(h['High'].max() * 0.95))
                low = inf.get('targetLowPrice', float(h['Low'].min() * 1.05))
                rec = str(inf.get('recommendationKey', 'N/A')).upper()
                if rec == 'N/A': rec = "BUY" if cp > h['Close'].mean() else "HOLD"
                
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                
                # --- UI 加大加粗：Heading 與 Body ---
                st.markdown(f"# 💎 {orig_sym}")
                st.markdown(f"## **現價: {'HK$' if is_hk else 'US$'}{cp:.2f}**")
                
                st.markdown(f"### **[ 評級: {rec} | 升幅: {((tgt-cp)/cp*100):.1f}% | 評分: {rr} ]**")
                
                # 財經建議文字 Body
                advice = f"📍 **專業分析：** 標的 `{orig_sym}` 目前報價 **{cp:.2f}**。根據最新技術指標，"
                if rr > 2: advice += f"該股展現極強的風險回報比。目標價看 **{tgt:.2f}**，建議在支撐位 **{low:.2f}** 上方積極加倉。"
                elif rr > 1: advice += f"目前處於合理價值區間，走勢中規中矩。建議分批逢低吸納，長期持有至 **{tgt:.2f}**。"
                else: advice += f"股價已接近分析師阻力位 **{tgt:.2f}**，短期上行空間有限，建議觀望或獲利回吐。"
                
                if p_pct < -15: advice = f"🆘 **緊急預警：** 當前虧損達 **{p_pct:.1f}%**！股價已威脅到支撐底線 **{low:.2f}**，需嚴格執行止蝕計劃。"
                
                st.write(f"#### {advice}")

                with st.expander("📊 點擊展開 12 個月走勢圖表"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close'], name="股價"))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="green", annotation_text="阻力目標")
                    fig.add_hline(y=low, line_dash="dot", line_color="red", annotation_text="支撐底線")
                    fig.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                v_hkd += (cp * r["數量"] * rate)
                p_hkd += ((cp - r["成本"]) * r["數量"] * rate)
                res.append({"代號": orig_sym, "R/R": rr, "現價": cp, "評級": rec})
                st.divider()
            except Exception as e:
                st.warning(f"解析 {orig_sym} 數據時出錯，可能是 API 限制。")
        
        st.header("🌍 家族全域看板 (HKD)")
        d1, d2 = st.columns(2)
        d1.metric("總市值", f"HK${v_hkd:,.0f}")
        d2.metric("總盈虧", f"HK${p_hkd:,.0f}", f"{(p_hkd/max(1, v_hkd)*100):.2f}%")
        st.dataframe(pd.DataFrame(res).sort_values("R/R", ascending=False), use_container_width=True)
    else: st.info("👋 數據修復完成。請啟動掃描。")
