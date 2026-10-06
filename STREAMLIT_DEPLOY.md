# ResumeSystem Streamlit Cloud 部署

## 本機測試
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run app.py
```

## GitHub
將此資料夾內容推送到 GitHub repository。確認 repository 根目錄有：
- `app.py`
- `requirements.txt`
- `backend/`
- `storage/`

不要上傳 `.env` 的秘密資料。Streamlit 版不需要原 FastAPI 的 `SESSION_SECRET`。

## Streamlit Community Cloud
1. 登入 Streamlit Community Cloud。
2. Create app / New app。
3. 選擇 GitHub repository、branch。
4. Main file path 填 `app.py`。
5. Deploy。

## 重要：資料持久性
Streamlit Community Cloud 的本機檔案系統不是永久資料儲存。`resume.db` 與 `storage/uploads` 可用於展示/測試，但 app reboot、重新部署或平台重建時可能遺失執行期間新增資料。
正式公開使用時，請把 SQLite 換成外部 PostgreSQL（例如 Supabase/Neon），上傳檔案換成物件儲存（例如 Supabase Storage）。
