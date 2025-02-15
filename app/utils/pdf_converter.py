from io import BytesIO
from PIL import Image
import asyncio

async def png_to_pdf(image_bytes: bytes, original_filename: str) -> dict:
    """
    Converts PNG bytes to PDF bytes using Pillow.
    Returns dictionary with converted filename and PDF bytes.
    """
    print(f"[DEBUG] Received {len(image_bytes)} bytes for {original_filename}")
    try:
        # Run synchronous image processing in thread executor
        return await asyncio.to_thread(_sync_conversion, image_bytes, original_filename)
    except Exception as e:
        print(f"[ERROR] Conversion failed: {type(e).__name__} - {str(e)}")
        raise RuntimeError(f"Conversion failed: {str(e)}") from e

def _sync_conversion(image_bytes: bytes, original_filename: str) -> dict:
    """Synchronous conversion logic to be run in thread pool"""
    print(f"[DEBUG] Starting conversion for {original_filename}")
    
    try:
        print(f"[DEBUG] Attempting to open image (buffer size: {len(image_bytes)})")
        with Image.open(BytesIO(image_bytes)) as img:
            print(f"[DEBUG] Image opened successfully. Format: {img.format}, Mode: {img.mode}, Size: {img.size}")
            
            if img.format != 'PNG':
                print(f"[WARN] Invalid format detected: {img.format}")
                raise ValueError(f"Invalid image content - detected {img.format} instead of PNG")
            
            pdf_buffer = BytesIO()
            print("[DEBUG] Attempting PDF save...")
            img.save(pdf_buffer, format='PDF', resolution=100.0)
            pdf_bytes = pdf_buffer.getvalue()
            
            if len(pdf_bytes) == 0:
                raise RuntimeError("Generated PDF is empty")
                
            print(f"[DEBUG] PDF generated successfully ({len(pdf_bytes)} bytes)")
            
            pdf_filename = original_filename.rsplit('.', 1)[0] + '.pdf'
            return {
                'filename': pdf_filename,
                'content': pdf_bytes
            }
            
    except Exception as e:
        print(f"[ERROR] Conversion error at step: {type(e).__name__} - {str(e)}")
        raise 