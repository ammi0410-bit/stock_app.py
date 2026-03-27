import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. 基本設定 ---
st.set_page_config(page_title="私人投資分析師", layout="wide")
st.title("📈 策略實戰與建議")

# --- 2. 側邊欄 ---
st.sidebar.header("⚙️ 參數設定")
ticker = st.sidebar.text_input("1. 股票代號", "0005.HK").upper()
short_p = st.sidebar.number_input("短期快線", 1, 100, 20)
long_p = st.sidebar.number_input("長期慢線", 10, 500, 60)
start_date = st.sidebar.date_input("3. 開始日期", pd.to_datetime("2024-01-01"))
run_button = st.sidebar.button("🚀 執行診斷")

# --- 3. 邏輯區 ---
if run_button:
    try:
        df = yf.download(ticker, start=start_date)
        if isinstance(df.columns, pd.MultiIndex):
            close_price = df['Close'][ticker]
        else:
            close_price = df['Close']

        ma_short = close_price.rolling(window=short_p).mean()
        ma_long = close_price.rolling(window=long_p).mean()

        curr_val = float(close_price.iloc[-1])
        s_val = float(ma_short.iloc[-1])
        l_val = float(ma_long.iloc[-1])

        # --- 4. 顯示基本指標 ---
        col1, col2 = st.columns(2)
        col1.metric(f"{ticker} 現價", f"${curr_val:.2f}")
        
        # --- 💡 重點：加入「建議」邏輯 ---
        st.divider()
        st.subheader("📋 投資診斷建議")
        
        advice_col1, advice_col2 = st.columns([1, 2])

        if s_val > l_val:
            advice_col1.success("🌟 趨勢：【多頭市場】")
            advice_col2.info(f"建議：快線(${s_val:.1f}) 高於慢線(${l_val:.1f})，動能向上。若已持倉可繼續持有；未持倉者可尋找股價拉回支撐點的買入機會。")
        else:
            advice_col1.error("⚠️ 趨勢：【空頭市場】")
            advice_col2.warning(f"建議：快線(${s_val:.1f}) 低於慢線(${l_val:.1f})，動能轉弱。目前不建議進場，已持倉者請注意設置止損點 (建議設在 ${curr_val*0.92:.2f})。")

        # --- 5. 圖表 ---
        st.subheader("走勢分析圖")
        chart_df = pd.DataFrame({'現價': close_price, f'{short_p}日線': ma_short, f'{long_p}日線': ma_long})
        st.line_chart(chart_df)

    except Exception as e:
        st.error(f"錯誤: {e}")
else:
    st.info("👈 請在左側輸入並按「執行診斷」")
