# 1. 選擇基底：就像選一塊乾淨的地基，我們選用官方的 Python 3.11 輕量版 (slim)
FROM python:3.11-slim

# 2. 設定工作目錄：在貨櫃裡建立一個叫 /app 的資料夾，並走進去
WORKDIR /app

# 3. 複製清單：先把你的 requirements.txt 複製到貨櫃裡
COPY requirements.txt .

# 4. 安裝套件：請 Docker 裡的終端機，幫你把 FastAPI, MySQL 等套件裝好
RUN pip install --no-cache-dir -r requirements.txt

# 5. 搬運程式碼：把我們資料夾裡的所有東西 (包含 main.py, static, .env 等) 全部搬進貨櫃
COPY . .

# 6. 開通對外窗戶：告訴 Docker 我們的伺服器跑在 8000 port
EXPOSE 8000

# 7. 啟動指令：當貨櫃啟動時，自動執行這行指令 (注意 --host 0.0.0.0 是讓外部可以連進來的關鍵)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]