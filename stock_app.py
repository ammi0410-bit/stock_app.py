import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 強制初始化數據 (放在最頂層防止 AttributeError)
HK_NAMES = {
    "06082.HK": "騰訊控股", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "中銀航空租賃", "02172.HK": "微創醫療", "02050.HK": "索信達控股",
    "01810.HK": "小米集團", "01530.HK": "三生製藥", "00699.HK": "神州租車"
}

if 'df' not in st.session_state:
    d = {"代號": list(HK_NAMES.keys()) + ["GOOG","KO","RBLX","TEM"],
         "成本": [38.2, 32.0, 182.0, 4.26, 13.0, 39.8, 34.7, 28.5, 19.0, 319.5, 52.9, 121.5, 77.9],
         "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]}
    st.session_state.df = pd.DataFrame(d)

# 2. 安全解鎖介面
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    pwd = st.text_input("密鑰", type="password")
    if st.button("🔓 解鎖系統", use_container_width=True):
        if pwd == "13579": 
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. 主程式分頁
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 管理"])

with t2: 
    # 更新編輯後的數據
    edf = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    st.session_state.df = edf

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        res, v_hkd, p_hkd, c_hkd = [], 0.0, 0.0, 0.0
        try: fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.825
        
        st.write(f"### 🌐 實時匯率: 1 USD = {fx:.4f} HKD")
        stocks = st.session_state.df.to_dict('records')
        
        for r in stocks:
            s_orig = str(r["代號"]).strip().upper()
            is_hk = ".HK" in s_orig
            # 自動修復港股代號
            s_list = [s_orig, s_orig.lstrip("0")] if s_orig.startswith("0") and is_hk else [s_orig]
            
            h, tk, ok = None, None, False
            for s in s_list:
                try:
                    tk = yf.Ticker(s); h = tk.history(period="1y")
                    if not h.empty: ok = True; break
                except: continue
            if not ok: continue

            try:
                inf = tk.info
                # 繁體中文與英文全名分流
                nm = HK_NAMES.get(s_orig, inf.get('shortName', s_orig)) if is_hk else inf.get('longName', s_orig)
                cp = float(h['Close'].iloc[-1])
                bp = float(r["成本"])
                rate = 1.0 if is_hk else fx
                
                # 止蝕位邏輯修正
                tgt = inf.get('targetMeanPrice', float(h['High'].max()*0.98))
                low = inf.get('targetLowPrice', 0)
                if low <= 0 or low >= cp: low = float(h['Low'].min())
                if low >= cp: low = bp * 0.85 

                rec = str(inf.get('recommendationKey', 'N/A')).upper()
                if rec == 'N/A': rec = "BUY" if cp > h['Close'].mean() else "HOLD"
                
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - bp) / bp * 100
                
                # --- UI 更新：現價與買入價並排 (H4 字體) ---
                st.markdown(f"#### 💎 {s_orig} | {nm}")
                cur_sym = 'HK$' if is_hk else 'US$'
                st.markdown(f"#### **現價: {cur_sym}{cp:.2f}** | 買入價: {cur_sym}{bp:.2f}")
                st.markdown(f"#### [ 評級: `{rec}` | R/R: `{rr}` | 盈虧: `{p_pct:.1f}%` ]")
                
                # 建議 Body
                adv = f"📍 **分析：** {nm} 目標價 **{tgt:.2f}**，支撐防線 **{low:.2f}**。"
                if p_pct < -15: 
                    adv = f"🆘 **止蝕警告：** 虧損達 {p_pct:.1f}%！目前支撐位在 **{low:.2f}**，跌破請考慮減倉。"
                st.write(f"#### {adv}")

                with st.expander("📈 點擊展開 12 個月走勢圖表"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close']))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="green", annotation_text="目標")
                    fig.add_hline(y=low, line_dash="dot", line_color="red", annotation_text="支撐")
                    fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                v_hkd += (cp * r["數量"] * rate)
                p_hkd += ((cp - bp) * r["數量"] * rate)
                c_hkd += (bp * r["數量"] * rate)
                res.append({"代號": s_orig, "名稱": nm, "盈虧%": round(p_pct, 1)})
                st.divider()
            except: pass
        
        # 4. 全域看板
        st.header("🌍 全域看板 (HKD)")
        d1, d2, d3 = st.columns(3)
        d1.metric("總市值", f"HK${v_hkd:,.0f}")
        d2.metric("總投入成本", f"HK${c_hkd:,.0f}")
        d3.metric("總盈虧", f"HK${p_hkd:,.0f}", f"{(p_hkd/max(1, c_hkd)*100):.2f}%")
        st.dataframe(pd.DataFrame(res).sort_values("盈虧%", ascending=False), use_container_width=True)
    else: st.info("系統就緒，請執行掃描。")
