from PIL import Image
import io
import base64

async def convert_jfif_to_jpg(file_contents: bytes, filename: str) -> dict:
    try:
        # Create image object from bytes
        image = Image.open(io.BytesIO(file_contents))
        
        # Convert to RGB if necessary
        if image.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', image.size, (255, 255, 255))
            background.paste(image, mask=image.split()[-1])
            image = background
        
        # Save as JPEG
        output = io.BytesIO()
        image.save(output, format='JPEG', quality=95)
        output.seek(0)
        
        # Create new filename
        new_filename = filename.rsplit('.', 1)[0] + '.jpg'
        
        # Convert to base64 for response
        encoded_image = base64.b64encode(output.getvalue()).decode()
        
        return {
            "filename": new_filename,
            "content_type": "image/jpeg",
            "base64_data": encoded_image
        }
        
    except Exception as e:
        raise Exception(f"Error converting image: {str(e)}")