# 帳號註銷版本
一般帳號：登入後進入「使用者中心」，在頁面下方輸入目前密碼及「註銷」，按下永久註銷並確認。
若目前在履歷查閱頁，先按「返回編輯頁面」進入使用者中心。無密碼查閱者無權註銷。
批閱帳號：登入公司批閱中心，在頁面下方操作。
一般帳號會刪除基本資料、技能、證照、文件關聯、頭像、上傳文件及所有投遞快照。
批閱帳號會刪除收到的投遞快照及批閱狀態，保留申請者的帳號與原始資料。
成功後自動登出；其他已登入的工作階段不能再使用已刪除的帳號。舊版本工作階段需重新登入。
此 ZIP 保留原本 resume.db、storage 與 .env；.venv 與編譯快取未打包。
升級前關閉伺服器並備份原專案。將新 backend、frontend 覆蓋至原專案即可，保留原 .venv、resume.db、storage、.env。
全新解壓時於專案根目錄執行：
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
.venv\Scripts\python -m uvicorn backend.main:app --reload
若刪除附件時發生權限問題，資料庫變更會回滾；成功提交後若暫存附件清理失敗，介面會提示聯絡管理者。
