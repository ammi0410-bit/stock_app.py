import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 【核心數據庫】繁體中文映射表 (已根據富途牛牛更正 2562 為 獅騰控股)
HK_NAMES = {
    "02562.HK": "獅騰控股", 
    "06082.HK": "騰訊控股", 
    "03888.HK": "金山軟件", 
    "02888.HK": "渣打集團",
    "02172.HK": "微創醫療", 
    "02050.HK": "索信達控股",
    "01810.HK": "小米集團", 
    "01530.HK": "三生製藥", 
    "00699.HK": "神州租車",
    "00700.HK": "騰訊控股(主)",
    "09988.HK": "阿里巴巴",
    "03690.HK": "美團"
}

# 2. 【數據持久化】固定你的真實持倉
if 'df' not in st.session_state:
    d = {
        "代號": ["02562.HK", "06082.HK", "03888.HK", "02888.HK", "02172.HK", "02050.HK", "GOOG", "KO", "TEM"],
        "成本": [4.26, 38.2, 32.0, 182.0, 13.0, 39.8, 155.2, 58.5, 77.9],
        "數量": [3000, 200, 400, 50, 1000, 300, 10, 50, 170]
    }
    st.session_state.df = pd.DataFrame(d)

# 3. 安全解鎖
st.set_page_config(page_title="家族辦公室", layout="wide")
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("密鑰", type="password")
    if st.button("🔓 解鎖系統", use_container_width=True):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

# 4. 主介面
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 持倉管理"])

with t2:
    st.info("💡 提示：在代號欄輸入 XXXX.HK，掃描時會自動匹配中文名稱。永久修改請更動代碼。")
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
                # 優先從映射表找中文名
                nm = HK_NAMES.get(s_orig, inf.get('shortName', s_orig)) if is_hk else inf.get('longName', s_orig)
                cp = float(h['Close'].iloc[-1])
                bp = float(r["成本"])
                rate = 1.0 if is_hk else fx
                
                # 止蝕/目標價邏輯
                tgt = inf.get('targetMeanPrice', float(h['High'].max()*0.98))
                low = inf.get('targetLowPrice', 0)
                if low <= 0 or low >= cp: low = float(h['Low'].min())
                if low >= cp: low = bp * 0.85 

                rec = str(inf.get('recommendationKey', 'N/A')).upper()
                if rec == 'N/A': rec = "BUY" if cp > h['Close'].mean() else "HOLD"
                
                p_pct = (cp - bp) / bp * 100
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                
                # --- UI: 視覺統一呈現 ---
                st.markdown(f"#### 💎 {s_orig} | {nm}")
                cur = 'HK$' if is_hk else 'US$'
                st.markdown(f"#### 現價: {cur}{cp:.2f} | 買入價: {cur}{bp:.2f}")
                
                color = "🔴" if p_pct < -10 else "🟢"
                st.markdown(f"#### [ 評級: {rec} | R/R: {rr} | {color} 盈虧: {p_pct:.1f}% ]")
                
                adv = f"📍 分析：{nm} 目前支撐 {low:.2f}。目標看 {tgt:.2f}。"
                if p_pct < -15: 
                    adv = f"🆘 止蝕警告：虧損已達 {p_pct:.1f}%！若跌破 {low:.2f} 建議考慮防守。"
                st.write(f"#### {adv}")

                with st.expander("📈 點擊展開 12 個月走勢圖表"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close'], name="價格"))
                    fig.add_hline(y=tgt, line_dash="dash", line_color="green", annotation_text="目標")
                    fig.add_hline(y=low, line_dash="dot", line_color="red", annotation_text="支撐")
                    fig.update_layout(height=220, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                v_hkd += (cp * r["數量"] * rate)
                c_hkd += (bp * r["數量"] * rate)
                p_hkd += ((cp - bp) * r["數量"] * rate)
                res.append({"代號": s_orig, "名稱": nm, "盈虧%": round(p_pct, 1)})
                st.divider()
            except: pass
        
        # 5. 全域看板
        st.header("🌍 全域看板 (HKD)")
        col1, col2, col3 = st.columns(3)
        col1.metric("總市值", f"HK${v_hkd:,.0f}")
        col2.metric("總投入", f"HK${c_hkd:,.0f}")
        col3.metric("總盈虧", f"HK${p_hkd:,.0f}", f"{(p_hkd/max(1, c_hkd)*100):.2f}%")
        st.dataframe(pd.DataFrame(res).sort_values("盈虧%", ascending=False), use_container_width=True)
    else:
        st.info("✅ 系統已就緒，請執行掃描。")
