import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# --- 1. 頁面配置 ---
st.set_page_config(page_title="專業資產共識決策系統", layout="wide")

# --- 2. 安全登入 ---
st.sidebar.header("🔐 安全認證")
password_input = st.sidebar.text_input("輸入解鎖密碼", type="password")
if password_input != "13579":
    st.info("請輸入正確密碼以獲取市場分析師綜合建議。")
    st.stop()

# --- 🔓 登入成功 ---
st.title("📊 市場共識綜合分析與戰略部署")

# --- 3. 持倉數據 (已根據截圖預設) ---
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = [
        {"代號": "06082.HK", "成本": 38.20, "數量": 200.0},
        {"代號": "03888.HK", "成本": 32.00, "數量": 400.0},
        {"代號": "02888.HK", "成本": 182.00, "數量": 50.0},
        {"代號": "02562.HK", "成本": 4.267, "數量": 3000.0},
        {"代號": "02172.HK", "成本": 13.00, "數量": 1000.0},
        {"代號": "02050.HK", "成本": 39.80, "數量": 300.0},
        {"代號": "01810.HK", "成本": 34.75, "數量": 400.0},
        {"代號": "01530.HK", "成本": 28.54, "數量": 500.0},
        {"代號": "00699.HK", "成本": 19.00, "數量": 1000.0},
        {"代號": "GOOG", "成本": 319.58, "數量": 12.0},
        {"代號": "KO", "成本": 52.98, "數量": 1.0},
        {"代號": "RBLX", "成本": 121.558, "數量": 52.0},
        {"代號": "TEM", "成本": 77.924, "數量": 170.0}
    ]

edited_df = st.data_editor(pd.DataFrame(st.session_state.portfolio), num_rows="dynamic", use_container_width=True)

# --- 4. 執行深度分析 ---
if st.button("🚀 獲取全球分析師綜合建議"):
    st.divider()
    summary = []
    
    for _, row in edited_df.iterrows():
        t = str(row["代號"]).upper().strip()
        cost = float(row["成本"])
        try:
            ticker_obj = yf.Ticker(t)
            info = ticker_obj.info
            hist = ticker_obj.history(period="1y")
            
            if hist.empty: continue
            
            curr_p = float(hist['Close'].iloc[-1])
            
            # --- 抓取市場共識數據 ---
            # 獲取平均目標價 (Target Mean Price)
            target_mean = info.get('targetMeanPrice', curr_p * 1.1) 
            target_high = info.get('targetHighPrice', target_mean * 1.1)
            target_low = info.get('targetLowPrice', curr_p * 0.9)
            analyst_count = info.get('numberOfAnalystOpinions', 'N/A')
            rec_key = info.get('recommendationKey', 'none').upper()
            
            # --- 綜合止盈止蝕邏輯 (非百分比) ---
            # 止盈：參考分析師平均目標價
            # 止蝕：參考分析師最低預期或 200 天均線 (長線支撐)
            ma200 = hist['Close'].rolling(200).mean().iloc[-1] if len(hist) > 200 else curr_p * 0.85
            final_stop = min(target_low, ma200) if target_low > 0 else ma200
            
            pnl_pct = (curr_p - cost) / cost * 100
            
            summary.append({
                "資產": t,
                "現價": round(curr_p, 2),
                "分析師人數": analyst_count,
                "市場評級": rec_key,
                "平均目標價 (止盈)": round(target_mean, 2),
                "共識底線 (止蝕)": round(final_stop, 2),
                "目前狀態": "✅ 優於成本" if curr_p > cost else "❌ 低於成本"
            })

            # --- 繪製戰略部署圖 ---
            with st.expander(f"📊 {t} - 市場共識分析 (共 {analyst_count} 位分析師)", expanded=(pnl_pct < -15)):
                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], name="股價走勢", line=dict(color='white')))
                
                # 標註市場關鍵位
                fig.add_hline(y=target_mean, line_dash="dash", line_color="lime", annotation_text="市場平均目標 (止盈)")
                fig.add_hline(y=final_stop, line_dash="dot", line_color="orange", annotation_text="共識支撐位 (止蝕)")
                fig.add_hline(y=cost, line_dash="solid", line_color="yellow", annotation_text="你的入貨成本")
                
                fig.update_layout(title=f"{t} 分析師目標位佈局", template="plotly_dark", height=400)
                st.plotly_chart(fig, use_container_width=True)
                
                if analyst_count != 'N/A':
                    st.info(f"💡 該建議綜合了全球 {analyst_count} 位分析師的數據。目前市場整體評價為：**{rec_key}**。")

        except Exception as e:
            st.error(f"無法
