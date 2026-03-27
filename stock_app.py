import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import requests
import json
import base64

# --- 1. 核心映射表 (對照富途最新資料) ---
HK_NAMES = {
    "06082.HK": "壁仞科技", "03888.HK": "金山軟件", "02888.HK": "渣打集團",
    "02562.HK": "獅騰控股", "02172.HK": "微創腦科學", "02050.HK": "三花智控",
    "01810.HK": "小米集團-W", "01530.HK": "三生製藥", "00699.HK": "均勝電子"
}

# --- 2. 數據讀取邏輯 ---
def load_initial_data():
    # 這是你的保底數據，對照富途真實截圖
    default_df = pd.DataFrame({
        "代號": ["06082.HK", "03888.HK", "02888.HK", "02562.HK", "02172.HK", "02050.HK", "01810.HK", "01530.HK", "00699.HK", "GOOG", "KO", "RBLX", "TEM"],
        "成本": [38.20, 32.00, 182.00, 4.267, 13.00, 39.80, 34.75, 28.54, 19.00, 319.58, 52.98, 121.558, 77.924],
        "數量": [200, 400, 50, 3000, 1000, 300, 400, 500, 1000, 12, 1, 52, 170]
    })
    
    # 嘗試從 GitHub 讀取 (僅在配置 Secrets 後生效)
    if "GITHUB_TOKEN" in st.secrets and "REPO_NAME" in st.secrets:
        try:
            url = f"https://api.github.com/repos/{st.secrets['REPO_NAME']}/contents/portfolio.json"
            headers = {"Authorization": f"token {st.secrets['GITHUB_TOKEN']}"}
            r = requests.get(url, headers=headers, timeout=5)
            if r.status_code == 200:
                content = base64.b64decode(r.json()['content']).decode('utf-8')
                return pd.DataFrame(json.loads(content))
        except: pass
    return default_df

# --- 3. UI 設置 ---
st.set_page_config(page_title="家族辦公室", layout="wide")

if 'df' not in st.session_state:
    st.session_state.df = load_initial_data()

# 簡單安全檢查
if 'auth' not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    pwd = st.text_input("🔑 系統密鑰", type="password")
    if st.button("🔓 解鎖", use_container_width=True):
        if pwd == "13579": st.session_state.auth = True; st.rerun()
    st.stop()

t1, t2 = st.tabs(["📊 決策分析", "⚙️ 持倉管理"])

with t2:
    st.markdown("### 🛠️ 持倉數據編輯")
    # 編輯器：修改這裡的數據會暫存在瀏覽器中
    edited_df = st.data_editor(st.session_state.df, num_rows="dynamic", use_container_width=True)
    
    c1, c2 = st.columns(2)
    if c1.button("✅ 暫存更改", use_container_width=True):
        st.session_state.df = edited_df
        st.success("數據已更新至暫存區，請前往『決策分析』掃描。")
        
    if c2.button("☁️ 永久存檔 (需配置 Secrets)", use_container_width=True):
        if "GITHUB_TOKEN" in st.secrets:
            st.info("正在嘗試寫入 GitHub...")
            # 這裡放置 API 寫入代碼 (測試
