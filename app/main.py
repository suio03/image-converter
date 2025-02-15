from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from utils.converter import convert_jfif_to_jpg
import os
from fastapi import Depends
from utils.pdf_converter import png_to_pdf
app = FastAPI(title="JFIF to JPG Converter", root_path="/api")


# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://png2pdf.net", "http://localhost:3000", "https://png2pdf.net"],  # Replace with your frontend URL in production
    # allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
async def verify_api_key(x_api_key: Optional[str] = Header(None, alias="X-API-Key")):
    if not x_api_key or x_api_key != os.getenv("API_KEY"):
        raise HTTPException(status_code=403, detail="Invalid API key")
    return x_api_key

@app.get("/")
async def read_root():
    return {"message": "JFIF to JPG Converter API"}

@app.post("/convert")
async def convert_image(
    file: UploadFile = File(...),
    x_api_key: str = Depends(verify_api_key)
):
    try:
        contents = bytearray()
        
        # Read file in chunks to handle large files
        while chunk := await file.read(8192):
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

@app.post("/convert-png-to-pdf")
async def convert_png_to_pdf(
    file: UploadFile = File(...),
    x_api_key: str = Depends(verify_api_key)
):
    try:
        contents = bytearray()
        
        chunk_count = 0
        while chunk := await file.read(8192):
            chunk_count += 1
            contents.extend(chunk)

        if len(contents) == 0:
            raise HTTPException(400, "Empty file received")
            
        input_bytes = bytes(contents)

        if not file.filename.lower().endswith('.png'):
            raise HTTPException(
                status_code=400,
                detail="Unsupported file format. Only PNG files are supported."
            )

        result = await png_to_pdf(input_bytes, file.filename)
        
        if not result.get('content'):
            raise HTTPException(500, "PDF generation returned empty content")
            
        
        # Return PDF directly with proper headers
        return Response(
            content=result['content'],
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={result['filename']}"
            }
        )

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(500, detail=f"Internal error: {str(e)}")