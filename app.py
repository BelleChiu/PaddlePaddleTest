from fastapi import FastAPI, File, UploadFile, HTTPException
import uvicorn
import os

app = FastAPI()

@app.get("/")
async def root():
    return {"status": "healthy", "service": "PaddleOCR API"}

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "PaddleOCR API"}

@app.post("/ocr")
async def ocr_endpoint(file: UploadFile = File(...)):
    try:
        # 簡化：先返回文件信息，不做實際 OCR
        return {
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(await file.read()),
            "status": "received",
            "message": "File processing temporarily disabled due to memory constraints"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)
