FROM python:3.10-slim

WORKDIR /app

# 設置環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLAGS_enable_ir_optim=0
ENV PORT=8000

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# 複製需求文件
COPY requirements.txt .

# 升級 pip 並安裝 Python 依賴
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY app.py .

# 暴露端口
EXPOSE $PORT

# 啟動命令
CMD ["sh", "-c", "python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]
