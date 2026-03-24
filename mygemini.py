import streamlit as st
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# --- 1. 環境設定 ---
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")
if api_key:
    genai.configure(api_key=api_key)
else:
    st.error("未偵測到 API Key")
    st.stop()

st.set_page_config(page_title="My Gemini", page_icon="✨", layout="wide")

st.markdown("""
    <style>
    .stChatInputContainer { padding-bottom: 20px; }
    [data-testid="stSidebar"] { background-color: #1e1e1e; }
    .error-box { 
        padding: 10px; border-radius: 5px; background-color: #4a1515; 
        color: #ffbaba; border: 1px solid #ff5f5f; margin: 5px 0;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 初始化 Session State (多對話管理系統) ---
if "all_chats" not in st.session_state:
    st.session_state.all_chats = {"預設資料夾": {"新對話": []}}

if "current_folder" not in st.session_state:
    st.session_state.current_folder = "預設資料夾"

if "current_topic" not in st.session_state:
    st.session_state.current_topic = "新對話"

if "temp_attachments" not in st.session_state:
    st.session_state.temp_attachments = []

if "total_tokens" not in st.session_state:
    st.session_state.total_tokens = 0
if "last_run_tokens" not in st.session_state:
    st.session_state.last_run_tokens = 0

# --- 3. 側邊欄：用戶管理系統 ---
with st.sidebar:
    st.title("🚀 My OS")
    
    # --- A. 新增對話按鈕 ---
    if st.button("📝 + 新的對話", use_container_width=True):
        new_name = f"新對話_{len(st.session_state.all_chats[st.session_state.current_folder]) + 1}"
        st.session_state.all_chats[st.session_state.current_folder][new_name] = []
        st.session_state.current_topic = new_name
        st.rerun()

    st.divider()
    ### st.divider()
    st.subheader("📊 消耗統計")
    col_a, col_b = st.columns(2)
    col_a.metric("本次 Token", st.session_state.last_run_tokens)
    col_b.metric("累計 Token", st.session_state.total_tokens)
 
    # 假設 1M Tokens = 0.1 USD
    total_cost = (st.session_state.total_tokens / 1000000) * 0.1
    st.caption(f"預計累計成本: ${total_cost:.6f} USD")

    # --- B. 資料夾管理 (CRUD + 重新命名) ---
    st.subheader("📂 資料夾管理")
    
    with st.popover("➕ 新增資料夾"):
        new_folder_name = st.text_input("輸入名稱")
        if st.button("確認建立"):
            if new_folder_name and new_folder_name not in st.session_state.all_chats:
                st.session_state.all_chats[new_folder_name] = {"新對話": []}
                st.rerun()

    for folder_name, topics in list(st.session_state.all_chats.items()):
        with st.expander(f"📁 {folder_name}", expanded=(folder_name == st.session_state.current_folder)):
            c1, c2 = st.columns([4, 1])
            if c2.button("🗑️", key=f"del_fol_{folder_name}"):
                del st.session_state.all_chats[folder_name]
                st.rerun()
            
            for topic_name in list(topics.keys()):
                sub_c1, sub_c2, sub_c3 = st.columns([6, 1, 1])
                is_active = (topic_name == st.session_state.current_topic and folder_name == st.session_state.current_folder)
                btn_label = f"💬 {topic_name}" if not is_active else f"🔹 {topic_name}"
                
                if sub_c1.button(btn_label, key=f"btn_{folder_name}_{topic_name}", use_container_width=True):
                    st.session_state.current_folder = folder_name
                    st.session_state.current_topic = topic_name
                    st.rerun()
                
                with sub_c2.popover("✏️"):
                    new_topic_title = st.text_input("修改名稱", value=topic_name, key=f"rename_{folder_name}_{topic_name}")
                    if st.button("儲存", key=f"save_{folder_name}_{topic_name}"):
                        st.session_state.all_chats[folder_name][new_topic_title] = st.session_state.all_chats[folder_name].pop(topic_name)
                        if is_active: st.session_state.current_topic = new_topic_title
                        st.rerun()

                if sub_c3.button("×", key=f"del_top_{folder_name}_{topic_name}"):
                    del st.session_state.all_chats[folder_name][topic_name]
                    st.rerun()

    st.divider()

    # --- C. AI 控制中心 (模型特色說明) ---
    st.subheader("🤖 AI 控制中心")
    
    model_info = {
        "🚀 Gemini 3 Flash Preview (最強推理與創意)": "gemini-3-flash-preview",
        "🚀 Gemini 2.5 Flash (平衡旗艦：圖片理解強)": "gemini-2.5-flash",
        "🚀 Gemini 1.5 Flash (最穩定)": "gemini-flash-latest",
        "⚡ Gemini 3.1 Flash Lite (極速響應：最新架構)": "gemini-3.1-flash-lite-preview",
        "⚡ Gemini 2.5 Flash Lite (效率平衡：簡單對話)": "gemini-2.5-flash-lite"
    }
    selected_model_label = st.selectbox("選擇模型", options=list(model_info.keys()))
    final_model = model_info[selected_model_label]

    with st.expander("🛠️ 進階參數"):
        system_prompt = st.text_area("System Prompt", value="你是一個專業助理，請用繁體中文回答。", height=80)
        temp = st.slider("Temperature", 0.0, 2.0, 1.0, 0.1)
        top_p = st.slider("Top P", 0.0, 1.0, 0.95, 0.05)
        max_tokens = st.number_input("Max Tokens", 100, 8192, 2048)
        use_streaming = st.toggle("開啟串流", value=True)

    # 備份功能
    history_json = json.dumps(st.session_state.all_chats, indent=2, ensure_ascii=False)
    st.download_button("📥 備份 JSON", data=history_json, file_name="voyager_backup.json", use_container_width=True)

# --- 4. 主介面：顯示區 ---
current_messages = st.session_state.all_chats[st.session_state.current_folder][st.session_state.current_topic]

st.title(f"✨ {st.session_state.current_topic}")
st.caption(f"📂 路徑：{st.session_state.current_folder} / 模型：`{final_model}`")

# 渲染對話 (含錯誤紀錄)
for message in current_messages:
    if message["role"] == "error":
        st.markdown(f'<div class="error-box">⚠️ 系統錯誤：{message["content"]}</div>', unsafe_allow_html=True)
    else:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# --- 5. 底部輸入區 (官網樣式附件按鈕) ---
st.write("---")
col_up, col_input = st.columns([0.08, 0.92])

with col_up:
    with st.popover("➕", help="附件"):
        new_files = st.file_uploader("檔案", accept_multiple_files=True, type=['png', 'jpg', 'pdf', 'txt'], label_visibility="collapsed")
        if new_files:
            st.session_state.temp_attachments = [{"name": f.name, "type": f.type, "data": f.read()} for f in new_files]
            st.toast(f"已夾帶 {len(new_files)} 個檔案")

if st.session_state.temp_attachments:
    st.caption(f"📎 準備送出：{', '.join([f['name'] for f in st.session_state.temp_attachments])}")

# --- 6. 核心對話邏輯 ---
if prompt := st.chat_input("問問 Gemini Assistant..."):
    # 存入 User 訊息
    current_messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 準備發送內容 (文字 + 附件)
    user_content = [prompt]
    for f in st.session_state.temp_attachments:
        user_content.append({"mime_type": f['type'], "data": f['data']})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        full_res = ""
        try:
            # 初始化模型 (已移除 google_search)
            model = genai.GenerativeModel(
                model_name=final_model, 
                system_instruction=system_prompt
            )
            
            # 過濾 Error 紀錄後的對話歷史
            history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} 
                       for m in current_messages[:-1] if m["role"] != "error"]
            
            chat = model.start_chat(history=history)
            
            # API 請求與串流
            response = chat.send_message(user_content, stream=use_streaming)
            
            if use_streaming:
                for chunk in response:
                    if chunk.text:
                        full_res += chunk.text
                        placeholder.markdown(full_res + "▌")
                placeholder.markdown(full_res)
                try:
                    usage = response.usage_metadata
                    st.session_state.last_run_tokens = usage.total_token_count
                    st.session_state.total_tokens += usage.total_token_count
                except:
                    pass # 預防某些模型沒回傳 metadata
            else:
                with st.spinner("思考中..."):
                    full_res = response.text
                    placeholder.markdown(full_res)
                if hasattr(response, 'usage_metadata'):
                    usage = response.usage_metadata
                    st.session_state.last_run_tokens = usage.total_token_count
                    st.session_state.total_tokens += usage.total_token_count
            
            # 存入 Assistant 回覆
            current_messages.append({"role": "assistant", "content": full_res})
            # 清空附件並刷新 UI
            st.session_state.temp_attachments = []
            st.rerun()

        except Exception as e:
            # 發生錯誤時：保留對話紀錄，將錯誤訊息存入該話題
            error_msg = str(e)
            current_messages.append({"role": "error", "content": error_msg})
            st.markdown(f'<div class="error-box">⚠️ 發生錯誤：{error_msg}</div>', unsafe_allow_html=True)
            st.session_state.temp_attachments = []
