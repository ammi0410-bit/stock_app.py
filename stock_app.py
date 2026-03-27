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
with t2: 
    # 更新編輯後的數據到 session_state
    edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    st.session_state.df = edf

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        res, v_hkd, p_hkd = [], 0.0, 0.0
        try: fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.825
        
        st.write(f"### 🌐 實時匯率: 1 USD = {fx:.4f} HKD")
        
        # 確保數據源不為空
        stocks = st.session_state.df.to_dict('records')
        
        for r in stocks:
            s_orig = str(r["代號"]).strip()
            # 港股格式補丁
            s_list = [s_orig, s_orig.lstrip("0")] if s_orig.startswith("0") else [s_orig]
            h, tk, ok = None, None, False
            
            for s in s_list:
                try:
                    tk = yf.Ticker(s)
                    h = tk.history(period="1y")
                    if not h.empty: ok = True; break
                except: continue
                
            if not ok:
                st.write(f"#### ⚠️ 無法獲取 {s_orig} 數據")
                continue

            try:
                inf = tk.info
                # 獲取名稱
                nm = inf.get('longName', s_orig)
                cp = float(h['Close'].iloc[-1])
                is_hk = ".HK" in s_orig.upper()
                rate = 1.0 if is_hk else fx
                
                # 數據計算
                tgt = inf.get('targetMeanPrice', float(h['High'].max()*0.98))
                low = inf.get('targetLowPrice', float(h['Low'].min()*1.02))
                rec = str(inf.get('recommendationKey', 'N/A')).upper()
                if rec == 'N/A': rec = "BUY" if cp > h['Close'].mean() else "HOLD"
                
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - r["成本"]) / r["成本"] * 100
                
                # --- UI: 統一 H4 字體 ---
                st.markdown(f"#### 💎 {s_orig} | {nm}")
                st.markdown(f"#### **現價: {'HK$' if is_hk else 'US$'}{cp:.2f}**")
                st.markdown(f"#### [ 評級: `{rec}` | R/R: `{rr}` | 盈虧: `{p_pct:.1f}%` ]")
                
                # 建議文字
                adv = f"📍 **分析：** {nm} 目標價看 **{tgt:.2f}**，支撐位 **{low:.2f}**。"
                if rr > 2: adv += " 現價風險回報比佳，建議積極關注。"
                elif rr > 1: adv += " 走勢穩健，建議長線持有。"
                else: adv += " 接近阻力位，建議觀望。"
                if p_pct < -15: adv = f"🆘 **止蝕警告：** 虧損 {p_pct:.1f}%，請嚴守 **{low:.2f}**。"
                st.write(f"#### {adv}")

                with st.expander("📈 點擊展開 12 個月走勢圖表"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close']))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="green")
                    fig.add_hline(y=low, line_dash="dot", line_color="red")
                    fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                v_hkd += (cp * r["數量"] * rate)
                p_hkd += ((cp - r["成本"]) * r["數量"] * rate)
                res.append({"代號": s_orig, "名稱": nm, "R/R": rr, "盈虧%": round(p_pct, 1)})
                st.divider()
            except: 
                st.write(f"#### ⚠️ {s_orig} 解析出錯")
        
        st.header("🌍 全域看板 (HKD)")
        d1, d2 = st.columns(2)
        d1.metric("總市值", f"HK${v_hkd:,.0f}")
        d2.metric("總盈虧", f"HK${p_hkd:,.0f}", f"{(p_hkd/max(1, v_hkd)*100):.2f}%")
        st.dataframe(pd.DataFrame(res).sort_values("盈虧%", ascending=False), use_container_width=True)
    else: st.info("系統就緒。")
