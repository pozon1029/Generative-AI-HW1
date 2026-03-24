# My Gemini 

🚀 一個基於 Google Gemini API 與 Streamlit 構建的 AI 智慧對話助理。

## 🛠️ 安裝與環境設定

1. 複製本專案與進入目錄
    ```bash
    git clone [https://github.com/你的帳號/gemini-voyager-pro.git](https://github.com/你的帳號/gemini-voyager-pro.git)
    cd gemini-voyager-pro
    ```

2. 安裝套件、設定金鑰與啟動程式
    ```bash
    pip install -r requirements.txt
    # 請將下方替換為你的實際金鑰
    export GOOGLE_API_KEY="貼上你的_GEMINI_API_金鑰"
    streamlit run mygemini.py
    ```

---

## 📂 檔案結構說明

* `mygemini.py`：專案核心程式碼。
* `requirements.txt`：所需的 Python 套件清單（如 `google-generativeai`, `streamlit`）。
* `README.md`：專案說明文件。

---

## 📝 使用備註

* **API Key**：請至 [Google AI Studio](https://aistudio.google.com/) 申請免費金鑰。
* **Windows 使用者**：若使用 Command Prompt，請將 `export` 改為 `set`。
* **安全性**：切勿將包含金鑰的指令或 `.env` 檔案上傳至公開的 GitHub 儲存庫。

---

