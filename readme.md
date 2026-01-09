# PaddleOCR API Service for Zeabur

這是一個專為 n8n 集成設計的 PaddleOCR API 服務，部署在 Zeabur 平台上。

## 功能特色

- 支援中文 OCR 識別
- FastAPI 框架，RESTful API 設計
- 支援多種圖片格式（PNG, JPG, JPEG, BMP, TIFF, WebP, PDF）
- 針對 Zeabur 優化的 Docker 配置
- 健康檢查和錯誤處理

## API 端點

### 1. 健康檢查
```
GET /health
```

### 2. OCR 識別
```
POST /ocr
Content-Type: multipart/form-data

參數：
- file: 上傳的圖片文件
```

回應格式：
```json
{
  "ok": true,
  "filename": "image.png",
  "text": "識別出的完整文字",
  "lines": [
    {
      "text": "第一行文字",
      "confidence": 0.95
    }
  ],
  "total_lines": 1
}
```

## 在 n8n 中使用

### HTTP Request Node 設定：
- Method: POST
- URL: `https://your-zeabur-app.zeabur.app/ocr`
- Body Content Type: Multipart-Form Data
- Parameters:
  - Name: `file`
  - Value: `{{$binary.data}}`

## 部署到 Zeabur

1. 將所有檔案推送到 Git 倉庫
2. 在 Zeabur 中連接您的倉庫
3. Zeabur 會自動檢測 Dockerfile 並開始建構
4. 部署完成後會提供公開 URL

## 環境需求

- Python 3.10
- PaddlePaddle (CPU版本，無AVX指令集)
- PaddleOCR 2.8.1
- FastAPI 0.115.0

## 本地測試

```bash
# 建構 Docker 映像
docker build -t paddleocr-api .

# 執行容器
docker run -p 8000:8000 paddleocr-api

# 測試 API
curl -X POST -F "file=@test_image.png" http://localhost:8000/ocr
```

## 注意事項

- 服務啟動可能需要 30-60 秒，因為要下載 OCR 模型
- 建議設置至少 2GB 記憶體
- 大型圖片處理可能需要較長時間
- 支援的最大檔案大小受 Zeabur 限制
