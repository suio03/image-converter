from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from utils.converter import convert_jfif_to_jpg
import os

app = FastAPI(title="JFIF to JPG Converter")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"message": "JFIF to JPG Converter API"}

@app.post("/convert")
async def convert_image(file: UploadFile = File(...)):
    try:
        # Validate file size
        MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", 10 * 1024 * 1024))  # Default 10MB
        file_size = 0
        contents = bytearray()
        
        # Read file in chunks to handle large files
        while chunk := await file.read(8192):
            file_size += len(chunk)
            if file_size > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="File too large"
                )
            contents.extend(chunk)

        # Validate file type
        if not file.filename.lower().endswith(('.jfif', '.jpg', '.jpeg')):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only JFIF files are supported."
            )

        # Convert the image
        result = await convert_jfif_to_jpg(contents, file.filename)
        
        return JSONResponse(
            content={
                "success": True,
                "message": "File converted successfully",
                "data": result
            },
            status_code=200
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred: {str(e)}"
        )