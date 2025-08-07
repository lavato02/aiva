from PIL import ImageGrab
from io import BytesIO
from config import Config
import logging

class ScreenCapturer:
    def __init__(self):
        self.region = Config.SCREEN_REGION

    def capture(self) -> bytes:
        try:
            screenshot = ImageGrab.grab(bbox=self.region)
            img_byte_arr = BytesIO()
            
            # Optimize edilmiş kayıt
            screenshot.save(
                img_byte_arr,
                format='PNG',
                optimize=True,
                quality=95
            )
            
            # Boyut kontrolü (20MB limiti için)
            if len(img_byte_arr.getvalue()) > 15 * 1024 * 1024:
                screenshot = screenshot.resize((screenshot.width//2, screenshot.height//2))
                img_byte_arr = BytesIO()
                screenshot.save(img_byte_arr, format='PNG', quality=85)
            
            return img_byte_arr.getvalue()
            
        except Exception as e:
            logging.error(f"Görüntü yakalama hatası: {str(e)}")
            raise