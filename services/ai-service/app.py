"""Week 3 contract adapter. Does not load or simulate an actual trained model."""
import io
import os
import warnings

from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from PIL import Image, UnidentifiedImageError

load_dotenv()
app = FastAPI(title="AI Fundus mock service", version="0.3.0")
MAX_BYTES = int(os.getenv("MAX_UPLOAD_BYTES", "10485760"))
Image.MAX_IMAGE_PIXELS = 40000000


@app.get("/health")
def health():
    return {"status": "healthy", "service": "ai", "modelLoaded": False,
            "modelVersion": "mock-v0", "isMock": True}


@app.post("/predict")
async def predict(image: UploadFile = File(...)):
    try:
        content = await image.read(MAX_BYTES + 1)
    finally:
        await image.close()
    if len(content) > MAX_BYTES:
        return JSONResponse(status_code=413, content={"success": False, "error": {"code": "UPLOAD_TOO_LARGE"}})
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(content)) as decoded:
                if decoded.format not in ("PNG", "JPEG") or image.content_type != Image.MIME[decoded.format] or getattr(decoded, "n_frames", 1) != 1:
                    raise ValueError("Unsupported image")
                decoded.verify()
            with Image.open(io.BytesIO(content)) as decoded:
                decoded.load()
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError, Image.DecompressionBombWarning):
        return JSONResponse(status_code=400, content={"success": False, "error": {"code": "INVALID_IMAGE"}})
    return {"success": True, "isMock": True,
            "prediction": {"class": "Moderate", "confidence": 0.81},
            "probabilities": {"No_DR": 0.02, "Mild": 0.07, "Moderate": 0.81, "Severe": 0.08, "Proliferative_DR": 0.02},
            "riskLevel": "MEDIUM", "modelVersion": "mock-v0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("AI_SERVICE_HOST", "127.0.0.1"), port=int(os.getenv("AI_SERVICE_PORT", "8000")))
