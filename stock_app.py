import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# 1. 【核心數據庫】繁體中文映射表 (根據富途牛牛真實截圖 100% 正名)
HK_NAMES = {
    "06082.HK": "壁仞科技",      # 修正：之前誤植為騰訊
    "03888.HK": "金山軟件",
    "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股",
    "02172.HK": "微創腦科學",    # 修正：之前誤植為微創醫療
    "02050.HK": "三花智控",      # 修正：富途正名
    "01810.HK": "小米集團-W",
    "01530.HK": "三生製藥",
    "00699.HK": "均勝電子",      # 修正：富途正名
}

US_NAMES = {
    "GOOG": "谷歌-C",
    "KO": "可口可樂",
    "RBLX": "Roblox",
    "TEM": "Tempus AI"
}

# 2. 【數據持久化】將截圖中的真實存倉資料直接固定
if 'df' not in st.session_state:
    # 這份數據 100% 對照你的富途帳戶截圖
    d = {
        "代號": [
            "06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", 
            "02050.HK", "01810.HK", "01530.HK", "00699.HK", 
            "GOOG", "KO", "RBLX", "TEM"
        ],
        "成本": [
            38.20, 32.00, 182.00, 4.267, 13.00, 
            39.80, 34.75, 28.54, 19.00, 
            319.58, 52.98, 121.558, 77.924
        ],
        "數量": [
            200, 400, 50, 3000, 1000, 
            300, 400, 500, 1000, 
            12, 1, 52, 170
        ]
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

# 4. 主介面分頁
t1, t2 = st.tabs(["📊 決策分析", "⚙️ 持倉管理"])

with t2:
    st.markdown("#### 📋 持倉數據編輯")
    st.info("💡 操作指南：\n1. 此表格已同步你的富途截圖數據。\n2. 修改後需切換到「決策分析」並掃描。\n3. 若要永久修改預設數據，請更動代碼中的 Section 2。")
    
    # 編輯器與 session_state 綁定
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    
    # 即時寫入邏輯
    if not edited_df.equals(st.session_state.df):
        st.session_state.df = edited_df
        st.success("✅ 記錄已同步，請前往『決策分析』進行掃描。")

with t1:
    if st.button("🚀 執行全球同步掃描", use_container_width=True):
        res, v_hkd, p_hkd, c_hkd = [], 0.0, 0.0, 0.0
        try: fx = yf.Ticker("HKD=X").history(period="1d")['Close'].iloc[-1]
        except: fx = 7.825
        
        st.write(f"### 🌐 實時匯率: 1 USD = {fx:.4f} HKD")
        stocks = st.session_state.df.to_dict('records')
        
        for r in stocks:
            s_orig = str(r["代號"]).strip().upper()
            if not s_orig or s_orig == 'NAN': continue
            
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
                # --- 真實名稱映射邏輯 ---
                if is_hk:
                    nm = HK_NAMES.get(s_orig, inf.get('shortName', s_orig))
                else:
                    nm = US_NAMES.get(s_orig, inf.get('longName', s_orig))
                
                cp = float(h['Close'].iloc[-1])
                bp = float(r["成本"])
                qty = float(r["數量"])
                rate = 1.0 if is_hk else fx
                
                # 數據補足
                tgt = inf.get('targetMeanPrice', float(h['High'].max()*0.98))
                low = inf.get('targetLowPrice', 0)
                if low <= 0 or low >= cp: low = float(h['Low'].min())
                if low >= cp: low = bp * 0.85 
                
                rec = str(inf.get('recommendationKey', 'N/A')).upper()
                if rec == 'N/A': rec = "BUY" if cp > h['Close'].mean() else "HOLD"
                
                rr = round((tgt - cp) / max(0.1, cp - low), 2)
                p_pct = (cp - bp) / bp * 100
                
                # --- UI: 視覺統一呈現 ---
                st.markdown(f"#### 💎 {s_orig} | {nm}")
                cur = 'HK$' if is_hk else 'US$'
                st.markdown(f"#### 現價: {cur}{cp:.2f} | 買入價: {cur}{bp:.2f}")
                
                color = "🔴" if p_pct < -10 else "🟢"
                st.markdown(f"#### [ 評級: {rec} | R/R: {rr} | {color} 盈虧: {p_pct:.1f}% ]")
                
                adv = f"📍 分析：{nm} 支撐 {low:.2f}，目標 {tgt:.2f}。"
                if p_pct < -15: 
                    adv = f"🆘 止蝕警告：虧損已達 {p_pct:.1f}%！若跌破 {low:.2f} 需嚴格防守。"
                st.write(f"#### {adv}")

                with st.expander("📈 點擊展開 12 個月走勢圖表"):
                    fig = go.Figure(go.Scatter(x=h.index, y=h['Close']))
                    fig.update_layout(height=200, margin=dict(l=0,r=0,t=0,b=0), template="plotly_dark")
                    st.plotly_chart(fig, use_container_width=True)
                
                v_hkd += (cp * qty * rate)
                c_hkd += (bp * qty * rate)
                res.append({"代號": s_orig, "名稱": nm, "盈虧%": round(p_pct, 1)})
                st.divider()
            except: pass
        
        # 全域看板
        st.header("🌍 全域看板 (HKD)")
        d1, d2, d3 = st.columns(3)
        d1.metric("總市值", f"HK${v_hkd:,.0f}")
        d2.metric("總投入", f"HK${c_hkd:,.0f}")
        # 修正：今日損益顯示錯誤
        d3.metric("總損益", f"HK${(v_hkd-c_hkd):,.0f}", f"{((v_hkd-c_hkd)/c_hkd*100):.2f}%")
        st.dataframe(pd.DataFrame(res).sort_values("盈虧%", ascending=False), use_container_width=True)
    else: st.info("✅ 數據已 100% 同步富途截圖。請執行掃描。")
