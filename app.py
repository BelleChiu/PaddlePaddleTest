from fastapi import FastAPI, UploadFile, File, HTTPException
from paddleocr import PaddleOCR
import tempfile
import os
import logging
from pathlib import Path

# 設置日誌
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PaddleOCR API", description="OCR Service for n8n integration")

# 初始化 PaddleOCR
try:
    logger.info("Initializing PaddleOCR...")
    ocr = PaddleOCR(use_angle_cls=True, lang="ch", ir_optim=False, show_log=False)
    logger.info("PaddleOCR initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize PaddleOCR: {e}")
    ocr = None

@app.get("/")
async def root():
    return {"message": "PaddleOCR API is running", "status": "ok"}

@app.get("/health")
async def health_check():
    if ocr is None:
        raise HTTPException(status_code=503, detail="OCR service not available")
    return {"status": "healthy", "service": "PaddleOCR API"}

@app.post("/ocr")
async def ocr_file(file: UploadFile = File(...)):
    if ocr is None:
        raise HTTPException(status_code=503, detail="OCR service not initialized")
    
    # 驗證檔案類型
    allowed_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.tiff', '.webp', '.pdf'}
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_extension}")
    
    # 建立臨時檔案
    suffix = file_extension or ".png"
    temp_file_path = None
    
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            temp_file_path = tmp.name
        
        logger.info(f"Processing file: {file.filename}, size: {len(content)} bytes")
        
        # 執行 OCR
        result = ocr.ocr(temp_file_path, cls=True)
        
        if not result or not result[0]:
            return {
                "ok": True,
                "filename": file.filename,
                "text": "",
                "lines": [],
                "message": "No text detected"
            }
        
        # 處理結果
        lines = []
        full_text = []
        
        for page in result:
            if page:  # 確保頁面不為空
                for item in page:
                    if item and len(item) >= 2:  # 確保項目格式正確
                        text = item[1][0]
                        confidence = float(item[1][1])
                        lines.append({
                            "text": text,
                            "confidence": confidence
                        })
                        full_text.append(text)
        
        return {
            "ok": True,
            "filename": file.filename,
            "text": "\n".join(full_text),
            "lines": lines,
            "total_lines": len(lines)
        }
        
    except Exception as e:
        logger.error(f"OCR processing error: {e}")
        raise HTTPException(status_code=500, detail=f"OCR processing failed: {str(e)}")
    
    finally:
        # 清理臨時檔案
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to remove temp file: {e}")

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)