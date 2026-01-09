FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    libgomp1 \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# 1) 從 noavx stable.html 抓出「符合 cp310 的 wheel 連結」
# 2) 直接用該 wheel URL 安裝 paddlepaddle（不走 PyPI）
RUN set -eux; \
    HTML_URL="https://www.paddlepaddle.org.cn/whl/linux/cpu/noavx/stable.html"; \
    WHEEL_URL="$(curl -fsSL "$HTML_URL" \
      | grep -oE 'https?://[^"]+paddlepaddle-[0-9.]+-cp310-cp310-[^"]+\.whl' \
      | head -n 1)"; \
    echo "Selected wheel: $WHEEL_URL"; \
    test -n "$WHEEL_URL"; \
    pip install --no-cache-dir --no-deps "$WHEEL_URL"

# 安裝其餘套件（paddleocr / fastapi / uvicorn 等）
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# 保險：關掉 IR optimizer（避免 SelfAttentionFusePass SIGILL）
ENV FLAGS_enable_ir_optim=0
ENV PORT=8000

CMD ["sh", "-c", "python -m uvicorn app:app --host 0.0.0.0 --port ${PORT:-8000}"]
