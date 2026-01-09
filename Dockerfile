FROM python:3.10-slim

# 設置工作目錄
WORKDIR /app

# 設置環境變數
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV FLAGS_enable_ir_optim=0
ENV PORT=8000

# 安裝系統依賴
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgcc-s1 \
    ca-certificates \
    curl \
    wget \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# 複製需求文件
COPY requirements.txt .

# 安裝 PaddlePaddle (CPU 版本，無 AVX)
RUN set -eux; \
    HTML_URL="https://www.paddlepaddle.org.cn/whl/linux/cpu/noavx/stable.html"; \
    echo "Fetching PaddlePaddle wheel URL..."; \
    WHEEL_URL="$(curl -fsSL "$HTML_URL" \
      | grep -oE 'https?://[^"]+paddlepaddle-[0-9.]+-cp310-cp310-[^"]+\.whl' \
      | head -n 1)"; \
    echo "Selected wheel: $WHEEL_URL"; \
    if [ -z "$WHEEL_URL" ]; then \
        echo "Error: No suitable PaddlePaddle wheel found"; \
        exit 1; \
    fi; \
    pip install --no-cache-dir --no-deps "$WHEEL_URL"

# 安裝其他 Python 依賴
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 複製應用程式碼
COPY app.py .

# 建立非 root 用戶
RUN groupadd -r appuser && useradd -r -g appuser appuser \
    && chown -R appuser:appuser /app
USER appuser

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:${PORT}/health || exit 1

# 暴露端口
EXPOSE $PORT

# 啟動命令
CMD ["sh", "-c", "python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000} --workers 1"]