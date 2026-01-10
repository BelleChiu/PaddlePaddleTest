from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
import os
import io
import numpy as np
from PIL import Image
import logging

# 設置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="PaddleOCR API", version="1.0.0")

# 延遲加載 PaddleOCR
ocr_instance = None

def get_ocr():
    global ocr_instance
    if ocr_instance is None:
        try:
            from paddleocr import PaddleOCR
            # 只使用中文和英文，減少內存使用
            ocr_instance = PaddleOCR(use_angle_cls=False, lang='ch', show_log=False)
            logger.info("PaddleOCR initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize PaddleOCR: {e}")
            raise e
    return ocr_instance

@app.get("/")
async def root():
    return {"status": "healthy", "service": "PaddleOCR API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "PaddleOCR API"}

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        # 檢查文件類型
        if not file.content_type.startswith('image/'):
            return JSONResponse(
                status_code=400,
                content={
                    "error": "Unsupported file type", 
                    "message": f"Only image files supported, got {file.content_type}",
                    "supported_types": ["image/jpeg", "image/png", "image/bmp", "image/tiff"]
                }
            )
        
        # 讀取文件
        file_bytes = await file.read()
        
        # 檢查文件大小（限制 5MB）
        if len(file_bytes) > 5 * 1024 * 1024:
            return JSONResponse(
                status_code=400,
                content={
                    "error": "File too large",
                    "message": "File size must be less than 5MB"
                }
            )
        
        # 轉換為 PIL Image
        image = Image.open(io.BytesIO(file_bytes))
        
        # 轉換為 RGB（如果是 RGBA）
        if image.mode in ['RGBA', 'LA']:
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
            image = background
        elif image.mode != 'RGB':
            image = image.convert('RGB')
        
        # 調整圖片大小（減少內存使用）
        max_size = 1024
        if max(image.size) > max_size:
            ratio = max_size / max(image.size)
            new_size = (int(image.size[0] * ratio), int(image.size[1] * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # 轉換為 numpy array
        img_array = np.array(image)
        
        # 執行 OCR
        ocr = get_ocr()
        result = ocr.ocr(img_array, cls=False)
        
        # 解析結果
        text_results = []
        full_text = []
        
        if result and result[0]:
            for line in result[0]:
                if line:
                    bbox = line[0]
                    text_info = line[1]
                    text = text_info[0]
                    confidence = text_info[1]
                    
                    text_results.append({
                        "text": text,
                        "confidence": round(confidence, 4),
                        "bbox": bbox
                    })
                    full_text.append(text)
        
        return {
            "success": True,
            "filename": file.filename,
            "content_type": file.content_type,
            "image_size": f"{image.size[0]}x{image.size[1]}",
            "total_text_blocks": len(text_results),
            "full_text": " ".join(full_text),
            "text_blocks": text_results
        }
        
    except Exception as e:
        logger.error(f"OCR processing error: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": "OCR processing failed",
                "message": str(e)
            }
        )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
