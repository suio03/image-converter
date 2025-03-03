import base64
import os
import tempfile
import asyncio
from PIL import Image
import pillow_heif  # Add this import

async def heic_to_pdf_binary(image_bytes: bytes, original_filename: str) -> tuple[bytes, str]:
    """Convert HEIC image to PDF and return binary data directly."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None, 
        _sync_heic_conversion_binary,
        image_bytes,
        original_filename
    )

def _sync_heic_conversion_binary(image_bytes: bytes, original_filename: str) -> tuple[bytes, str]:
    try:
        # Create a temporary file for the HEIC image
        with tempfile.NamedTemporaryFile(suffix='.heic', delete=False) as temp_heic:
            temp_heic.write(image_bytes)
            temp_heic_path = temp_heic.name
        
        # Convert HEIC to PIL Image
        heif_file = pillow_heif.read_heif(temp_heic_path)
        image = Image.frombytes(
            heif_file.mode, 
            heif_file.size, 
            heif_file.data,
            "raw", 
            heif_file.mode, 
            heif_file.stride,
        )
        
        # Create a temporary file for the PDF
        pdf_filename = os.path.splitext(original_filename)[0] + '.pdf'
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
        
        # Save the image as PDF
        image.save(temp_pdf_path, 'PDF', resolution=300.0)
        
        # Read the PDF file
        with open(temp_pdf_path, 'rb') as pdf_file:
            pdf_bytes = pdf_file.read()
        
        # Clean up temporary files
        os.unlink(temp_heic_path)
        os.unlink(temp_pdf_path)
        
        return pdf_bytes, pdf_filename
    except Exception as e:
        raise Exception(f"Failed to convert HEIC to PDF: {str(e)}")