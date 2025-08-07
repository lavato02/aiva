import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # API Ayarları
    API_KEY = os.getenv("OPENAI_API_KEY")
    VISION_MODEL = "gpt-4-turbo"
    
    # Davranış Ayarları
    ACTION_DELAY = float(os.getenv("ACTION_DELAY", "1.0"))
    SAFE_MODE = os.getenv("SAFE_MODE", "False").lower() == "true"
    CAPTURE_INTERVAL = 10  # 10 saniye
    STOP_TIMEOUT = 3.0  # Durdurma için maksimum bekleme süresi
    
    # Görsel Ayarları
    IMAGE_DETAIL = "auto"  # "low", "high", "auto"
    SCREEN_REGION = None  # (x1,y1,x2,y2) veya None

config = Config()  # Config instance oluşturuldu