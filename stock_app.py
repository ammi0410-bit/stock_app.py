import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. 設定 ---
st.set_page_config(page_title="我的私人投資分析師", layout="wide")
st.title("📈 均線策略實戰模型")

# --- 2. 側邊欄控制面板 ---
st.sidebar.header("⚙️ 參數設定")
ticker = st.sidebar.text_input("1. 股票代號 (如: VOO, 0005.HK)", "0005.HK").upper()

st.sidebar.subheader("2. 均線天數")
short_p = st.sidebar.number_input("短期快線天數", min_value=1, max_value=100, value=20)
long_p = st.sidebar.number_input("長期慢線天數", min_value=10, max_value=500, value=60)

start_date = st.sidebar.date_input("3. 開始日期", pd.to_datetime("2024-01-01"))

run_button = st.sidebar.button("🚀 開始執行分析")

# --- 3. 邏輯執行區 ---
if run_button:
    with st.spinner('正在抓取數據...'):
        try:
            # 抓取數據
            df = yf.download(ticker, start=start_date)
            
            if df.empty:
                st.error("找不到該股票數據，請檢查代號是否正確。")
            else:
                # 【核心修正】確保取到的是單一數值而非整個序列
                close_price = df['Close']
                
                # 計算均線
                df['Short_MA'] = close_price.rolling(window=short_p).mean()
                df['Long_MA'] = close_price.rolling(window=long_p).mean()

                # 取最後一天的數據，並轉為浮點數 (float) 避免 format 錯誤
                current_price = float(close_price.iloc[-1])
                last_short = float(df['Short_MA'].iloc[-1])
                last_long = float(df['Long_MA'].iloc[-1])

                # --- 4. 顯示結果 ---
                col1, col2 = st.columns(2)
                with col1:
                    st.metric(f"{ticker} 當前股價", f"${current_price:.2f}")
                with col2:
                    if last_short > last_long:
                        st.success(f"✅ 趨勢：多頭 (快線 > 慢線)")
                    else:
                        st.error(f"⚠️ 趨勢：空頭 (快線 < 慢線)")

                # --- 5. 圖表 ---
                st.subheader(f"{ticker} 走勢與 {short_p}/{long_p} 均線圖")
                # 重新整合繪圖數據，確保欄位清晰
                plot_data = pd.DataFrame({
                    'Price': close_price.squeeze(),
                    'Short MA': df['Short_MA'].squeeze(),
                    'Long MA': df['Long_MA'].squeeze()
                })
                st.line_chart(plot_data)
        
        except Exception as e:
            st.error(f"發生錯誤: {e}")
else:
    st.info("👈 請在左側輸入代號並點擊「開始執行分析」。")
