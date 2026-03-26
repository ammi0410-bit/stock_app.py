import streamlit as st
import yfinance as yf
import pandas as pd

# --- 1. 網頁標題與設定 ---
st.set_page_config(page_title="我的私人投資分析師", layout="wide")
st.title("📈 均線策略實戰模型")
st.markdown("輸入股票代號並調整參數，系統會自動判斷目前趨勢。")

# --- 2. 側邊欄控制面板 (防止改錯位) ---
st.sidebar.header("⚙️ 參數設定")
ticker = st.sidebar.text_input("股票代號 (如: VOO, AAPL, 0700.HK)", "VOO").upper()
start_date = st.sidebar.date_input("開始日期", pd.to_datetime("2024-01-01"))

st.sidebar.subheader("均線週期")
short_p = st.sidebar.slider("短期快線 (天)", 5, 50, 20)
long_p = st.sidebar.slider("長期慢線 (天)", 20, 250, 60)

# --- 3. 抓取與計算數據 ---
@st.cache_data
def get_data(t, s):
    df = yf.download(t, start=s)
    return df

try:
    df = get_data(ticker, start_date)
    
    # 計算均線
    df['Short_MA'] = df['Close'].rolling(window=short_p).mean()
    df['Long_MA'] = df['Close'].rolling(window=long_p).mean()

    # --- 4. 顯示診斷結果 ---
    col1, col2 = st.columns(2)
    current_price = df['Close'].iloc[-1]
    last_short = df['Short_MA'].iloc[-1]
    last_long = df['Long_MA'].iloc[-1]

    with col1:
        st.metric("當前股價", f"${current_price:.2f}")
    
    with col2:
        if last_short > last_long:
            st.success(f"✅ 趨勢：多頭 (快線 {last_short:.1f} > 慢線 {last_long:.1f})")
        else:
            st.error(f"⚠️ 趨勢：空頭 (快線 {last_short:.1f} < 慢線 {last_long:.1f})")

    # --- 5. 繪製圖表 ---
    st.subheader("價格與均線走勢圖")
    st.line_chart(df[['Close', 'Short_MA', 'Long_MA']])

except Exception as e:
    st.warning("請輸入正確的股票代號（例如美股用 VOO，港股用 0700.HK）")
