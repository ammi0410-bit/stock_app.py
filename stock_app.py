import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. 設定 ---
st.set_page_config(page_title="我的私人投資分析師", layout="wide")
st.title("📈 均線策略實戰模型")

# --- 2. 側邊欄 ---
st.sidebar.header("⚙️ 參數設定")
ticker = st.sidebar.text_input("1. 股票代號 (如: VOO, 0005.HK)", "0005.HK").upper()
short_p = st.sidebar.number_input("短期快線天數", min_value=1, max_value=100, value=20)
long_p = st.sidebar.number_input("長期慢線天數", min_value=10, max_value=500, value=60)
start_date = st.sidebar.date_input("3. 開始日期", pd.to_datetime("2024-01-01"))

run_button = st.sidebar.button("🚀 開始執行分析")

# --- 3. 邏輯執行區 ---
if run_button:
    with st.spinner('正在抓取並優化數據格式...'):
        try:
            # 抓取數據並強制清除多層標籤
            df = yf.download(ticker, start=start_date)
            
            if df.empty:
                st.error("找不到該股票數據。")
            else:
                # 【防錯重點】處理數據結構，提取收盤價
                if isinstance(df.columns, pd.MultiIndex):
                    # 如果有多層標籤，只取 'Close' 這一列
                    close_price = df['Close'][ticker]
                else:
                    close_price = df['Close']

                # 計算均線
                ma_short = close_price.rolling(window=short_p).mean()
                ma_long = close_price.rolling(window=long_p).mean()

                # 提取最後一天的數字，確保轉化為單一浮點數
                curr_val = float(close_price.iloc[-1])
                s_val = float(ma_short.iloc[-1])
                l_val = float(ma_long.iloc[-1])

                # --- 4. 顯示結果 ---
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"{ticker} 當前股價", f"${curr_val:.2f}")
                with col2:
                    if s_val > l_val:
                        st.success(f"✅ 趨勢：多頭 (快線 > 慢線)")
                    else:
                        st.error(f"⚠️ 趨勢：空頭 (快線 < 慢線)")

                # --- 5. 圖表 ---
                st.subheader(f"{ticker} 走勢與 {short_p}/{long_p} 均線圖")
                chart_df = pd.DataFrame({
                    'Price': close_price,
                    'Short MA': ma_short,
                    'Long MA': ma_long
                })
                st.line_chart(chart_df)
        
        except Exception as e:
            st.error(f"發生錯誤: {e}")
else:
    st.info("👈 請在左側輸入代號並點擊「開始執行分析」。")
